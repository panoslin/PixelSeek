from rest_framework_mongoengine import serializers
from users.serializers import UserProfileSerializer
from .models import Video, SearchHistory, VectorReference


class VideoSerializer(serializers.DocumentSerializer):
    """
    Serializer for Video model with all fields.
    Used for detailed video information.
    """
    owner = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = Video
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'view_count', 'download_count', 'like_count', 'vector_id']


class VideoListSerializer(serializers.DocumentSerializer):
    """
    Simplified Video serializer for list views.
    """
    owner = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = Video
        fields = ['id', 'title', 'thumbnail_path', 'duration', 'owner', 'created_at', 'view_count', 'status']
        read_only_fields = fields


class VideoCreateSerializer(serializers.DocumentSerializer):
    """
    Serializer for creating new videos.
    """    
    class Meta:
        model = Video
        fields = ['title', 'description', 'file_path', 'thumbnail_path', 'tags', 'is_public', 'access_level']
        
    def validate(self, data):
        """
        Perform additional validation on video creation.
        """
        # Add validation logic here if needed
        return data


class SearchHistorySerializer(serializers.DocumentSerializer):
    """
    Serializer for search history records.
    """
    class Meta:
        model = SearchHistory
        fields = '__all__'
        read_only_fields = ['created_at']


class VectorReferenceSerializer(serializers.DocumentSerializer):
    """
    Serializer for vector reference mapping.
    """
    class Meta:
        model = VectorReference
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at'] 