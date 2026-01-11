"""
Image/Logo watermark processing module
"""
from PIL import Image, ImageEnhance
from typing import Tuple, Optional, Union
from pathlib import Path
import io

from .watermark_engine import WatermarkEngine
from models.schemas import ImageWatermarkConfig, WatermarkPosition


class ImageWatermark:
    """Handles image/logo watermark creation and application"""

    def __init__(self, engine: Optional[WatermarkEngine] = None):
        self.engine = engine or WatermarkEngine()

    def load_logo(self, config: ImageWatermarkConfig) -> Image.Image:
        """
        Load logo from file path or base64 string

        Args:
            config: Image watermark configuration

        Returns:
            PIL Image of the logo in RGBA mode
        """
        if config.logo_base64:
            logo = self.engine.decode_base64_image(config.logo_base64)
        elif config.logo_path:
            logo = self.engine.load_image(config.logo_path)
        else:
            raise ValueError("Either logo_path or logo_base64 must be provided")

        # Ensure RGBA mode
        if logo.mode != 'RGBA':
            logo = logo.convert('RGBA')

        return logo

    def prepare_logo(
        self,
        logo: Image.Image,
        config: ImageWatermarkConfig,
        target_size: Tuple[int, int]
    ) -> Image.Image:
        """
        Prepare logo for watermarking (resize, apply effects)

        Args:
            logo: Logo image
            config: Image watermark configuration
            target_size: Size of the target image

        Returns:
            Prepared logo image
        """
        # Calculate scaled size based on target image
        target_width = int(min(target_size) * config.scale)

        # Resize logo
        if config.maintain_aspect_ratio:
            aspect_ratio = logo.width / logo.height
            new_width = target_width
            new_height = int(new_width / aspect_ratio)
        else:
            new_width = target_width
            new_height = target_width

        logo = logo.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Convert to grayscale if requested
        if config.grayscale:
            logo = self._convert_to_grayscale(logo)

        # Apply opacity
        logo = self.engine.apply_opacity(logo, config.opacity)

        # Apply rotation
        if config.rotation != 0:
            logo = self.engine.rotate_image(logo, config.rotation)

        return logo

    def _convert_to_grayscale(self, image: Image.Image) -> Image.Image:
        """
        Convert image to grayscale while preserving alpha channel

        Args:
            image: RGBA image

        Returns:
            Grayscale RGBA image
        """
        # Split channels
        r, g, b, a = image.split()

        # Convert RGB to grayscale
        grayscale = Image.merge('RGB', (r, g, b)).convert('L')

        # Create grayscale RGB
        grayscale_rgb = Image.merge('RGB', (grayscale, grayscale, grayscale))

        # Add back alpha channel
        grayscale_rgba = grayscale_rgb.convert('RGBA')
        grayscale_rgba.putalpha(a)

        return grayscale_rgba

    def apply_image_watermark(
        self,
        image: Image.Image,
        config: ImageWatermarkConfig
    ) -> Image.Image:
        """
        Apply image/logo watermark to an image

        Args:
            image: Base image to watermark
            config: Image watermark configuration

        Returns:
            Watermarked image
        """
        # Ensure RGBA mode
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        # Load and prepare logo
        logo = self.load_logo(config)
        logo = self.prepare_logo(logo, config, image.size)

        # Handle tiling mode
        if config.position == WatermarkPosition.TILE:
            watermark_layer = self.engine.create_tile_pattern(
                logo,
                image.size,
                config.tile_spacing
            )
            return Image.alpha_composite(image, watermark_layer)

        # Calculate position for single watermark
        position = self.engine.calculate_position(
            image.size,
            logo.size,
            config.position.value,
            config.margin,
            config.custom_x,
            config.custom_y
        )

        # Composite watermark onto image
        return self.engine.composite_watermark(image, logo, position)

    def create_logo_from_text(
        self,
        text: str,
        font_size: int = 48,
        font_color: Tuple[int, int, int] = (255, 255, 255),
        background_color: Optional[Tuple[int, int, int, int]] = None,
        padding: int = 20
    ) -> Image.Image:
        """
        Create a simple logo image from text

        Args:
            text: Text for the logo
            font_size: Font size
            font_color: RGB color tuple
            background_color: Optional RGBA background color
            padding: Padding around text

        Returns:
            Logo image
        """
        from PIL import ImageDraw

        # Get font
        font = self.engine.get_font("arial", font_size)

        # Measure text
        temp_img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Create logo image
        logo_width = text_width + padding * 2
        logo_height = text_height + padding * 2

        if background_color:
            logo = Image.new('RGBA', (logo_width, logo_height), background_color)
        else:
            logo = Image.new('RGBA', (logo_width, logo_height), (0, 0, 0, 0))

        draw = ImageDraw.Draw(logo)
        draw.text(
            (padding, padding),
            text,
            font=font,
            fill=(*font_color, 255)
        )

        return logo

    def add_border_to_logo(
        self,
        logo: Image.Image,
        border_width: int = 2,
        border_color: Tuple[int, int, int, int] = (255, 255, 255, 255)
    ) -> Image.Image:
        """
        Add a border around the logo

        Args:
            logo: Logo image
            border_width: Border width in pixels
            border_color: RGBA border color

        Returns:
            Logo with border
        """
        new_width = logo.width + border_width * 2
        new_height = logo.height + border_width * 2

        bordered = Image.new('RGBA', (new_width, new_height), border_color)
        bordered.paste(logo, (border_width, border_width), logo)

        return bordered
