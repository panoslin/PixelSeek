import base64
import json
import logging
import traceback

import requests
from django.conf import settings
from django.http import HttpResponseRedirect
from rest_framework import (
    viewsets,
    permissions,
)
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import (
    UserSerializer,
    UserProfileSerializer,
)

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)


# OAuth Helper Functions
def generate_tokens_for_user(user):
    """Generate JWT tokens for a user"""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access':  str(refresh.access_token),
    }


# DRF API Browser Authentication
def set_auth_cookie(response, token):
    """Set JWT token as an HTTP-only cookie"""
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
    """Redirect to frontend with tokens or error message"""
    # Check if we should return to the API interface
    if return_to_api:
        # For DRF browsable API, redirect back to the API page with a cookie
        response = HttpResponseRedirect('/api/?format=api')
        if not error and tokens:
            response = set_auth_cookie(response, tokens['access'])
        return response

    # For regular frontend redirects
    frontend_url = settings.CORS_ALLOWED_ORIGINS[0]

    if error:
        redirect_url = f"{frontend_url}/auth/callback?error={error}"
    else:
        redirect_url = f"{frontend_url}/auth/callback?tokens={json.dumps(tokens)}"

    return HttpResponseRedirect(redirect_url)


# Monkey-patch the function to store the request
def wrapper(original_func):
    def new_func(request, *args, **kwargs):
        # Store the request to access it in redirect_with_tokens
        redirect_with_tokens.request = request
        return original_func(request, *args, **kwargs)

    return new_func


# Google OAuth Views
def google_login(request):
    """Initiates Google OAuth flow"""
    redirect_uri = settings.GOOGLE_OAUTH_REDIRECT_URI
    client_id = settings.GOOGLE_OAUTH_CLIENT_ID

    # Check if the request is coming from the API interface
    from_api = 'api' in request.META.get('HTTP_REFERER', '')
    state = 'api' if from_api else 'frontend'

    auth_url = (
        f"https://accounts.google.com/o/oauth2/auth"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope=openid%20email%20profile"
        f"&state={state}"
    )

    return HttpResponseRedirect(auth_url)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def google_callback(request):
    """Handles Google OAuth callback and creates/authenticates user"""
    code = request.GET.get('code')
    state = request.GET.get('state', '')

    # Check if the original request came from the API interface
    return_to_api = state == 'api'

    if not code:
        logger.warning("Google OAuth callback received without authorization code")
        return redirect_with_tokens(None, error="Authorization code not provided", return_to_api=return_to_api)

    # Exchange code for tokens
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        'code':          code,
        'client_id':     settings.GOOGLE_OAUTH_CLIENT_ID,
        'client_secret': settings.GOOGLE_OAUTH_SECRET,
        'redirect_uri':  settings.GOOGLE_OAUTH_REDIRECT_URI,
        'grant_type':    'authorization_code'
    }

    try:
        # Request tokens from Google
        response = requests.post(token_url, data=payload)
        response.raise_for_status()  # Raise exception for non-2xx responses
        token_data = response.json()

        id_token = token_data.get('id_token')
        if not id_token:
            logger.error("Failed to obtain id_token from Google")
            return redirect_with_tokens(None, error="Failed to obtain user information", return_to_api=return_to_api)

        # Decode JWT without verification (Google already verified it)
        # In production, you'd validate this token
        try:
            header, payload_part, signature = id_token.split('.')
            # Add padding if needed
            payload_part += '=' * ((4 - len(payload_part) % 4) % 4)
            # Decode using base64 module
            decoded_bytes = base64.urlsafe_b64decode(payload_part)
            decoded_string = decoded_bytes.decode('utf-8')
            user_data = json.loads(decoded_string)
        except Exception as e:
            logger.error(f"Error decoding Google id_token: {traceback.format_exc()}")
            return redirect_with_tokens(None, error="Failed to process authentication token",
                                        return_to_api=return_to_api)

        # Get user info from payload
        email = user_data.get('email')
        if not email:
            logger.error("Email not found in Google token payload")
            return redirect_with_tokens(None, error="Email not found in user profile", return_to_api=return_to_api)

        # Find or create user - MongoEngine version
        try:
            # Try to find the user first
            user = User.objects(email=email).first()
            created = False

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
                created = True
                logger.info(f"Created new user via Google OAuth: {email}")
            else:
                # Update existing user with latest data
                user.auth_provider = 'google'
                user.auth_provider_id = user_data.get('sub')
                user.full_name = user_data.get('name', user.full_name)
                user.is_verified = user_data.get('email_verified', user.is_verified)
                user.save()
                logger.info(f"Updated existing user via Google OAuth: {email}")

            # Generate JWT tokens
            tokens = generate_tokens_for_user(user)

            # Redirect to frontend with tokens
            return redirect_with_tokens(tokens, return_to_api=return_to_api)

        except Exception as e:
            logger.error(f"Error creating/updating user from Google OAuth: {traceback.format_exc()}")
            return redirect_with_tokens(None, error="Failed to create or update user account",
                                        return_to_api=return_to_api)

    except requests.RequestException as e:
        logger.error(f"Google OAuth token exchange error: {traceback.format_exc()}")
        return redirect_with_tokens(None, error="Failed to communicate with authentication server",
                                    return_to_api=return_to_api)
    except Exception as e:
        logger.error(f"Unexpected error in Google OAuth callback: {traceback.format_exc()}")
        return redirect_with_tokens(None, error="Authentication failed", return_to_api=return_to_api)


