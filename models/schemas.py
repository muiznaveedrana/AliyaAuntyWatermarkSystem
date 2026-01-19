"""
Pydantic models for data validation and serialization
"""
from enum import Enum
from typing import Optional, List, Tuple
from pydantic import BaseModel, Field, field_validator
from pathlib import Path


class WatermarkPosition(str, Enum):
    """9-point positioning system for watermarks"""
    TOP_LEFT = "top-left"
    TOP_CENTER = "top-center"
    TOP_RIGHT = "top-right"
    MIDDLE_LEFT = "middle-left"
    CENTER = "center"
    MIDDLE_RIGHT = "middle-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_CENTER = "bottom-center"
    BOTTOM_RIGHT = "bottom-right"
    CUSTOM = "custom"  # For exact x, y coordinates
    TILE = "tile"  # Repeat across entire image


class OutputFormat(str, Enum):
    """Supported output formats for images"""
    JPEG = "JPEG"
    PNG = "PNG"
    WEBP = "WEBP"


class VideoOutputFormat(str, Enum):
    """Supported output formats for videos"""
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    WEBM = "webm"


class VideoCodec(str, Enum):
    """Supported video codecs"""
    H264 = "libx264"
    H265 = "libx265"
    VP9 = "libvpx-vp9"
    MPEG4 = "mpeg4"


class VideoPreset(str, Enum):
    """Video encoding presets (speed vs quality tradeoff)"""
    ULTRAFAST = "ultrafast"
    FAST = "fast"
    MEDIUM = "medium"
    SLOW = "slow"


class TextWatermarkConfig(BaseModel):
    """Configuration for text watermarks"""
    text: str = Field(..., min_length=1, max_length=500, description="Watermark text")
    font_family: str = Field(default="arial", description="Font family name")
    font_size: int = Field(default=36, ge=8, le=500, description="Font size in pixels")
    font_color: Tuple[int, int, int] = Field(
        default=(255, 255, 255),
        description="RGB color tuple"
    )
    opacity: float = Field(default=0.5, ge=0.0, le=1.0, description="Opacity (0-1)")
    position: WatermarkPosition = Field(
        default=WatermarkPosition.BOTTOM_RIGHT,
        description="Watermark position"
    )
    custom_x: Optional[int] = Field(default=None, description="Custom X coordinate")
    custom_y: Optional[int] = Field(default=None, description="Custom Y coordinate")
    rotation: float = Field(default=0, ge=-360, le=360, description="Rotation angle in degrees")
    margin: int = Field(default=20, ge=0, le=500, description="Margin from edges")
    shadow: bool = Field(default=False, description="Add drop shadow")
    shadow_color: Tuple[int, int, int] = Field(
        default=(0, 0, 0),
        description="Shadow RGB color"
    )
    shadow_offset: int = Field(default=2, ge=0, le=20, description="Shadow offset in pixels")
    outline: bool = Field(default=False, description="Add text outline")
    outline_color: Tuple[int, int, int] = Field(
        default=(0, 0, 0),
        description="Outline RGB color"
    )
    outline_width: int = Field(default=1, ge=1, le=10, description="Outline width")
    tile_spacing: int = Field(default=100, ge=10, le=500, description="Spacing for tile mode")
    use_exif: bool = Field(default=False, description="Use EXIF data placeholders in text")
    scale_with_image: bool = Field(default=True, description="Scale watermark with image size")
    scale_factor: float = Field(default=0.08, ge=0.01, le=0.5, description="Scale factor relative to image")

    @field_validator('font_color', 'shadow_color', 'outline_color', mode='before')
    @classmethod
    def validate_color(cls, v):
        if isinstance(v, (list, tuple)):
            if len(v) == 3 and all(0 <= c <= 255 for c in v):
                return tuple(v)
        raise ValueError('Color must be RGB tuple with values 0-255')


