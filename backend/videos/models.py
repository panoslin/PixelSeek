from mongoengine import Document, StringField, FloatField, IntField, BooleanField, \
                      ListField, DictField, DateTimeField, ReferenceField
from datetime import datetime
from users.models import User

class Video(Document):
    """
    Video model for storing video content metadata and file references.
    """
    title = StringField(required=True, max_length=200)
    description = StringField(max_length=2000)
    
    # File information
    file_path = StringField()
    thumbnail_path = StringField()
    duration = FloatField()
    file_size = IntField()  # in bytes
    format = StringField()
    resolution = StringField()
    
    # Keyframes
    keyframes = ListField(StringField())  # URLs or file paths to keyframes
    keyframes_extracted = BooleanField(default=False)
    keyframe_count = IntField(default=0)
    
    # Ownership and access
    owner = ReferenceField(User, required=True)
    is_public = BooleanField(default=True)
    access_level = StringField(choices=['public', 'restricted', 'private'], default='public')
    
    # Metadata for search
    tags = ListField(StringField(max_length=50))
    colors = ListField(DictField())  # Store dominant colors as {color: hex, percentage: float}
    
    # Vector search reference - ID that links to Weaviate
    vector_id = StringField()
    keyframe_vector_ids = ListField(StringField())  # List of Weaviate IDs for keyframes
    
    # Stats
    view_count = IntField(default=0)
    download_count = IntField(default=0)
    like_count = IntField(default=0)
    
    # Processing status
    status = StringField(choices=['processing', 'extracting_keyframes', 'indexing_vectors', 'ready', 'error'], default='processing')
    error_message = StringField()
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'indexes': [
            'owner', 
            'tags', 
            'status',
            'created_at',
            {
                'fields': ['$title', '$description'],
                'default_language': 'english',
                'weights': {'title': 10, 'description': 5}
            }
        ],
        'collection': 'videos'
    }
    
    def __str__(self):
        return self.title


class SearchHistory(Document):
    """
    Model to store user search history and patterns.
    """
    user = ReferenceField(User, required=True)
    
    # Search details
    query_type = StringField(choices=['text', 'image', 'color', 'tag', 'keyframe'])
    query_content = DictField()  # Flexible structure based on query_type
    
    # Results
    results_count = IntField(default=0)
    selected_video = ReferenceField(Video)
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'indexes': ['user', 'query_type', 'created_at'],
        'collection': 'search_history'
    }


class VectorReference(Document):
    """
    Maps Django objects to their vector representations in Weaviate.
    Used to maintain the relationship between MongoDB documents and Weaviate vectors.
    """
    content_type = StringField(required=True)  # 'video', 'image', 'keyframe', etc.
    object_id = StringField(required=True)  # MongoDB ObjectId as string
    weaviate_id = StringField(required=True)  # UUID in Weaviate
    vector_type = StringField()  # 'visual', 'text_embedding', etc.
    
    # For keyframes, store additional metadata
    parent_video_id = StringField()  # If this is a keyframe, reference to the parent video
    keyframe_index = IntField()  # Position in the sequence of keyframes
    timestamp = FloatField()  # Timestamp in the video (seconds)
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'indexes': [
            'weaviate_id',
            ('content_type', 'object_id'),
            'parent_video_id'
        ],
        'collection': 'vector_references'
    }
    
    def __str__(self):
        return f"{self.content_type}:{self.object_id} -> {self.weaviate_id}"