# WeChat OAuth Views
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def wechat_login(request):
    """Initiates WeChat OAuth flow"""
    app_id = settings.WECHAT_OAUTH_APP_ID
    redirect_uri = settings.WECHAT_OAUTH_REDIRECT_URI

    # Check if the request is coming from the API interface
    from_api = 'api' in request.META.get('HTTP_REFERER', '')
    state = 'api' if from_api else 'frontend'

    auth_url = (
        f"https://open.weixin.qq.com/connect/qrconnect"
        f"?appid={app_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope=snsapi_login"
        f"&state={state}"
        f"#wechat_redirect"
    )

    return HttpResponseRedirect(auth_url)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def wechat_callback(request):
    """Handles WeChat OAuth callback"""
    code = request.GET.get('code')
    state = request.GET.get('state', '')

    # Check if the original request came from the API interface
    return_to_api = state == 'api'

    if not code:
        logger.warning("WeChat OAuth callback received without authorization code")
        return redirect_with_tokens(None, error="Authorization code not provided", return_to_api=return_to_api)

    # Exchange code for access token
    token_url = "https://api.weixin.qq.com/sns/oauth2/access_token"
    params = {
        'appid':      settings.WECHAT_OAUTH_APP_ID,
        'secret':     settings.WECHAT_OAUTH_SECRET,
        'code':       code,
        'grant_type': 'authorization_code'
    }

    try:
        # Get tokens from WeChat
        response = requests.get(token_url, params=params)
        response.raise_for_status()
        token_data = response.json()

        if 'errcode' in token_data:
            logger.error(f"WeChat access token error: {token_data['errmsg']}")
            return redirect_with_tokens(None, error=token_data['errmsg'], return_to_api=return_to_api)

        access_token = token_data.get('access_token')
        openid = token_data.get('openid')

        if not access_token or not openid:
            logger.error("Failed to obtain access token or openid from WeChat")
            return redirect_with_tokens(None, error="Failed to obtain user information", return_to_api=return_to_api)

        # Get user info
        userinfo_url = "https://api.weixin.qq.com/sns/userinfo"
        userinfo_params = {
            'access_token': access_token,
            'openid':       openid
        }

        try:
            userinfo_response = requests.get(userinfo_url, params=userinfo_params)
            userinfo_response.raise_for_status()
            user_data = userinfo_response.json()

            if 'errcode' in user_data:
                logger.error(f"WeChat userinfo error: {user_data['errmsg']}")
                return redirect_with_tokens(None, error=user_data['errmsg'], return_to_api=return_to_api)

            nickname = user_data.get('nickname', '')
            # Generate a username based on openid since WeChat doesn't provide email
            username = f"wechat_{openid[:10]}"

            try:
                # Try to find the user first
                user = User.objects(auth_provider='wechat', auth_provider_id=openid).first()
                created = False

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
                    created = True
                    logger.info(f"Created new user via WeChat OAuth: {openid}")
                else:
                    # Update existing user with latest data
                    user.full_name = nickname if nickname else user.full_name
                    user.save()
                    logger.info(f"Updated existing user via WeChat OAuth: {openid}")

                # Generate JWT tokens
                tokens = generate_tokens_for_user(user)

                # Redirect to frontend with tokens
                return redirect_with_tokens(tokens, return_to_api=return_to_api)

            except Exception as e:
                logger.error(f"Error creating/updating user from WeChat OAuth: {traceback.format_exc()}")
                return redirect_with_tokens(None, error="Failed to create or update user account",
                                            return_to_api=return_to_api)

        except requests.RequestException as e:
            logger.error(f"WeChat userinfo request error: {traceback.format_exc()}")
            return redirect_with_tokens(None, error="Failed to retrieve user profile", return_to_api=return_to_api)

    except requests.RequestException as e:
        logger.error(f"WeChat OAuth token exchange error: {traceback.format_exc()}")
        return redirect_with_tokens(None, error="Failed to communicate with authentication server",
                                    return_to_api=return_to_api)
    except Exception as e:
        logger.error(f"Unexpected error in WeChat OAuth callback: {traceback.format_exc()}")
        return redirect_with_tokens(None, error="Authentication failed", return_to_api=return_to_api)


# Apply the wrapper to the callback views
google_callback = wrapper(google_callback)
wechat_callback = wrapper(wechat_callback)


# Custom logout view for DRF Browsable API
def api_logout(request):
    """
    Custom logout view that clears authentication cookies
    """
    response = HttpResponseRedirect(request.GET.get('next', '/'))
    response.delete_cookie('accessToken')
    return response
