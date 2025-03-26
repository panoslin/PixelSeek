from rest_framework import serializers
from rest_framework_mongoengine import serializers as mongoengine_serializers

from .models import User


class UserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True, max_length=100)
    full_name = serializers.CharField(required=False, allow_blank=True, max_length=200)
    auth_provider = serializers.ChoiceField(choices=['google', 'wechat', 'email'], default='email')
    auth_provider_id = serializers.CharField(required=False, allow_blank=True)
    is_active = serializers.BooleanField(default=True)
    is_staff = serializers.BooleanField(default=False)
    is_verified = serializers.BooleanField(default=False)
    subscription_tier = serializers.ChoiceField(choices=['free', 'basic', 'premium'], default='free')
    credits_balance = serializers.IntegerField(default=0)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True, required=False, allow_null=True)
    search_preferences = serializers.DictField(required=False, default=dict)

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class UserProfileSerializer(serializers.Serializer):
    """Serializer for user profile data that's safe to expose to the frontend"""
    id = serializers.CharField(source='pk', read_only=True)
    email = serializers.EmailField(read_only=True)
    username = serializers.CharField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    auth_provider = serializers.CharField(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    subscription_tier = serializers.CharField(read_only=True)
    credits_balance = serializers.IntegerField(read_only=True)
    search_preferences = serializers.DictField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)


class SSOTokenObtainSerializer(serializers.Serializer):
    """Serializer for obtaining tokens via SSO"""
    provider = serializers.ChoiceField(choices=['google', 'wechat'])
    code = serializers.CharField()
    redirect_uri = serializers.CharField(required=False)


class UserUpdateSerializer(mongoengine_serializers.DocumentSerializer):
    """
    Serializer for updating user information.
    Only allows updates to specific fields.
    """

    class Meta:
        model = User
        fields = ['username', 'full_name', 'search_preferences']
