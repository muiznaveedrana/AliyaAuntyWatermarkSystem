"""
Text watermark processing module
"""
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Optional, Dict, Any
import re

from .watermark_engine import WatermarkEngine
from models.schemas import TextWatermarkConfig, WatermarkPosition


class TextWatermark:
    """Handles text watermark creation and application"""

    def __init__(self, engine: Optional[WatermarkEngine] = None):
        self.engine = engine or WatermarkEngine()

    def create_text_watermark(
        self,
        config: TextWatermarkConfig,
        image_size: Tuple[int, int],
        exif_data: Optional[Dict[str, Any]] = None
    ) -> Image.Image:
        """
        Create a text watermark image

        Args:
            config: Text watermark configuration
            image_size: Size of the target image (for scaling)
            exif_data: EXIF data for placeholder replacement

        Returns:
            RGBA image with the text watermark
        """
        # Process text with EXIF placeholders if enabled
        text = config.text
        if config.use_exif and exif_data:
            text = self._replace_exif_placeholders(text, exif_data)

        # Calculate font size based on scaling
        font_size = config.font_size
        if config.scale_with_image:
            # Scale font size relative to image dimensions
            base_dimension = min(image_size)
            font_size = max(12, int(base_dimension * config.scale_factor))

        # Get font
        font = self.engine.get_font(config.font_family, font_size)

        # Create a temporary image to measure text
        temp_img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)

        # Get text bounding box
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Add padding for effects
        padding = 20
        if config.shadow:
            padding += config.shadow_offset * 2
        if config.outline:
            padding += config.outline_width * 2

        # Create watermark image with padding
        wm_width = text_width + padding * 2
        wm_height = text_height + padding * 2
        watermark = Image.new('RGBA', (wm_width, wm_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark)

        # Calculate text position within watermark
        text_x = padding
        text_y = padding

        # Calculate opacity value
        opacity = int(config.opacity * 255)

        # Draw shadow if enabled
        if config.shadow:
            shadow_color = (*config.shadow_color, int(opacity * 0.5))
            shadow_x = text_x + config.shadow_offset
            shadow_y = text_y + config.shadow_offset
            draw.text(
                (shadow_x, shadow_y),
                text,
                font=font,
                fill=shadow_color
            )

        # Draw outline if enabled
        if config.outline:
            outline_color = (*config.outline_color, opacity)
            for dx in range(-config.outline_width, config.outline_width + 1):
                for dy in range(-config.outline_width, config.outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text(
                            (text_x + dx, text_y + dy),
                            text,
                            font=font,
                            fill=outline_color
                        )

        # Draw main text
        text_color = (*config.font_color, opacity)
        draw.text((text_x, text_y), text, font=font, fill=text_color)

        # Apply rotation if specified
        if config.rotation != 0:
            watermark = self.engine.rotate_image(watermark, config.rotation)

        return watermark

    def apply_text_watermark(
        self,
        image: Image.Image,
        config: TextWatermarkConfig,
        exif_data: Optional[Dict[str, Any]] = None
    ) -> Image.Image:
        """
        Apply text watermark to an image

        Args:
            image: Base image to watermark
            config: Text watermark configuration
            exif_data: EXIF data for placeholder replacement

        Returns:
            Watermarked image
        """
        # Ensure RGBA mode
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        # Create the text watermark
        watermark = self.create_text_watermark(config, image.size, exif_data)

        # Handle tiling mode
        if config.position == WatermarkPosition.TILE:
            watermark_layer = self.engine.create_tile_pattern(
                watermark,
                image.size,
                config.tile_spacing
            )
            return Image.alpha_composite(image, watermark_layer)

        # Calculate position for single watermark
        position = self.engine.calculate_position(
            image.size,
            watermark.size,
            config.position.value,
            config.margin,
            config.custom_x,
            config.custom_y
        )

        # Composite watermark onto image
        return self.engine.composite_watermark(image, watermark, position)

    def _replace_exif_placeholders(self, text: str, exif_data: Dict[str, Any]) -> str:
        """
        Replace EXIF placeholders in text

        Supported placeholders:
        - {date} - Date taken
        - {time} - Time taken
        - {camera} - Camera model
        - {lens} - Lens model
        - {aperture} - Aperture value
        - {shutter} - Shutter speed
        - {iso} - ISO value
        - {focal_length} - Focal length
        - {copyright} - Copyright info
        - {artist} - Artist name
        - {filename} - Original filename
        """
        placeholders = {
            '{date}': exif_data.get('date', ''),
            '{time}': exif_data.get('time', ''),
            '{datetime}': exif_data.get('datetime', ''),
            '{camera}': exif_data.get('camera_model', ''),
            '{make}': exif_data.get('camera_make', ''),
            '{lens}': exif_data.get('lens_model', ''),
            '{aperture}': exif_data.get('aperture', ''),
            '{shutter}': exif_data.get('shutter_speed', ''),
            '{iso}': exif_data.get('iso', ''),
            '{focal_length}': exif_data.get('focal_length', ''),
            '{copyright}': exif_data.get('copyright', ''),
            '{artist}': exif_data.get('artist', ''),
            '{filename}': exif_data.get('filename', ''),
            '{width}': str(exif_data.get('width', '')),
            '{height}': str(exif_data.get('height', '')),
        }

        result = text
        for placeholder, value in placeholders.items():
            result = result.replace(placeholder, str(value))

        return result

    def create_copyright_watermark(
        self,
        name: str,
        year: Optional[int] = None,
        position: WatermarkPosition = WatermarkPosition.BOTTOM_RIGHT,
        **kwargs
    ) -> TextWatermarkConfig:
        """
        Create a standard copyright watermark configuration

        Args:
            name: Copyright holder name
            year: Copyright year (optional)
            position: Watermark position
            **kwargs: Additional TextWatermarkConfig parameters

        Returns:
            TextWatermarkConfig for copyright watermark
        """
        from datetime import datetime

        if year is None:
            year = datetime.now().year

        copyright_text = f"© {year} {name}"

        default_config = {
            'text': copyright_text,
            'font_size': 24,
            'font_color': (255, 255, 255),
            'opacity': 0.7,
            'position': position,
            'shadow': True,
            'shadow_color': (0, 0, 0),
            'shadow_offset': 2,
        }

        default_config.update(kwargs)
        return TextWatermarkConfig(**default_config)
