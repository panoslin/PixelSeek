from rest_framework_mongoengine import serializers
from .models import User

class UserSerializer(serializers.DocumentSerializer):
    """
    Serializer for User model with full fields.
    Used for admin operations and detailed user information.
    """
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'last_login']
        
    def validate_email(self, value):
        """
        Validate that the email is not already taken.
        """
        if User.objects.filter(email=value).exclude(id=self.instance.id if self.instance else None).count() > 0:
            raise serializers.ValidationError("This email is already in use.")
        return value


class UserProfileSerializer(serializers.DocumentSerializer):
    """
    Serializer for User model with restricted fields.
    Used for public profile information.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'subscription_tier', 'created_at']
        read_only_fields = ['id', 'created_at', 'subscription_tier']


class UserUpdateSerializer(serializers.DocumentSerializer):
    """
    Serializer for updating user information.
    Only allows updates to specific fields.
    """
    class Meta:
        model = User
        fields = ['username', 'full_name', 'search_preferences'] 