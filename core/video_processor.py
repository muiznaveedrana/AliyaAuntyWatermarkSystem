"""
Video processing module for watermarking videos
"""
import logging
from pathlib import Path
from typing import Optional, Callable, Dict, Any
import numpy as np
from PIL import Image

from moviepy import VideoFileClip, ImageClip, CompositeVideoClip

from .watermark_engine import WatermarkEngine
from .text_watermark import TextWatermark
from .image_watermark import ImageWatermark
from models.schemas import (
    TextWatermarkConfig,
    ImageWatermarkConfig,
    WatermarkPosition,
)
from config import POSITION_MAP

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Handles video watermarking using moviepy"""

    def __init__(self):
        self.engine = WatermarkEngine()
        self.text_watermark = TextWatermark(self.engine)
        self.image_watermark = ImageWatermark(self.engine)
        self._progress_callback: Optional[Callable[[float], None]] = None

    def set_progress_callback(self, callback: Callable[[float], None]) -> None:
        """Set a callback for progress updates (0.0 to 1.0)"""
        self._progress_callback = callback

    def extract_frame(self, video_path: Path, time_sec: float = 0) -> Optional[Image.Image]:
        """
        Extract a single frame from video for preview

        Args:
            video_path: Path to video file
            time_sec: Time in seconds to extract frame from

        Returns:
            PIL Image of the frame or None if failed
        """
        try:
            clip = VideoFileClip(str(video_path))
            # Ensure time is within video duration
            time_sec = min(time_sec, clip.duration - 0.1)
            time_sec = max(0, time_sec)

            frame = clip.get_frame(time_sec)
            clip.close()

            # Convert numpy array to PIL Image
            return Image.fromarray(frame)
        except Exception as e:
            logger.error(f"Error extracting frame from {video_path}: {e}")
            return None

    def get_video_info(self, video_path: Path) -> Dict[str, Any]:
        """
        Get video metadata

        Args:
            video_path: Path to video file

        Returns:
            Dictionary with video info (duration, fps, size, etc.)
        """
        try:
            clip = VideoFileClip(str(video_path))
            info = {
                'duration': clip.duration,
                'fps': clip.fps,
                'size': clip.size,  # (width, height)
                'width': clip.size[0],
                'height': clip.size[1],
                'has_audio': clip.audio is not None,
            }
            clip.close()
            return info
        except Exception as e:
            logger.error(f"Error getting video info for {video_path}: {e}")
            return {}

    def _create_watermark_frame(
        self,
        video_size: tuple,
        text_watermarks: list,
        image_watermarks: list,
    ) -> Optional[Image.Image]:
        """
        Create a watermark overlay frame to composite onto video

        Args:
            video_size: (width, height) of video
            text_watermarks: List of TextWatermarkConfig
            image_watermarks: List of ImageWatermarkConfig

        Returns:
            PIL Image with transparent background and watermarks
        """
        # Create transparent RGBA image same size as video
        watermark_layer = Image.new('RGBA', video_size, (0, 0, 0, 0))

        # Apply text watermarks
        for text_config in text_watermarks:
            watermark_layer = self.text_watermark.apply_text_watermark(
                watermark_layer,
                text_config,
                {}  # No EXIF data for videos
            )

        # Apply image watermarks
        for img_config in image_watermarks:
            if img_config.logo_path or img_config.logo_base64:
                watermark_layer = self.image_watermark.apply_image_watermark(
                    watermark_layer,
                    img_config
                )

        return watermark_layer

    def process_video(
        self,
        input_path: Path,
        output_path: Path,
        text_watermarks: list,
        image_watermarks: list,
        output_codec: str = 'libx264',
        audio_codec: str = 'aac',
        bitrate: Optional[str] = None,
        fps: Optional[float] = None,
        preset: str = 'medium',
    ) -> bool:
        """
        Apply watermarks to a video

        Args:
            input_path: Path to input video
            output_path: Path for output video
            text_watermarks: List of TextWatermarkConfig
            image_watermarks: List of ImageWatermarkConfig
            output_codec: Video codec (default: libx264)
            audio_codec: Audio codec (default: aac)
            bitrate: Video bitrate (e.g., '5000k')
            fps: Output FPS (None = same as input)
            preset: Encoding preset (ultrafast, fast, medium, slow)

        Returns:
            True if successful, False otherwise
        """
        clip = None
        try:
            # Load video
            clip = VideoFileClip(str(input_path))
            video_size = clip.size  # (width, height)

            # Create watermark overlay
            watermark_image = self._create_watermark_frame(
                video_size,
                text_watermarks,
                image_watermarks
            )

            if watermark_image is None:
                logger.error("Failed to create watermark layer")
                if clip:
                    clip.close()
                return False

            # Convert PIL image to numpy array for moviepy
            watermark_array = np.array(watermark_image)

            # Create an ImageClip from the watermark
            watermark_clip = (
                ImageClip(watermark_array)
                .with_duration(clip.duration)
                .with_position((0, 0))
            )

            # Composite video with watermark overlay
            final_clip = CompositeVideoClip([clip, watermark_clip])

            # Prepare output parameters
            write_params = {
                'codec': output_codec,
                'audio_codec': audio_codec if clip.audio else None,
                'preset': preset,
                'logger': None,  # Suppress moviepy's progress bar
            }

            if bitrate:
                write_params['bitrate'] = bitrate
            if fps:
                write_params['fps'] = fps

            # Progress callback wrapper for moviepy
            if self._progress_callback:
                def progress_logger(t):
                    progress = t / clip.duration if clip.duration > 0 else 0
                    self._progress_callback(min(progress, 1.0))
                write_params['logger'] = 'bar'

            # Write output video
            final_clip.write_videofile(str(output_path), **write_params)

            # Clean up
            final_clip.close()
            clip.close()

            return True

        except Exception as e:
            logger.error(f"Error processing video {input_path}: {e}")
            if clip:
                clip.close()
            return False

    def process_video_frame_by_frame(
        self,
        input_path: Path,
        output_path: Path,
        text_watermarks: list,
        image_watermarks: list,
        output_codec: str = 'libx264',
        audio_codec: str = 'aac',
        bitrate: Optional[str] = None,
        preset: str = 'medium',
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> bool:
        """
        Process video frame by frame - useful for complex watermarks
        that need per-frame adjustment

        Args:
            input_path: Path to input video
            output_path: Path for output video
            text_watermarks: List of TextWatermarkConfig
            image_watermarks: List of ImageWatermarkConfig
            output_codec: Video codec
            audio_codec: Audio codec
            bitrate: Video bitrate
            preset: Encoding preset
            progress_callback: Callback(current_frame, total_frames)

        Returns:
            True if successful, False otherwise
        """
        clip = None
        try:
            clip = VideoFileClip(str(input_path))
            video_size = clip.size
            total_frames = int(clip.duration * clip.fps)

            # Pre-create the watermark layer (same for all frames)
            watermark_image = self._create_watermark_frame(
                video_size,
                text_watermarks,
                image_watermarks
            )

            if watermark_image is None:
                logger.error("Failed to create watermark layer")
                if clip:
                    clip.close()
                return False

            frame_count = [0]  # Use list for closure

            def apply_watermark_to_frame(get_frame, t):
                """Apply watermark to each frame"""
                frame = get_frame(t)
                frame_count[0] += 1

                if progress_callback and frame_count[0] % 30 == 0:  # Update every 30 frames
                    progress_callback(frame_count[0], total_frames)

                # Convert frame to PIL, apply watermark, convert back
                pil_frame = Image.fromarray(frame).convert('RGBA')

                # Composite watermark onto frame
                pil_frame.paste(watermark_image, (0, 0), watermark_image)

                # Convert back to RGB for video output
                return np.array(pil_frame.convert('RGB'))

            # Apply transformation
            processed_clip = clip.transform(apply_watermark_to_frame)

            # Write output
            write_params = {
                'codec': output_codec,
                'audio_codec': audio_codec if clip.audio else None,
                'preset': preset,
                'logger': None,
            }

            if bitrate:
                write_params['bitrate'] = bitrate

            processed_clip.write_videofile(str(output_path), **write_params)

            processed_clip.close()
            clip.close()

            return True

        except Exception as e:
            logger.error(f"Error processing video frame-by-frame {input_path}: {e}")
            if clip:
                clip.close()
            return False
