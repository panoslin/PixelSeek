import json
import logging

import requests
from django.conf import settings
from django.http import HttpResponseRedirect
from rest_framework import (
    status,
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


# Google OAuth Views
def google_login(request):
    """Initiates Google OAuth flow"""
    redirect_uri = settings.GOOGLE_OAUTH_REDIRECT_URI
    client_id = settings.GOOGLE_OAUTH_CLIENT_ID

    auth_url = (
        f"https://accounts.google.com/o/oauth2/auth"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope=openid%20email%20profile"
    )

    return HttpResponseRedirect(auth_url)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def google_callback(request):
    """Handles Google OAuth callback and creates/authenticates user"""
    code = request.GET.get('code')

    if not code:
        return Response({
                            "error": "Authorization code not provided"
                        },
                        status=status.HTTP_400_BAD_REQUEST)

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
        response = requests.post(token_url, data=payload)
        token_data = response.json()

        id_token = token_data.get('id_token')
        if not id_token:
            return Response({
                                "error": "Failed to obtain id_token"
                            },
                            status=status.HTTP_400_BAD_REQUEST)

        # Decode JWT without verification (Google already verified it)
        # In production, you'd validate this token
        header, payload, signature = id_token.split('.')
        payload += '=' * (4 - len(payload) % 4)  # Add padding
        user_data = json.loads(payload.encode().decode('base64'))

        # Get user info from payload
        email = user_data.get('email')
        if not email:
            return Response({
                                "error": "Email not found in token payload"
                            },
                            status=status.HTTP_400_BAD_REQUEST)

        # Find or create user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username':         email.split('@')[0],
                'auth_provider':    'google',
                'auth_provider_id': user_data.get('sub'),
                'full_name':        user_data.get('name', ''),
                'is_verified':      user_data.get('email_verified', False)
            }
        )

        if not created:
            # Update existing user with latest data
            user.auth_provider = 'google'
            user.auth_provider_id = user_data.get('sub')
            user.full_name = user_data.get('name', user.full_name)
            user.is_verified = user_data.get('email_verified', user.is_verified)
            user.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        tokens = {
            'refresh': str(refresh),
            'access':  str(refresh.access_token),
        }

        # Redirect to frontend with tokens
        frontend_url = settings.CORS_ALLOWED_ORIGINS[0]
        redirect_url = f"{frontend_url}/auth/callback?tokens={json.dumps(tokens)}"
        return HttpResponseRedirect(redirect_url)

    except Exception as e:
        logger.error(f"Google OAuth error: {str(e)}")
        return Response({
                            "error": "Authentication failed"
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# WeChat OAuth Views
def wechat_login(request):
    """Initiates WeChat OAuth flow"""
    redirect_uri = settings.WECHAT_OAUTH_REDIRECT_URI
    app_id = settings.WECHAT_OAUTH_APP_ID

    auth_url = (
        f"https://open.weixin.qq.com/connect/qrconnect"
        f"?appid={app_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope=snsapi_login"
        f"&state=STATE#wechat_redirect"
    )

    return HttpResponseRedirect(auth_url)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def wechat_callback(request):
    """Handles WeChat OAuth callback and creates/authenticates user"""
    code = request.GET.get('code')

    if not code:
        return Response({
                            "error": "Authorization code not provided"
                        },
                        status=status.HTTP_400_BAD_REQUEST)

    # Exchange code for access token
    token_url = "https://api.weixin.qq.com/sns/oauth2/access_token"
    params = {
        'appid':      settings.WECHAT_OAUTH_APP_ID,
        'secret':     settings.WECHAT_OAUTH_SECRET,
        'code':       code,
        'grant_type': 'authorization_code'
    }

    try:
        response = requests.get(token_url, params=params)
        token_data = response.json()

        if 'errcode' in token_data:
            return Response({
                                "error": f"WeChat error: {token_data['errmsg']}"
                            },
                            status=status.HTTP_400_BAD_REQUEST)

        access_token = token_data.get('access_token')
        openid = token_data.get('openid')

        if not access_token or not openid:
            return Response({
                                "error": "Failed to obtain access token or openid"
                            },
                            status=status.HTTP_400_BAD_REQUEST)

        # Get user info from WeChat
        userinfo_url = "https://api.weixin.qq.com/sns/userinfo"
        params = {
            'access_token': access_token,
            'openid':       openid
        }

        response = requests.get(userinfo_url, params=params)
        user_data = response.json()

        if 'errcode' in user_data:
            return Response({
                                "error": f"WeChat userinfo error: {user_data['errmsg']}"
                            },
                            status=status.HTTP_400_BAD_REQUEST)

        # Generate a username from nickname or openid
        username = user_data.get('nickname', '').replace(' ', '_') or f"wechat_{openid[:10]}"

        # Find or create user - using openid as the unique identifier
        user, created = User.objects.get_or_create(
            auth_provider='wechat',
            auth_provider_id=openid,
            defaults={
                'username':    username,
                'email':       f"{openid}@wechat.placeholder",  # WeChat doesn't provide email
                'full_name':   user_data.get('nickname', ''),
                'is_verified': True  # WeChat users are considered verified
            }
        )

        if not created:
            # Update existing user with latest data
            user.full_name = user_data.get('nickname', user.full_name)
            user.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        tokens = {
            'refresh': str(refresh),
            'access':  str(refresh.access_token),
        }

        # Redirect to frontend with tokens
        frontend_url = settings.CORS_ALLOWED_ORIGINS[0]
        redirect_url = f"{frontend_url}/auth/callback?tokens={json.dumps(tokens)}"
        return HttpResponseRedirect(redirect_url)

    except Exception as e:
        logger.error(f"WeChat OAuth error: {str(e)}")
        return Response({
                            "error": "Authentication failed"
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
