import os
import logging
from datetime import datetime
import uuid
import shutil
from django.conf import settings

from .models import Video, VectorReference
from .utils import (
    extract_keyframes, 
    image_to_bytes, 
    extract_dominant_colors,
    create_media_directories
)
from .weaviate_schema import weaviate_client

logger = logging.getLogger(__name__)

class VideoProcessingService:
    """
    Service for processing uploaded videos, extracting keyframes, 
    and integrating with vector databases.
    """
    
    def __init__(self):
        """Initialize the service with necessary directories."""
        self.directories = create_media_directories()
        
    def process_video(self, video_id):
        """
        Process a video by extracting keyframes and storing them in Weaviate.
        
        Args:
            video_id: MongoDB ObjectId of the video
            
        Returns:
            bool: Success status
        """
        try:
            # Get the video from MongoDB
            video = Video.objects.get(id=video_id)
            
            # Update status
            video.status = 'extracting_keyframes'
            video.save()
            
            # Extract keyframes
            keyframes_dir = os.path.join(
                self.directories['keyframes'],
                str(video.id)
            )
            
            # Create keyframes directory for this video
            if not os.path.exists(keyframes_dir):
                os.makedirs(keyframes_dir)
            
            # Extract keyframes using PySceneDetect's content detector
            keyframes = extract_keyframes(
                video.file_path,
                keyframes_dir,
                max_frames=15,  # Adjust as needed
                method='content'  # Using content-based detection from PySceneDetect
            )
            
            if not keyframes:
                video.status = 'error'
                video.error_message = "Failed to extract keyframes"
                video.save()
                return False
            
            # Save keyframe paths to video model
            keyframe_paths = [kf['path'] for kf in keyframes]
            video.keyframes = [os.path.basename(path) for path in keyframe_paths]
            video.keyframe_count = len(keyframes)
            video.keyframes_extracted = True
            video.save()
            
            # Update status
            video.status = 'indexing_vectors'
            video.save()
            
            # Store in Weaviate
            success = self._store_in_weaviate(video, keyframes, keyframes_dir)
            
            if success:
                video.status = 'ready'
            else:
                video.status = 'error'
                video.error_message = "Failed to store in vector database"
            
            video.save()
            return success
            
        except Video.DoesNotExist:
            logger.error(f"Video with id {video_id} does not exist")
            return False
        except Exception as e:
            logger.error(f"Error processing video {video_id}: {e}")
            
            # Update video status to error
            try:
                video = Video.objects.get(id=video_id)
                video.status = 'error'
                video.error_message = str(e)
                video.save()
            except:
                pass
                
            return False
    
    def _store_in_weaviate(self, video, keyframes, keyframes_dir):
        """
        Store video and keyframes in Weaviate.
        
        Args:
            video: Video model instance
            keyframes: List of keyframe dictionaries
            keyframes_dir: Directory containing keyframe images
            
        Returns:
            bool: Success status
        """
        try:
            # First, store the video thumbnail in Weaviate
            thumbnail_data = image_to_bytes(video.thumbnail_path)
            
            if not thumbnail_data:
                logger.error(f"Could not read thumbnail for video {video.id}")
                return False
            
            # Extract colors from thumbnail for color search
            colors = extract_dominant_colors(video.thumbnail_path)
            color_hex_values = [c['color'] for c in colors]
            
            # Add video to Weaviate
            video_uuid = weaviate_client.add_video(
                mongodb_id=str(video.id),
                thumbnail_data=thumbnail_data,
                title=video.title,
                description=video.description,
                tags=video.tags,
                colors=color_hex_values,
                owner_id=str(video.owner.id),
                access_level=video.access_level
            )
            
            if not video_uuid:
                logger.error(f"Failed to add video {video.id} to Weaviate")
                return False
            
            # Store Weaviate ID in video model
            video.vector_id = video_uuid
            video.save()
            
            # Create VectorReference
            VectorReference(
                content_type='video',
                object_id=str(video.id),
                weaviate_id=video_uuid,
                vector_type='visual'
            ).save()
            
            # Process keyframes
            keyframe_vector_ids = []
            
            for i, keyframe in enumerate(keyframes):
                # Load keyframe image
                keyframe_path = keyframe['path']
                keyframe_data = image_to_bytes(keyframe_path)
                
                if not keyframe_data:
                    logger.warning(f"Could not read keyframe {i} for video {video.id}")
                    continue
                
                # Add keyframe to Weaviate
                keyframe_uuid = weaviate_client.add_keyframe(
                    mongodb_id=str(video.id),
                    video_weaviate_id=video_uuid,
                    keyframe_data=keyframe_data,
                    timestamp=keyframe['timestamp'],
                    index=keyframe['index'],
                    access_level=video.access_level
                )
                
                if not keyframe_uuid:
                    logger.warning(f"Failed to add keyframe {i} to Weaviate for video {video.id}")
                    continue
                
                keyframe_vector_ids.append(keyframe_uuid)
                
                # Create VectorReference for keyframe
                VectorReference(
                    content_type='keyframe',
                    object_id=str(video.id),
                    weaviate_id=keyframe_uuid,
                    vector_type='visual',
                    parent_video_id=str(video.id),
                    keyframe_index=keyframe['index'],
                    timestamp=keyframe['timestamp']
                ).save()
            
            # Update video with keyframe vector IDs
            video.keyframe_vector_ids = keyframe_vector_ids
            video.save()
            
            return True
            
        except Exception as e:
            logger.error(f"Error storing video {video.id} in Weaviate: {e}")
            return False

# Singleton instance for service
video_processing_service = VideoProcessingService() 