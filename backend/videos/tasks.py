import logging

from celery import shared_task

from .services import video_processing_service

logger = logging.getLogger(__name__)


@shared_task(name='videos.extract_keyframes')
def extract_keyframes(video_id):
    """
    Celery task to process a video and extract keyframes.
    
    Args:
        video_id: MongoDB ObjectId of the video to process
        
    Returns:
        bool: Success status
    """
    logger.info(f"Starting keyframe extraction for video {video_id}")

    result = video_processing_service.process_video(video_id)

    if result:
        logger.info(f"Successfully processed video {video_id}")
    else:
        logger.error(f"Failed to process video {video_id}")

    return result
