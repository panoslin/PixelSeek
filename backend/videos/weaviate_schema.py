import weaviate
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class WeaviateClient:
    """
    Client for interacting with Weaviate vector database.
    Handles schema creation and vector operations.
    Uses Chinese-CLIP for vectorization of both images and text.
    """
    def __init__(self):
        """Initialize the Weaviate client with configuration from settings."""
        self.client = weaviate.Client(
            url=settings.WEAVIATE_URL,
            auth_client_secret=weaviate.AuthApiKey(api_key=settings.WEAVIATE_API_KEY) if settings.WEAVIATE_API_KEY else None,
            additional_headers={
                "X-PixelSeek-Backend": "django"
            }
        )
        
    def create_schema(self):
        """
        Initialize the Weaviate schema for PixelSeek.
        Creates necessary classes for video content and search.
        All classes use Chinese-CLIP for vectorization.
        """
        try:
            # Check if schema exists first
            schema = self.client.schema.get()
            existing_classes = [c["class"] for c in schema["classes"]] if "classes" in schema else []
            
            # Define Video class with Chinese-CLIP vectorizer
            if "Video" not in existing_classes:
                video_class = {
                    "class": "Video",
                    "description": "Video content with Chinese-CLIP embeddings",
                    "vectorizer": "custom-chinese-clip",
                    "vectorIndexType": "hnsw",
                    "moduleConfig": {
                        "custom-chinese-clip": {
                            "imageFields": ["thumbnail"]
                        }
                    },
                    "properties": [
                        {
                            "name": "thumbnail",
                            "dataType": ["blob"],
                            "description": "The thumbnail image of the video"
                        },
                        {
                            "name": "title",
                            "dataType": ["text"],
                            "description": "The title of the video",
                            "indexInverted": True
                        },
                        {
                            "name": "description",
                            "dataType": ["text"],
                            "description": "The description of the video",
                            "indexInverted": True
                        },
                        {
                            "name": "tags",
                            "dataType": ["text[]"],
                            "description": "Tags associated with the video",
                            "indexInverted": True
                        },
                        {
                            "name": "colors",
                            "dataType": ["text[]"],
                            "description": "Dominant colors in the video (hex values)",
                            "indexInverted": True
                        },
                        {
                            "name": "mongodb_id",
                            "dataType": ["string"],
                            "description": "Reference to MongoDB ObjectId",
                            "indexInverted": True
                        },
                        {
                            "name": "owner_id",
                            "dataType": ["string"],
                            "description": "Reference to the owner in MongoDB",
                            "indexInverted": True
                        },
                        {
                            "name": "access_level",
                            "dataType": ["string"],
                            "description": "Access level for permissions",
                            "indexInverted": True
                        }
                    ]
                }
                self.client.schema.create_class(video_class)
                logger.info("Created Video class in Weaviate schema with Chinese-CLIP vectorizer")
                
            # Define Keyframe class with Chinese-CLIP vectorizer
            if "Keyframe" not in existing_classes:
                keyframe_class = {
                    "class": "Keyframe",
                    "description": "Keyframe images extracted from videos with Chinese-CLIP embeddings",
                    "vectorizer": "custom-chinese-clip",
                    "vectorIndexType": "hnsw",
                    "moduleConfig": {
                        "custom-chinese-clip": {
                            "imageFields": ["image"]
                        }
                    },
                    "properties": [
                        {
                            "name": "image",
                            "dataType": ["blob"],
                            "description": "The keyframe image"
                        },
                        {
                            "name": "timestamp",
                            "dataType": ["number"],
                            "description": "Timestamp in the video (seconds)",
                            "indexInverted": True
                        },
                        {
                            "name": "index",
                            "dataType": ["int"],
                            "description": "Position in the sequence of keyframes",
                            "indexInverted": True
                        },
                        {
                            "name": "video_id",
                            "dataType": ["string"],
                            "description": "Reference to the Weaviate Video UUID",
                            "indexInverted": True
                        },
                        {
                            "name": "mongodb_id",
                            "dataType": ["string"],
                            "description": "Reference to MongoDB ObjectId of the video",
                            "indexInverted": True
                        },
                        {
                            "name": "access_level",
                            "dataType": ["string"],
                            "description": "Inherited access level from the video",
                            "indexInverted": True
                        }
                    ]
                }
                self.client.schema.create_class(keyframe_class)
                logger.info("Created Keyframe class in Weaviate schema with Chinese-CLIP vectorizer")
                
            # Define TextSearch class with Chinese-CLIP vectorizer
            if "TextSearch" not in existing_classes:
                text_search_class = {
                    "class": "TextSearch",
                    "description": "Text embeddings for semantic search using Chinese-CLIP",
                    "vectorizer": "custom-chinese-clip",
                    "vectorIndexType": "hnsw",
                    "moduleConfig": {
                        "custom-chinese-clip": {
                            "textFields": ["content"]
                        }
                    },
                    "properties": [
                        {
                            "name": "content",
                            "dataType": ["text"],
                            "description": "The text content to search against"
                        },
                        {
                            "name": "type",
                            "dataType": ["string"],
                            "description": "The type of text (title, description, tag)",
                            "indexInverted": True
                        },
                        {
                            "name": "video_id",
                            "dataType": ["string"],
                            "description": "Reference to the Weaviate Video UUID",
                            "indexInverted": True
                        },
                        {
                            "name": "mongodb_id",
                            "dataType": ["string"],
                            "description": "Reference to MongoDB ObjectId",
                            "indexInverted": True
                        }
                    ]
                }
                self.client.schema.create_class(text_search_class)
                logger.info("Created TextSearch class in Weaviate schema with Chinese-CLIP vectorizer")
                
            # Define ColorSearch class (no vectorizer change needed as it uses RGB values)
            if "ColorSearch" not in existing_classes:
                color_search_class = {
                    "class": "ColorSearch",
                    "description": "Color-based search for videos",
                    "vectorIndexType": "hnsw",
                    "properties": [
                        {
                            "name": "color",
                            "dataType": ["string"],
                            "description": "Hex color code",
                            "indexInverted": True
                        },
                        {
                            "name": "percentage",
                            "dataType": ["number"],
                            "description": "Percentage of the color in the image",
                        },
                        {
                            "name": "rgb_vector",
                            "dataType": ["number[]"],
                            "description": "RGB vector representation of the color"
                        },
                        {
                            "name": "video_id",
                            "dataType": ["string"],
                            "description": "Reference to the Weaviate Video UUID",
                            "indexInverted": True
                        },
                        {
                            "name": "mongodb_id",
                            "dataType": ["string"],
                            "description": "Reference to MongoDB ObjectId",
                            "indexInverted": True
                        }
                    ]
                }
                self.client.schema.create_class(color_search_class)
                logger.info("Created ColorSearch class in Weaviate schema")
                
            return True
            
        except Exception as e:
            logger.error(f"Error creating Weaviate schema: {e}")
            return False
    
    def initialize(self):
        """
        Initialize the Weaviate connection and schema.
        """
        try:
            # Check if Weaviate is ready
            if not self.client.is_ready():
                logger.error("Weaviate server is not ready")
                return False
                
            # Create schema
            return self.create_schema()
            
        except Exception as e:
            logger.error(f"Error initializing Weaviate: {e}")
            return False
            
    def add_video(self, mongodb_id, thumbnail_data, title, description, tags, colors, owner_id, access_level):
        """
        Add a video to Weaviate with its Chinese-CLIP embedding.
        
        Args:
            mongodb_id: The MongoDB ObjectId as string
            thumbnail_data: Binary data of the thumbnail image
            title: Video title
            description: Video description
            tags: List of tags
            colors: List of dominant color hex codes
            owner_id: User ID of the owner
            access_level: Access level for permissions
            
        Returns:
            UUID of the created object in Weaviate
        """
        try:
            # Create data object with properties
            data_obj = {
                "thumbnail": thumbnail_data,
                "title": title,
                "description": description,
                "tags": tags,
                "colors": colors,
                "mongodb_id": mongodb_id,
                "owner_id": owner_id,
                "access_level": access_level
            }
            
            # Add to Weaviate
            result = self.client.data_object.create(
                class_name="Video",
                data_object=data_obj
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error adding video to Weaviate: {e}")
            return None
            
    def add_keyframe(self, mongodb_id, video_weaviate_id, keyframe_data, timestamp, index, access_level):
        """
        Add a keyframe from a video to Weaviate with its Chinese-CLIP embedding.
        
        Args:
            mongodb_id: The MongoDB ObjectId of the video as string
            video_weaviate_id: Weaviate UUID of the parent video
            keyframe_data: Binary data of the keyframe image
            timestamp: Timestamp in the video (seconds)
            index: Position in the sequence of keyframes
            access_level: Access level inherited from the video
            
        Returns:
            UUID of the created keyframe object in Weaviate
        """
        try:
            # Create data object with properties
            data_obj = {
                "image": keyframe_data,
                "timestamp": timestamp,
                "index": index,
                "video_id": video_weaviate_id,
                "mongodb_id": mongodb_id,
                "access_level": access_level
            }
            
            # Add to Weaviate
            result = self.client.data_object.create(
                class_name="Keyframe",
                data_object=data_obj
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error adding keyframe to Weaviate: {e}")
            return None
          
    def search_by_image(self, image_data, limit=20, offset=0, filters=None):
        """
        Search for videos using an image as query.
        
        Args:
            image_data: Binary data of the query image
            limit: Maximum number of results
            offset: Pagination offset
            filters: Additional filters to apply
            
        Returns:
            List of search results
        """
        try:
            query = self.client.query.get("Video", ["mongodb_id", "title", "description", "tags"])
            
            # Add filters if provided
            if filters:
                query = query.with_where(filters)
                
            # Execute nearImage search
            result = query.with_near_image({
                "image": image_data
            }).with_limit(limit).with_offset(offset).do()
            
            return result.get("data", {}).get("Get", {}).get("Video", [])
            
        except Exception as e:
            logger.error(f"Error searching by image: {e}")
            return []
            
    def search_by_keyframe(self, image_data, limit=20, offset=0, filters=None):
        """
        Search for keyframes using an image as query, then return the associated videos.
        
        Args:
            image_data: Binary data of the query image
            limit: Maximum number of results
            offset: Pagination offset
            filters: Additional filters to apply
            
        Returns:
            List of search results with keyframe information
        """
        try:
            # Search for keyframes first
            keyframe_query = self.client.query.get("Keyframe", ["mongodb_id", "video_id", "timestamp", "index"])
            
            # Add filters if provided
            if filters:
                keyframe_query = keyframe_query.with_where(filters)
                
            # Execute nearImage search on keyframes
            keyframe_result = keyframe_query.with_near_image({
                "image": image_data
            }).with_limit(limit * 2).do()  # Get more results as we'll group by video
            
            keyframes = keyframe_result.get("data", {}).get("Get", {}).get("Keyframe", [])
            
            if not keyframes:
                return []
                
            # Get unique video IDs from keyframe results
            video_ids = list(set(kf["video_id"] for kf in keyframes if "video_id" in kf))[:limit]
            
            # Get video details
            videos = []
            for video_id in video_ids:
                video_query = self.client.query.get("Video", ["mongodb_id", "title", "description", "tags"])
                video_result = video_query.with_id(video_id).do()
                video_data = video_result.get("data", {}).get("Get", {}).get("Video", [])
                
                if video_data:
                    # Find keyframes for this video
                    video_keyframes = [kf for kf in keyframes if kf.get("video_id") == video_id]
                    
                    # Add keyframe info to video result
                    video_data[0]["keyframes"] = video_keyframes
                    videos.append(video_data[0])
            
            return videos
            
        except Exception as e:
            logger.error(f"Error searching by keyframe: {e}")
            return []
            
    def search_by_text(self, query_text, limit=20, offset=0, filters=None):
        """
        Search for videos using text query via the TextSearch class.
        
        Args:
            query_text: Text query
            limit: Maximum number of results
            offset: Pagination offset
            filters: Additional filters to apply
            
        Returns:
            List of search results
        """
        try:
            query = self.client.query.get("TextSearch", ["mongodb_id", "video_id", "type"])
            
            # Add filters if provided
            if filters:
                query = query.with_where(filters)
                
            # Execute search
            result = query.with_near_text({
                "concepts": [query_text]
            }).with_limit(limit).with_offset(offset).do()
            
            return result.get("data", {}).get("Get", {}).get("TextSearch", [])
            
        except Exception as e:
            logger.error(f"Error searching by text: {e}")
            return []
            
    def search_by_color(self, hex_color, limit=20, offset=0, filters=None):
        """
        Search for videos by color proximity.
        
        Args:
            hex_color: Hex color code (e.g., "#FF5733")
            limit: Maximum number of results
            offset: Pagination offset
            filters: Additional filters to apply
            
        Returns:
            List of search results
        """
        try:
            # Convert hex to RGB vector [0-1]
            r = int(hex_color[1:3], 16) / 255
            g = int(hex_color[3:5], 16) / 255
            b = int(hex_color[5:7], 16) / 255
            
            vector = [r, g, b]
            
            query = self.client.query.get("ColorSearch", ["mongodb_id", "video_id", "color", "percentage"])
            
            # Add filters if provided
            if filters:
                query = query.with_where(filters)
                
            # Execute vector search
            result = query.with_near_vector({
                "vector": vector
            }).with_limit(limit).with_offset(offset).do()
            
            return result.get("data", {}).get("Get", {}).get("ColorSearch", [])
            
        except Exception as e:
            logger.error(f"Error searching by color: {e}")
            return []


# For importing in other modules
weaviate_client = WeaviateClient()

# For CLI initialization
if __name__ == "__main__":
    import django
    import os
    
    # Set up Django environment
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pixelseek.settings")
    django.setup()
    
    # Initialize Weaviate schema
    client = WeaviateClient()
    success = client.initialize()
    
    if success:
        print("✅ Weaviate schema initialized successfully with Chinese-CLIP vectorizer")
    else:
        print("❌ Failed to initialize Weaviate schema")