class ImageWatermarkConfig(BaseModel):
    """Configuration for image/logo watermarks"""
    logo_path: Optional[str] = Field(default=None, description="Path to logo file")
    logo_base64: Optional[str] = Field(default=None, description="Base64 encoded logo")
    opacity: float = Field(default=0.5, ge=0.0, le=1.0, description="Opacity (0-1)")
    position: WatermarkPosition = Field(
        default=WatermarkPosition.BOTTOM_RIGHT,
        description="Watermark position"
    )
    custom_x: Optional[int] = Field(default=None, description="Custom X coordinate")
    custom_y: Optional[int] = Field(default=None, description="Custom Y coordinate")
    rotation: float = Field(default=0, ge=-360, le=360, description="Rotation angle")
    margin: int = Field(default=20, ge=0, le=500, description="Margin from edges")
    scale: float = Field(default=0.15, ge=0.01, le=1.0, description="Scale relative to image")
    maintain_aspect_ratio: bool = Field(default=True, description="Maintain logo aspect ratio")
    tile_spacing: int = Field(default=150, ge=20, le=500, description="Spacing for tile mode")
    grayscale: bool = Field(default=False, description="Convert logo to grayscale")


class VideoProcessConfig(BaseModel):
    """Configuration for video processing"""
    output_format: VideoOutputFormat = Field(
        default=VideoOutputFormat.MP4,
        description="Output video format"
    )
    codec: VideoCodec = Field(
        default=VideoCodec.H264,
        description="Video codec"
    )
    preset: VideoPreset = Field(
        default=VideoPreset.MEDIUM,
        description="Encoding preset (speed vs quality)"
    )
    bitrate: Optional[str] = Field(
        default=None,
        description="Video bitrate (e.g., '5000k', '10M')"
    )
    audio_codec: str = Field(
        default="aac",
        description="Audio codec"
    )
    preserve_audio: bool = Field(
        default=True,
        description="Preserve original audio"
    )


class BatchProcessConfig(BaseModel):
    """Configuration for batch processing"""
    text_watermarks: List[TextWatermarkConfig] = Field(
        default=[],
        description="List of text watermarks to apply"
    )
    image_watermarks: List[ImageWatermarkConfig] = Field(
        default=[],
        description="List of image watermarks to apply"
    )
    # Image output settings
    output_format: OutputFormat = Field(
        default=OutputFormat.JPEG,
        description="Output image format"
    )
    output_quality: int = Field(
        default=90,
        ge=1,
        le=100,
        description="Output quality (1-100)"
    )
    resize_output: bool = Field(default=False, description="Resize output images")
    resize_width: Optional[int] = Field(default=None, ge=1, le=10000, description="Target width")
    resize_height: Optional[int] = Field(default=None, ge=1, le=10000, description="Target height")
    maintain_aspect_ratio: bool = Field(default=True, description="Maintain aspect ratio when resizing")
    prefix: str = Field(default="", max_length=50, description="Output filename prefix")
    suffix: str = Field(default="_watermarked", max_length=50, description="Output filename suffix")
    preserve_exif: bool = Field(default=True, description="Preserve EXIF data in output")
    # Video output settings
    video_config: VideoProcessConfig = Field(
        default_factory=VideoProcessConfig,
        description="Video processing configuration"
    )


class WatermarkProfile(BaseModel):
    """Saved watermark profile/template"""
    name: str = Field(..., min_length=1, max_length=100, description="Profile name")
    description: Optional[str] = Field(default=None, max_length=500, description="Profile description")
    config: BatchProcessConfig = Field(..., description="Batch processing configuration")
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Last update timestamp")


class MediaType(str, Enum):
    """Type of media file"""
    IMAGE = "image"
    VIDEO = "video"


class ProcessingResult(BaseModel):
    """Result of processing a single file"""
    input_file: str = Field(..., description="Input filename")
    output_file: Optional[str] = Field(default=None, description="Output filename")
    success: bool = Field(..., description="Processing success status")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    processing_time_ms: float = Field(default=0, description="Processing time in milliseconds")
    original_size: Optional[Tuple[int, int]] = Field(default=None, description="Original dimensions")
    output_size: Optional[Tuple[int, int]] = Field(default=None, description="Output dimensions")
    media_type: MediaType = Field(default=MediaType.IMAGE, description="Type of media processed")
    duration_seconds: Optional[float] = Field(default=None, description="Video duration in seconds")


class BatchProcessingResult(BaseModel):
    """Result of batch processing"""
    total_files: int = Field(..., description="Total number of files")
    total_images: int = Field(default=0, description="Total number of images")
    total_videos: int = Field(default=0, description="Total number of videos")
    successful: int = Field(default=0, description="Successfully processed count")
    failed: int = Field(default=0, description="Failed count")
    total_time_ms: float = Field(default=0, description="Total processing time")
    results: List[ProcessingResult] = Field(default=[], description="Individual results")
