import logging

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import AnonymousUser
from django.middleware.csrf import get_token
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import User

logger = logging.getLogger(__name__)


class MongoEngineBackend(BaseBackend):
    """
    Custom authentication backend for MongoEngine User model.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Not used for SSO authentication, but required for the backend interface.
        """
        return None

    def get_user(self, user_id):
        """
        Get the user by ID. Used by Django's auth system.
        """
        try:
            return User.objects.get(id=user_id)
        except (User.DoesNotExist, ValueError):
            return None


class MongoEngineJWTAuthentication(JWTAuthentication):
    """
    JWT Authentication for MongoEngine User models.
    Extends the standard JWT authentication to work with MongoEngine.
    """

    def get_user(self, validated_token):
        """
        Get user from validated token.
        """
        user_id = validated_token.get('user_id')

        if not user_id:
            return AnonymousUser()

        try:
            user = User.objects(id=user_id).first()
        except (ValueError, User.DoesNotExist):
            logger.warning(f"User not found with ID: {user_id}")
            return AnonymousUser()

        if not user or not user.is_active:
            logger.warning(f"User {user_id} is not active")
            return AnonymousUser()

        return user


class JWTCookieAuthentication(BaseAuthentication):
    """
    An authentication plugin that authenticates requests through JWT
    tokens passed in a cookie for the browsable API.
    """
    www_authenticate_realm = 'api'

    def authenticate(self, request):
        access_token = request.COOKIES.get('accessToken')

        if not access_token:
            return None

        try:
            jwt_auth = MongoEngineJWTAuthentication()
            validated_token = jwt_auth.get_validated_token(access_token)
            user = jwt_auth.get_user(validated_token)

            if user is None or isinstance(user, AnonymousUser):
                return None

            # Add CSRF protection by setting a token
            get_token(request)
            return (user, access_token)

        except exceptions.AuthenticationFailed:
            return None
        except Exception as e:
            logger.error(f"JWT Cookie authentication error: {str(e)}")
            return None

    def authenticate_header(self, request):
        return f'Bearer realm="{self.www_authenticate_realm}"'
