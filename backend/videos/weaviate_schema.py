import atexit
import logging
import traceback
import uuid
from typing import (
    Dict,
    List,
    Optional,
)

import weaviate
from django.conf import settings
from weaviate.classes.config import Configure

logger = logging.getLogger(__name__)


class WeaviateClient:
    """
    Client for interacting with Weaviate vector database using v4 API.
    Handles collection creation and vector operations for PixelSeek.
    Uses Chinese-CLIP for vectorization of both images and text.
    """

    def __init__(self):
        """Initialize the Weaviate client and connect to the server."""
        self.client = None
        try:
            # Connect to Weaviate using v4.11.3 API
            self.client = weaviate.connect_to_local(
                host=settings.CONTAINER_WEAVIATE,
                port=settings.WEAVIATE_PORT,
            )

            # Get vectorizer module configuration from settings
            self.vectorizer_module = getattr(
                settings, "WEAVIATE_VECTORIZER_MODULE", "chinese-clip"
            )
            self.model_name = getattr(settings, "CLIP_MODEL_NAME", "RN50")

            # Log the vectorizer configuration
            logger.info(
                f"Using vectorizer module: {self.vectorizer_module}, model: {self.model_name}"
            )

            # Verify connection
            self.ping()
            logger.info(
                f"Successfully connected to Weaviate at {settings.WEAVIATE_URL}"
            )

            # Register close method to be called on exit
            atexit.register(self.close)

        except Exception as e:
            logger.warning(
                f"Warning: Could not connect to Weaviate: {traceback.format_exc()}"
            )
            # Initialize client as None to handle graceful failures
            self.client = None

    def __enter__(self):
        """Enable context manager support."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure connection is closed when exiting context."""
        self.close()

    def close(self):
        """
        Properly close the Weaviate client connection to prevent resource leaks.
        """
        if self.client is not None:
            try:
                self.client.close()
                logger.info("Weaviate connection closed properly")
            except Exception as e:
                logger.error(f"Error closing Weaviate connection: {e}")
            finally:
                self.client = None

    def create_schema(self) -> bool:
        """
        Initialize the Weaviate collections for PixelSeek.
        Creates necessary collections for video content and search.
        Uses Chinese-CLIP vectorizer module for handling images and text.

        Returns:
            bool: Success status
        """
        try:
            if self.client is None:
                return False

            # Check existing collections
            existing_collections = [
                col.name for col in self.client.collections.get_all()
            ]

            # Configure module settings based on environment variables
            module_config = {"imageFields": ["thumbnail"], "model": self.model_name}

            # Define Video collection with Chinese-CLIP vectorizer config
            if "Video" not in existing_collections:
                video_collection = self.client.collections.create(
                    name="Video",
                    description=f"Video content with {self.vectorizer_module} embeddings for search",
                    properties=[
                        {
                            "name": "title",
                            "description": "The title of the video",
                            "dataType": ["text"],
                            "indexFilterable": True,
                            "indexSearchable": True,
                            "tokenization": "field",
                        },
                        {
                            "name": "description",
                            "description": "The description of the video",
                            "dataType": ["text"],
                            "indexFilterable": True,
                            "indexSearchable": True,
                            "tokenization": "field",
                        },
                        {
                            "name": "tags",
                            "description": "Tags associated with the video",
                            "dataType": ["text[]"],
                            "indexFilterable": True,
                            "indexSearchable": True,
                        },
                        {
                            "name": "colors",
                            "description": "Dominant colors in the video (hex values)",
                            "dataType": ["text[]"],
                            "indexFilterable": True,
                        },
                        {
                            "name": "mongodb_id",
                            "description": "Reference to MongoDB ObjectId",
                            "dataType": ["text"],
                            "indexFilterable": True,
                            "indexSearchable": True,
                        },
                        {
                            "name": "owner_id",
                            "description": "Reference to the owner in MongoDB",
                            "dataType": ["text"],
                            "indexFilterable": True,
                        },
                        {
                            "name": "thumbnail",
                            "description": "The thumbnail image of the video",
                            "dataType": ["blob"],
                        },
                        {
                            "name": "access_level",
                            "description": "Access level for permissions",
                            "dataType": ["text"],
                            "indexFilterable": True,
                        },
                    ],
                    vector_index_config=Configure.VectorIndex.hnsw(
                        distance_metric=Configure.VectorIndex.Distance.COSINE
                    ),
                    # Configure to use module vectorizer based on environment settings
                    vectorizer_config=Configure.Vectorizer.module(
                        module_name=self.vectorizer_module, module_config=module_config
                    ),
                )
                logger.info(
                    f"Created Video collection in Weaviate with {self.vectorizer_module} vectorizer using model "
                    f"{self.model_name}"
                )

            # Configure module settings for keyframes
            keyframe_module_config = {
                "imageFields": ["image"],
                "model": self.model_name,
            }

            # Define Keyframe collection with Chinese-CLIP vectorizer config
            if "Keyframe" not in existing_collections:
                keyframe_collection = self.client.collections.create(
                    name="Keyframe",
                    description=f"Keyframe images extracted from videos with {self.vectorizer_module} embeddings",
                    properties=[
                        {
                            "name": "image",
                            "description": "The keyframe image",
                            "dataType": ["blob"],
                        },
                        {
                            "name": "timestamp",
                            "description": "Timestamp in the video (seconds)",
                            "dataType": ["number"],
                            "indexFilterable": True,
                        },
                        {
                            "name": "index",
                            "description": "Position in the sequence of keyframes",
                            "dataType": ["int"],
                            "indexFilterable": True,
                        },
                        {
                            "name": "video_id",
                            "description": "Reference to the Weaviate Video UUID",
                            "dataType": ["text"],
                            "indexFilterable": True,
                        },
                        {
                            "name": "mongodb_id",
                            "description": "Reference to MongoDB ObjectId of the video",
                            "dataType": ["text"],
                            "indexFilterable": True,
                        },
                        {
                            "name": "access_level",
                            "description": "Inherited access level from the video",
                            "dataType": ["text"],
                            "indexFilterable": True,
                        },
                    ],
                    vector_index_config=Configure.VectorIndex.hnsw(
                        distance_metric=Configure.VectorIndex.Distance.COSINE
                    ),
                    # Configure to use module vectorizer based on environment settings
                    vectorizer_config=Configure.Vectorizer.module(
                        module_name=self.vectorizer_module,
                        module_config=keyframe_module_config,
                    ),
                )
                logger.info(
                    f"Created Keyframe collection in Weaviate with {self.vectorizer_module} vectorizer using model "
                    f"{self.model_name}"
                )

            # Define ColorSearch collection
            if "ColorSearch" not in existing_collections:
                color_collection = self.client.collections.create(
                    name="ColorSearch",
                    description="Color-based search for videos",
                    properties=[
                        {
                            "name": "color",
                            "description": "Hex color code",
                            "dataType": ["text"],
                            "indexFilterable": True,
                        },
                        {
                            "name": "percentage",
                            "description": "Percentage of the color in the image",
                            "dataType": ["number"],
                            "indexFilterable": True,
                        },
                        {
                            "name": "video_id",
                            "description": "Reference to the Weaviate Video UUID",
                            "dataType": ["text"],
                            "indexFilterable": True,
                        },
                        {
                            "name": "mongodb_id",
                            "description": "Reference to MongoDB ObjectId",
                            "dataType": ["text"],
                            "indexFilterable": True,
                        },
                    ],
                    vector_index_config=Configure.VectorIndex.hnsw(
                        distance_metric=Configure.VectorIndex.Distance.COSINE
                    ),
                    # Note: No vectorizer config for ColorSearch as we provide RGB vectors directly
                )
                logger.info("Created ColorSearch collection in Weaviate")

            return True

        except Exception as e:
            logger.error(f"Error creating Weaviate collections: {e}")
            return False

    def initialize(self) -> bool:
        """
        Initialize the Weaviate connection and schema.

        Returns:
            bool: Success status
        """
        try:
            if self.client is None:
                logger.error("Weaviate client failed to initialize")
                return False

            # Create collections
            return self.create_schema()

        except Exception as e:
            logger.error(f"Error initializing Weaviate: {e}")
            return False

    def add_video(
        self,
        mongodb_id: str,
        thumbnail_data: bytes,
        title: str,
        description: str,
        tags: List[str],
        colors: List[str],
        owner_id: str,
        access_level: str,
    ) -> Optional[str]:
        """
        Add a video to Weaviate with its embedding using the configured vectorizer.

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
            str: UUID of the created object in Weaviate or None if failed
        """
        try:
            if self.client is None:
                return None

            # Get the Video collection
            video_collection = self.client.collections.get("Video")

            # Create unique UUID for the object
            object_uuid = str(uuid.uuid4())

            # Add video object with properties and vector source
            video_collection.data.insert(
                uuid=object_uuid,
                properties={
                    "mongodb_id": mongodb_id,
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "colors": colors,
                    "owner_id": owner_id,
                    "access_level": access_level,
                    "thumbnail": thumbnail_data,  # Used by the vectorizer module
                },
                # No explicit vector needed; Module will generate from thumbnail
            )

            return object_uuid

        except Exception as e:
            logger.error(f"Error adding video to Weaviate: {e}")
            return None

    def add_keyframe(
        self,
        mongodb_id: str,
        video_weaviate_id: str,
        keyframe_data: bytes,
        timestamp: float,
        index: int,
        access_level: str,
    ) -> Optional[str]:
        """
        Add a keyframe from a video to Weaviate with its embedding using the configured vectorizer.

        Args:
            mongodb_id: The MongoDB ObjectId of the video as string
            video_weaviate_id: Weaviate UUID of the parent video
            keyframe_data: Binary data of the keyframe image
            timestamp: Timestamp in the video (seconds)
            index: Position in the sequence of keyframes
            access_level: Access level inherited from the video

        Returns:
            str: UUID of the created keyframe object in Weaviate or None if failed
        """
        try:
            if self.client is None:
                return None

            # Get the Keyframe collection
            keyframe_collection = self.client.collections.get("Keyframe")

            # Create unique UUID for the object
            object_uuid = str(uuid.uuid4())

            # Add keyframe object with properties and vector source
            keyframe_collection.data.insert(
                uuid=object_uuid,
                properties={
                    "mongodb_id": mongodb_id,
                    "video_id": video_weaviate_id,
                    "timestamp": timestamp,
                    "index": index,
                    "access_level": access_level,
                    "image": keyframe_data,  # Used by the vectorizer module
                },
                # No explicit vector needed; Module will generate from image
            )

            return object_uuid

        except Exception as e:
            logger.error(f"Error adding keyframe to Weaviate: {e}")
            return None

    def add_color_reference(
        self,
        mongodb_id: str,
        video_id: str,
        color_hex: str,
        percentage: float,
        rgb_vector: List[float],
    ) -> Optional[str]:
        """
        Add a color reference for a video.

        Args:
            mongodb_id: The MongoDB ObjectId of the video
            video_id: Weaviate UUID of the video
            color_hex: Hex color code
            percentage: Percentage of the color in the image
            rgb_vector: RGB vector (normalized to [0,1])

        Returns:
            str: UUID of the created color object or None if failed
        """
        try:
            if self.client is None:
                return None

            # Get the ColorSearch collection
            color_collection = self.client.collections.get("ColorSearch")

            # Create unique UUID for the object
            object_uuid = str(uuid.uuid4())

            # Add color object with properties
            color_collection.data.insert(
                uuid=object_uuid,
                properties={
                    "mongodb_id": mongodb_id,
                    "video_id": video_id,
                    "color": color_hex,
                    "percentage": percentage,
                },
                # Set the vector directly from RGB values
                vector=rgb_vector,
            )

            return object_uuid

        except Exception as e:
            logger.error(f"Error adding color to Weaviate: {e}")
            return None

    def search_by_image(
        self, image_data: bytes, limit: int = 20, offset: int = 0, filters: Dict = None
    ) -> List[Dict]:
        """
        Search for videos using an image as query.
        The vector is created using the configured vectorizer module.

        Args:
            image_data: Binary data of the query image
            limit: Maximum number of results
            offset: Pagination offset
            filters: Additional filters to apply

        Returns:
            List of search results
        """
        try:
            if self.client is None:
                return []

            # Get the Video collection
            video_collection = self.client.collections.get("Video")

            # Build query using the image for v4.11.3 API
            query = video_collection.query.near_media(
                media_type="image",
                media_content=image_data,
                media_encoded=True,
                limit=limit,
                offset=offset,
            )

            # Add filters if provided
            if filters:
                query = query.with_where(filters)

            # Execute query
            result = query.objects

            # Format results
            return [
                {
                    "mongodb_id": obj.properties.get("mongodb_id"),
                    "title": obj.properties.get("title"),
                    "description": obj.properties.get("description"),
                    "tags": obj.properties.get("tags", []),
                    "_additional": {"id": obj.uuid, "distance": obj.metadata.distance},
                }
                for obj in result
            ]

        except Exception as e:
            logger.error(f"Error searching by image: {e}")
            return []

    def search_by_keyframe(
        self, image_data: bytes, limit: int = 20, offset: int = 0, filters: Dict = None
    ) -> List[Dict]:
        """
        Search for keyframes using an image as query, then return the associated videos.
        The vector is created using the configured vectorizer module.

        Args:
            image_data: Binary data of the query image
            limit: Maximum number of results
            offset: Pagination offset
            filters: Additional filters to apply

        Returns:
            List of search results with keyframe information
        """
        try:
            if self.client is None:
                return []

            # Get the Keyframe collection
            keyframe_collection = self.client.collections.get("Keyframe")

            # Build query for keyframes using v4.11.3 API
            query = keyframe_collection.query.near_media(
                media_type="image",
                media_content=image_data,
                media_encoded=True,
                limit=limit * 2,  # Get more results as we'll group by video
            )

            # Add filters if provided
            if filters:
                query = query.with_where(filters)

            # Execute query
            keyframe_results = query.objects

            if not keyframe_results:
                return []

            # Get unique video IDs from keyframe results
            video_ids = set()
            keyframes_by_video = {}

            for kf in keyframe_results:
                video_id = kf.properties.get("video_id")
                if video_id and len(video_ids) < limit:
                    video_ids.add(video_id)

                    if video_id not in keyframes_by_video:
                        keyframes_by_video[video_id] = []

                    keyframes_by_video[video_id].append(
                        {
                            "timestamp": kf.properties.get("timestamp"),
                            "index": kf.properties.get("index"),
                            "id": kf.uuid,
                            "distance": kf.metadata.distance,
                        }
                    )

            # Get video details for each found keyframe
            results = []
            video_collection = self.client.collections.get("Video")

            for video_id in video_ids:
                try:
                    video = video_collection.query.fetch_object_by_id(video_id)

                    if video:
                        results.append(
                            {
                                "mongodb_id": video.properties.get("mongodb_id"),
                                "title": video.properties.get("title"),
                                "description": video.properties.get("description"),
                                "tags": video.properties.get("tags", []),
                                "keyframes": keyframes_by_video.get(video_id, []),
                                "_additional": {"id": video.uuid},
                            }
                        )
                except Exception as ve:
                    logger.warning(f"Error fetching video {video_id}: {ve}")

            return results

        except Exception as e:
            logger.error(f"Error searching by keyframe: {e}")
            return []

    def search_by_text(
        self, query_text: str, limit: int = 20, offset: int = 0, filters: Dict = None
    ) -> List[Dict]:
        """
        Search for videos using text query.
        The vector is created using the configured vectorizer module.

        Args:
            query_text: Text query
            limit: Maximum number of results
            offset: Pagination offset
            filters: Additional filters to apply

        Returns:
            List of search results
        """
        try:
            if self.client is None:
                return []

            # Get the Video collection
            video_collection = self.client.collections.get("Video")

            # Build hybrid query (combines vector search with BM25) for v4.11.3 API
            query = video_collection.query.hybrid(
                query=query_text,
                alpha=0.5,  # Balance between vector and keyword search
                limit=limit,
                offset=offset,
                fusion_type="hybrid",  # Explicitly specify hybrid fusion type
            )

            # Add filters if provided
            if filters:
                query = query.with_where(filters)

            # Execute query
            result = query.objects

            # Format results
            return [
                {
                    "mongodb_id": obj.properties.get("mongodb_id"),
                    "title": obj.properties.get("title"),
                    "description": obj.properties.get("description"),
                    "tags": obj.properties.get("tags", []),
                    "_additional": {"id": obj.uuid, "distance": obj.metadata.distance},
                }
                for obj in result
            ]

        except Exception as e:
            logger.error(f"Error searching by text: {e}")
            return []

    def search_by_color(
        self, hex_color: str, limit: int = 20, offset: int = 0, filters: Dict = None
    ) -> List[Dict]:
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
            if self.client is None:
                return []

            # Convert hex to RGB vector [0-1]
            r = int(hex_color[1:3], 16) / 255
            g = int(hex_color[3:5], 16) / 255
            b = int(hex_color[5:7], 16) / 255

            vector = [r, g, b]

            # Get the ColorSearch collection
            color_collection = self.client.collections.get("ColorSearch")

            # Build query
            query = color_collection.query.near_vector(
                vector=vector, limit=limit, offset=offset
            )

            # Add filters if provided
            if filters:
                query = query.with_where(filters)

            # Execute query
            color_results = query.objects

            # Get video details for each color result
            results = []
            video_collection = self.client.collections.get("Video")

            for color in color_results:
                video_id = color.properties.get("video_id")
                mongodb_id = color.properties.get("mongodb_id")

                if mongodb_id:
                    try:
                        # Find videos by MongoDB ID (more reliable)
                        filter_query = {
                            "path": ["mongodb_id"],
                            "operator": "Equal",
                            "valueText": mongodb_id,
                        }

                        # Execute query with filter in v4.11.3 API
                        videos = video_collection.query.fetch_objects(
                            filters=filter_query
                        )

                        if videos:
                            video = videos[0]
                            results.append(
                                {
                                    "mongodb_id": video.properties.get("mongodb_id"),
                                    "title": video.properties.get("title"),
                                    "description": video.properties.get("description"),
                                    "tags": video.properties.get("tags", []),
                                    "color": color.properties.get("color"),
                                    "percentage": color.properties.get("percentage"),
                                    "_additional": {
                                        "id": video.uuid,
                                        "distance": color.metadata.distance,
                                    },
                                }
                            )
                    except Exception as ve:
                        logger.warning(
                            f"Error fetching video for color {color.uuid}: {ve}"
                        )

            return results

        except Exception as e:
            logger.error(f"Error searching by color: {e}")
            return []

    def ping(self) -> bool:
        """
        Check if Weaviate is responsive.

        Returns:
            bool: True if Weaviate is ready, False otherwise
        """
        try:
            if self.client is None:
                return False
            return self.client.is_ready()
        except Exception:
            return False


# For importing in other modules
weaviate_client = WeaviateClient()

# For CLI initialization
if __name__ == "__main__":
    import django
    import os

    # Set up Django environment
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pixelseek.settings")
    django.setup()

    # Initialize Weaviate schema using context manager
    with WeaviateClient() as client:
        success = client.initialize()

        if success:
            print(
                f"✅ Weaviate collections initialized successfully with {client.vectorizer_module} vectorizer using "
                f"model {client.model_name}"
            )
        else:
            print("❌ Failed to initialize Weaviate collections")
