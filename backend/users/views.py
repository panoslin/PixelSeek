"""
User account management views and authentication flows.

This module handles user authentication, registration, profile management,
and OAuth integrations with providers like Google and WeChat.
"""
import base64
import json
import logging
import traceback
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.http import HttpResponseRedirect
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import UserSerializer, UserProfileSerializer

logger = logging.getLogger(__name__)

# =============================================================================
# Core API Views
# =============================================================================


class UserViewSet(viewsets.ModelViewSet):
    """Admin-only viewset for managing all users."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class CurrentUserView(APIView):
    """View for retrieving the current authenticated user's profile."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Return serialized data for the current user."""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)


# =============================================================================
# Authentication Helper Functions
# =============================================================================

def generate_tokens_for_user(user):
    """Generate JWT tokens for a user.
    
    Args:
        user: User object to generate tokens for
        
    Returns:
        dict: Contains refresh and access tokens
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def set_auth_cookie(response, token):
    """Set JWT token as an HTTP-only cookie.
    
    Args:
        response: HttpResponse to set cookie on
        token: JWT token string
        
    Returns:
        HttpResponse: Response with cookie set
    """
    max_age = 3600 * 24 * 7  # 7 days
    response.set_cookie(
        'accessToken',
        token,
        max_age=max_age,
        httponly=True,
        samesite='Lax'
    )
    return response


def redirect_with_tokens(tokens, error=None, return_to_api=False):
    """Redirect to appropriate location with tokens or error message.
    
    Args:
        tokens: JWT tokens dict or None if error
        error: Optional error message
        return_to_api: Whether to return to the API browsable interface
        
    Returns:
        HttpResponseRedirect: Redirect response with appropriate params/cookies
    """
    # API browsable interface redirect
    if return_to_api:
        response = HttpResponseRedirect('/api/?format=api')
        if tokens and not error:
            response = set_auth_cookie(response, tokens['access'])
        return response

    # Frontend application redirect
    frontend_url = settings.CORS_ALLOWED_ORIGINS[0]
    
    if error:
        redirect_url = f"{frontend_url}/auth/callback?error={error}"
    else:
        redirect_url = f"{frontend_url}/auth/callback?tokens={json.dumps(tokens)}"
    
    return HttpResponseRedirect(redirect_url)


def is_api_request(request):
    """Check if request originated from API browsable interface.
    
    Args:
        request: Django request object
        
    Returns:
        bool: True if request came from API interface
    """
    referer = request.META.get('HTTP_REFERER', '')
    return 'api' in referer


def handle_oauth_error(error_msg, return_to_api=False, log_msg=None):
    """Handle OAuth error with proper logging and redirect.
    
    Args:
        error_msg: User-facing error message
        return_to_api: Whether to return to API interface
        log_msg: Optional different message for server logs
        
    Returns:
        HttpResponseRedirect: Redirect with error
    """
    if log_msg:
        logger.error(log_msg)
    else:
        logger.error(error_msg)
        
    return redirect_with_tokens(None, error=error_msg, return_to_api=return_to_api)


# =============================================================================
# Google OAuth Implementation
# =============================================================================

def google_login(request):
    """Initiate Google OAuth authentication flow.
    
    Redirects the user to Google's authentication page with appropriate params.
    """
    redirect_uri = settings.GOOGLE_OAUTH_REDIRECT_URI
    client_id = settings.GOOGLE_OAUTH_CLIENT_ID
    
    # Determine if request is from the API browsable interface
    state = 'api' if is_api_request(request) else 'frontend'
    
    # Build OAuth URL with necessary parameters
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid email profile',
        'state': state,
    }
    
    auth_url = f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"
    return HttpResponseRedirect(auth_url)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def google_callback(request):
    """Handle Google OAuth callback and authenticate/register user.
    
    Creates or updates the user account based on Google profile data.
    """
    code = request.GET.get('code')
    state = request.GET.get('state', '')
    return_to_api = state == 'api'
    
    if not code:
        return handle_oauth_error(
            "Authorization code not provided", 
            return_to_api=return_to_api,
            log_msg="Google OAuth callback received without authorization code"
        )

    # Exchange code for tokens
    try:
        # Request access and ID tokens from Google
        token_data = exchange_google_code_for_token(code)
        
        # Extract and decode the ID token to get user profile data
        user_data = decode_google_id_token(token_data.get('id_token'))
        if not user_data:
            return handle_oauth_error(
                "Failed to process authentication token", 
                return_to_api=return_to_api
            )
        
        # Get essential user information 
        email = user_data.get('email')
        if not email:
            return handle_oauth_error(
                "Email not found in user profile", 
                return_to_api=return_to_api,
                log_msg="Email not found in Google token payload"
            )
        
        # Find or create the user account
        try:
            user = find_or_create_google_user(email, user_data)
            
            # Generate JWT tokens for our application
            tokens = generate_tokens_for_user(user)
            return redirect_with_tokens(tokens, return_to_api=return_to_api)
            
        except Exception as e:
            logger.error(f"Error creating/updating user from Google OAuth: {str(e)}\n{traceback.format_exc()}")
            return handle_oauth_error(
                "Failed to create or update user account", 
                return_to_api=return_to_api
            )
            
    except requests.RequestException as e:
        logger.error(f"Google OAuth token exchange error: {str(e)}")
        return handle_oauth_error(
            "Failed to communicate with authentication server", 
            return_to_api=return_to_api
        )
    except Exception as e:
        logger.error(f"Unexpected error in Google OAuth callback: {str(e)}\n{traceback.format_exc()}")
        return handle_oauth_error("Authentication failed", return_to_api=return_to_api)


def exchange_google_code_for_token(code):
    """Exchange authorization code for Google tokens.
    
    Args:
        code: Authorization code from Google
        
    Returns:
        dict: Token data from Google
        
    Raises:
        requests.RequestException: If API call fails
    """
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        'code': code,
        'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
        'client_secret': settings.GOOGLE_OAUTH_SECRET,
        'redirect_uri': settings.GOOGLE_OAUTH_REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    
    response = requests.post(token_url, data=payload)
    response.raise_for_status()
    return response.json()


def decode_google_id_token(id_token):
    """Decode the Google ID token to extract user data.
    
    Args:
        id_token: JWT token from Google
        
    Returns:
        dict: Decoded user data or None if decode fails
    """
    if not id_token:
        logger.error("Failed to obtain id_token from Google")
        return None
        
    try:
        # Split the token into parts
        header, payload_part, signature = id_token.split('.')
        
        # Add padding if needed
        payload_part += '=' * ((4 - len(payload_part) % 4) % 4)
        
        # Decode using base64
        decoded_bytes = base64.urlsafe_b64decode(payload_part)
        decoded_string = decoded_bytes.decode('utf-8')
        return json.loads(decoded_string)
        
    except Exception as e:
        logger.error(f"Error decoding Google id_token: {str(e)}\n{traceback.format_exc()}")
        return None


def find_or_create_google_user(email, user_data):
    """Find existing user or create new user from Google profile.
    
    Args:
        email: User's email from Google
        user_data: Dict containing Google profile data
        
    Returns:
        User: MongoDB user object
        
    Raises:
        Exception: If user creation/update fails
    """
    # Try to find the user first
    user = User.objects(email=email).first()
    
    if not user:
        # User doesn't exist, create one
        user = User(
            email=email,
            username=email.split('@')[0],
            auth_provider='google',
            auth_provider_id=user_data.get('sub'),
            full_name=user_data.get('name', ''),
            is_verified=user_data.get('email_verified', False)
        )
        user.save()
        logger.info(f"Created new user via Google OAuth: {email}")
    else:
        # Update existing user with latest data
        user.auth_provider = 'google'
        user.auth_provider_id = user_data.get('sub')
        user.full_name = user_data.get('name', user.full_name)
        user.is_verified = user_data.get('email_verified', user.is_verified)
        user.save()
        logger.info(f"Updated existing user via Google OAuth: {email}")
        
    return user


# =============================================================================
# WeChat OAuth Implementation
# =============================================================================

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def wechat_login(request):
    """Initiate WeChat OAuth authentication flow.
    
    Redirects the user to WeChat's authentication page with appropriate params.
    """
    app_id = settings.WECHAT_OAUTH_APP_ID
    redirect_uri = settings.WECHAT_OAUTH_REDIRECT_URI
    
    # Determine if request is from the API browsable interface
    state = 'api' if is_api_request(request) else 'frontend'
    
    # Build OAuth URL with necessary parameters
    params = {
        'appid': app_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'snsapi_login',
        'state': state,
    }
    
    # WeChat's URL format is slightly different from standard OAuth
    auth_url = f"https://open.weixin.qq.com/connect/qrconnect?{urlencode(params)}#wechat_redirect"
    return HttpResponseRedirect(auth_url)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def wechat_callback(request):
    """Handle WeChat OAuth callback and authenticate/register user.
    
    Creates or updates the user account based on WeChat profile data.
    """
    code = request.GET.get('code')
    state = request.GET.get('state', '')
    return_to_api = state == 'api'
    
    if not code:
        return handle_oauth_error(
            "Authorization code not provided", 
            return_to_api=return_to_api,
            log_msg="WeChat OAuth callback received without authorization code"
        )
    
    try:
        # Exchange authorization code for access token and openid
        token_data = exchange_wechat_code_for_token(code)
        
        if 'errcode' in token_data:
            logger.error(f"WeChat access token error: {token_data['errmsg']}")
            return handle_oauth_error(token_data['errmsg'], return_to_api=return_to_api)
            
        # Extract critical values
        access_token = token_data.get('access_token')
        openid = token_data.get('openid')
        
        if not access_token or not openid:
            return handle_oauth_error(
                "Failed to obtain user information", 
                return_to_api=return_to_api,
                log_msg="Failed to obtain access token or openid from WeChat"
            )
        
        # Get detailed user information
        try:
            user_data = get_wechat_user_info(access_token, openid)
            
            if 'errcode' in user_data:
                return handle_oauth_error(
                    user_data['errmsg'], 
                    return_to_api=return_to_api,
                    log_msg=f"WeChat userinfo error: {user_data['errmsg']}"
                )
            
            # Find or create the user
            try:
                user = find_or_create_wechat_user(openid, user_data)
                
                # Generate JWT tokens for our application
                tokens = generate_tokens_for_user(user)
                return redirect_with_tokens(tokens, return_to_api=return_to_api)
                
            except Exception as e:
                logger.error(f"Error creating/updating user from WeChat OAuth: {str(e)}\n{traceback.format_exc()}")
                return handle_oauth_error(
                    "Failed to create or update user account", 
                    return_to_api=return_to_api
                )
                
        except requests.RequestException as e:
            logger.error(f"WeChat userinfo request error: {str(e)}\n{traceback.format_exc()}")
            return handle_oauth_error("Failed to retrieve user profile", return_to_api=return_to_api)
            
    except requests.RequestException as e:
        logger.error(f"WeChat OAuth token exchange error: {str(e)}\n{traceback.format_exc()}")
        return handle_oauth_error(
            "Failed to communicate with authentication server", 
            return_to_api=return_to_api
        )
    except Exception as e:
        logger.error(f"Unexpected error in WeChat OAuth callback: {str(e)}\n{traceback.format_exc()}")
        return handle_oauth_error("Authentication failed", return_to_api=return_to_api)


def exchange_wechat_code_for_token(code):
    """Exchange authorization code for WeChat tokens.
    
    Args:
        code: Authorization code from WeChat
        
    Returns:
        dict: Token data from WeChat
        
    Raises:
        requests.RequestException: If API call fails
    """
    token_url = "https://api.weixin.qq.com/sns/oauth2/access_token"
    params = {
        'appid': settings.WECHAT_OAUTH_APP_ID,
        'secret': settings.WECHAT_OAUTH_SECRET,
        'code': code,
        'grant_type': 'authorization_code'
    }
    
    response = requests.get(token_url, params=params)
    response.raise_for_status()
    return response.json()


def get_wechat_user_info(access_token, openid):
    """Get user profile information from WeChat.
    
    Args:
        access_token: OAuth access token
        openid: User's WeChat openid
        
    Returns:
        dict: User profile data
        
    Raises:
        requests.RequestException: If API call fails
    """
    userinfo_url = "https://api.weixin.qq.com/sns/userinfo"
    params = {
        'access_token': access_token,
        'openid': openid
    }
    
    response = requests.get(userinfo_url, params=params)
    response.raise_for_status()
    return response.json()


def find_or_create_wechat_user(openid, user_data):
    """Find existing user or create new user from WeChat profile.
    
    Args:
        openid: User's WeChat openid
        user_data: Dict containing WeChat profile data
        
    Returns:
        User: MongoDB user object
        
    Raises:
        Exception: If user creation/update fails
    """
    # Try to find the user first
    user = User.objects(auth_provider='wechat', auth_provider_id=openid).first()
    nickname = user_data.get('nickname', '')
    username = f"wechat_{openid[:10]}"
    
    if not user:
        # User doesn't exist, create one
        user = User(
            username=username,
            email=f"{openid}@wechat.placeholder",  # WeChat doesn't provide email
            auth_provider='wechat',
            auth_provider_id=openid,
            full_name=nickname,
            is_verified=True  # WeChat users are considered verified
        )
        user.save()
        logger.info(f"Created new user via WeChat OAuth: {openid}")
    else:
        # Update existing user with latest data
        user.full_name = nickname if nickname else user.full_name
        user.save()
        logger.info(f"Updated existing user via WeChat OAuth: {openid}")
        
    return user


# =============================================================================
# Utility Endpoints
# =============================================================================

def api_logout(request):
    """Clear authentication cookies and redirect.
    
    Used for logging out users in the DRF browsable API interface.
    """
    response = HttpResponseRedirect(request.GET.get('next', '/api/?format=api'))
    response.delete_cookie('accessToken')
    return response
