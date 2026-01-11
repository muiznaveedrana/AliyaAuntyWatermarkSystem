"""
Configuration settings for the Image Batch Watermarking Tool
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Output directories
OUTPUT_FOLDER = BASE_DIR / "output"
PROFILES_FOLDER = BASE_DIR / "profiles"

# Create directories if they don't exist
OUTPUT_FOLDER.mkdir(exist_ok=True)
PROFILES_FOLDER.mkdir(exist_ok=True)

# Supported image formats
SUPPORTED_INPUT_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif', '.webp'}
SUPPORTED_OUTPUT_FORMATS = {'JPEG', 'PNG', 'WEBP'}

# Processing settings
MAX_WORKERS = os.cpu_count() or 4  # Number of threads for batch processing
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB max file size
MAX_BATCH_SIZE = 500  # Maximum images per batch

# Default watermark settings
DEFAULT_OPACITY = 0.5
DEFAULT_POSITION = "bottom-right"
DEFAULT_MARGIN = 20
DEFAULT_FONT_SIZE = 36
DEFAULT_FONT_COLOR = (255, 255, 255, 128)  # White with 50% opacity

# Position mapping (9-point system)
POSITION_MAP = {
    "top-left": (0, 0),
    "top-center": (0.5, 0),
    "top-right": (1, 0),
    "middle-left": (0, 0.5),
    "center": (0.5, 0.5),
    "middle-right": (1, 0.5),
    "bottom-left": (0, 1),
    "bottom-center": (0.5, 1),
    "bottom-right": (1, 1),
}

# Application settings
APP_NAME = "Batch Watermark Tool"
APP_VERSION = "1.0.0"
