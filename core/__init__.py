"""
Core watermarking module
"""
from .watermark_engine import WatermarkEngine
from .text_watermark import TextWatermark
from .image_watermark import ImageWatermark
from .video_processor import VideoProcessor
from .batch_processor import BatchProcessor
from .exif_handler import ExifHandler

__all__ = [
    "WatermarkEngine",
    "TextWatermark",
    "ImageWatermark",
    "VideoProcessor",
    "BatchProcessor",
    "ExifHandler",
]
