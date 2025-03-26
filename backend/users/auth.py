import logging

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import AnonymousUser
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
            user = User.objects.get(id=user_id)
        except (User.DoesNotExist, ValueError):
            logger.warning(f"User not found with ID: {user_id}")
            return AnonymousUser()

        if not user.is_active:
            logger.warning(f"User {user_id} is not active")
            return AnonymousUser()

        return user
