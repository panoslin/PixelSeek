import logging
import os
import tempfile
from io import BytesIO
from pathlib import Path

import cv2
import numpy as np
from django.conf import settings
from PIL import Image
# Import PySceneDetect
from scenedetect import (
    VideoManager,
    SceneManager,
    StatsManager,
)
from scenedetect.detectors import (
    ContentDetector,
    ThresholdDetector,
)

logger = logging.getLogger(__name__)


def extract_keyframes(video_path, output_dir=None, max_frames=10, method='content'):
    """
    Extract keyframes from a video file.
    
    Args:
        video_path: Path to the video file
        output_dir: Directory to save keyframe images (if None, creates a temp dir)
        max_frames: Maximum number of keyframes to extract
        method: Method for keyframe extraction ('uniform', 'content', 'threshold')
        
    Returns:
        List of dictionaries with keyframe info: 
        {
            'path': str, 
            'timestamp': float, 
            'index': int
        }
    """
    if not os.path.exists(video_path):
        logger.error(f"Video file not found: {video_path}")
        return []

    # Create output directory if not provided
    if not output_dir:
        output_dir = tempfile.mkdtemp()
    elif not os.path.exists(output_dir):
        os.makedirs(output_dir)

    video_filename = os.path.basename(video_path)
    base_name = os.path.splitext(video_filename)[0]

    try:
        if method == 'uniform':
            return extract_uniform_keyframes(video_path, output_dir, base_name, max_frames)
        elif method in ['content', 'threshold']:
            return extract_pyscenedetect_keyframes(video_path, output_dir, base_name, max_frames, method)
        else:
            logger.warning(f"Unsupported keyframe extraction method: {method}. Using 'content' instead.")
            return extract_pyscenedetect_keyframes(video_path, output_dir, base_name, max_frames, 'content')

    except Exception as e:
        logger.error(f"Error extracting keyframes from {video_path}: {e}")
        return []


def extract_uniform_keyframes(video_path, output_dir, base_name, max_frames):
    """Extract keyframes at uniform intervals throughout the video."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Could not open video: {video_path}")
        return []

    # Get video properties
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    if total_frames <= 0 or fps <= 0:
        logger.error(f"Invalid video properties: total_frames={total_frames}, fps={fps}")
        cap.release()
        return []

    # Calculate frame interval
    interval = max(1, total_frames // max_frames)

    keyframes = []

    for i in range(max_frames):
        frame_pos = min(i * interval, total_frames - 1)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
        ret, frame = cap.read()

        if not ret:
            break

        timestamp = frame_pos / fps
        frame_filename = f"{base_name}_frame_{i:03d}_{timestamp:.2f}.jpg"
        frame_path = os.path.join(output_dir, frame_filename)

        # Save frame as image
        cv2.imwrite(frame_path, frame)

        keyframes.append({
            'path':      frame_path,
            'timestamp': timestamp,
            'index':     i
        })

    cap.release()
    return keyframes


def extract_pyscenedetect_keyframes(video_path, output_dir, base_name, max_frames, method='content'):
    """
    Extract keyframes using PySceneDetect.
    
    Args:
        video_path: Path to the video file
        output_dir: Directory to save keyframe images
        base_name: Base name for the output files
        max_frames: Maximum number of keyframes to extract
        method: Detection method ('content' or 'threshold')
        
    Returns:
        List of dictionaries with keyframe info
    """
    # Create VideoManager and SceneManager
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager(StatsManager())

    # Add detector based on method
    if method == 'content':
        # Content detector is more accurate for most videos
        # Adjust threshold as needed (lower values detect more subtle scene changes)
        scene_manager.add_detector(ContentDetector(threshold=30))
    else:
        # Threshold detector is better for videos with abrupt changes in brightness
        scene_manager.add_detector(ThresholdDetector(threshold=15))

    # Start video manager and perform scene detection
    video_manager.set_downscale_factor()
    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)

    # Get scene list
    scene_list = scene_manager.get_scene_list()

    # Limit number of scenes if needed
    if len(scene_list) > max_frames:
        # Keep the first frame of each scene, prioritizing the start, end, and evenly sampling the middle
        scene_list = sample_scenes(scene_list, max_frames)

    # Extract frame from the beginning of each scene
    keyframes = []

    # Get video FPS for timestamp calculation
    fps = video_manager.get_framerate()

    # Use SceneDetect's save_images to extract keyframes
    # First, create a list of frames we want to extract
    frames_to_extract = [scene[0] for scene in scene_list]

    # Save keyframes
    for i, frame_num in enumerate(frames_to_extract):
        # Seek to frame
        video_manager.seek(frame_num)

        # Get frame
        ret, frame = video_manager.retrieve()
        if not ret:
            continue

        # Calculate timestamp
        timestamp = frame_num / fps

        # Create filename and path
        frame_filename = f"{base_name}_scene_{i:03d}_{timestamp:.2f}.jpg"
        frame_path = os.path.join(output_dir, frame_filename)

        # Save frame
        cv2.imwrite(frame_path, frame)

        # Add to keyframes list
        keyframes.append({
            'path':      frame_path,
            'timestamp': timestamp,
            'index':     i
        })

    # Release video manager
    video_manager.release()

    return keyframes


def sample_scenes(scene_list, max_frames):
    """
    Sample scenes to limit to max_frames.
    Always include the first and last scene, and evenly distribute the rest.
    """
    if len(scene_list) <= max_frames:
        return scene_list

    # Always include first and last scene
    first_scene = scene_list[0]
    last_scene = scene_list[-1]

    # Evenly sample the rest
    middle_scenes = []
    if max_frames > 2:
        remaining_scenes = scene_list[1:-1]
        step = max(1, len(remaining_scenes) // (max_frames - 2))

        for i in range(0, len(remaining_scenes), step):
            if len(middle_scenes) < max_frames - 2:
                middle_scenes.append(remaining_scenes[i])

    return [first_scene] + middle_scenes + [last_scene]


def image_to_bytes(image_path):
    """
    Convert an image file to byte data for Weaviate.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Binary data of the image
    """
    try:
        with Image.open(image_path) as img:
            # Resize if image is too large (Weaviate has limits)
            max_dim = 1024
            if img.width > max_dim or img.height > max_dim:
                img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Save to bytes
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=85)
            return buffer.getvalue()

    except Exception as e:
        logger.error(f"Error converting image to bytes: {e}")
        return None


def extract_dominant_colors(image_path, num_colors=5):
    """
    Extract dominant colors from an image.
    
    Args:
        image_path: Path to the image file
        num_colors: Number of dominant colors to extract
        
    Returns:
        List of dictionaries: {'color': hex_color, 'percentage': float}
    """
    try:
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Reshape the image data
        pixels = img.reshape(-1, 3).astype(np.float32)

        # Apply K-means clustering
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
        _, labels, centers = cv2.kmeans(pixels, num_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

        # Count labels to find percentages
        unique_labels, counts = np.unique(labels, return_counts=True)
        total_pixels = pixels.shape[0]

        # Convert to hex colors and percentages
        colors = []
        for i, center in enumerate(centers):
            r, g, b = int(center[0]), int(center[1]), int(center[2])
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            percentage = counts[i] / total_pixels

            colors.append({
                'color':      hex_color,
                'percentage': percentage
            })

        # Sort by percentage (descending)
        colors.sort(key=lambda x: x['percentage'], reverse=True)

        return colors

    except Exception as e:
        logger.error(f"Error extracting dominant colors: {e}")
        return []


def create_media_directories():
    """Create necessary media directories for video processing."""
    media_root = settings.MEDIA_ROOT
    video_upload_dir = os.path.join(media_root, 'videos')
    thumbnail_dir = os.path.join(media_root, 'thumbnails')
    keyframe_dir = os.path.join(media_root, 'keyframes')

    for directory in [media_root, video_upload_dir, thumbnail_dir, keyframe_dir]:
        Path(directory).mkdir(parents=True, exist_ok=True)

    return {
        'media_root':   media_root,
        'video_upload': video_upload_dir,
        'thumbnails':   thumbnail_dir,
        'keyframes':    keyframe_dir
    }
