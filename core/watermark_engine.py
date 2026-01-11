"""
Core watermarking engine - handles image loading, watermark application, and saving
"""
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from pathlib import Path
from typing import Tuple, Optional, List, Union
import io
import base64
import sys

from config import POSITION_MAP, SUPPORTED_INPUT_FORMATS


class WatermarkEngine:
    """Core engine for applying watermarks to images"""

    def __init__(self):
        self.supported_formats = SUPPORTED_INPUT_FORMATS
        self._font_cache = {}

    def load_image(self, source: Union[str, Path, bytes, io.BytesIO]) -> Image.Image:
        """
        Load an image from file path, bytes, or BytesIO

        Args:
            source: File path, bytes, or BytesIO object

        Returns:
            PIL Image object in RGBA mode
        """
        if isinstance(source, (str, Path)):
            path = Path(source)
            if not path.exists():
                raise FileNotFoundError(f"Image file not found: {source}")
            if path.suffix.lower() not in self.supported_formats:
                raise ValueError(f"Unsupported format: {path.suffix}")
            img = Image.open(path)
        elif isinstance(source, bytes):
            img = Image.open(io.BytesIO(source))
        elif isinstance(source, io.BytesIO):
            img = Image.open(source)
        else:
            raise TypeError(f"Unsupported source type: {type(source)}")

        # Convert to RGBA for watermarking
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        return img

    def save_image(
        self,
        image: Image.Image,
        output_path: Union[str, Path],
        format: str = "JPEG",
        quality: int = 90,
        exif_data: Optional[bytes] = None
    ) -> Path:
        """
        Save image to file

        Args:
            image: PIL Image to save
            output_path: Output file path
            format: Output format (JPEG, PNG, WEBP)
            quality: Output quality (1-100)
            exif_data: Optional EXIF data to preserve

        Returns:
            Path to saved file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert RGBA to RGB for JPEG
        if format.upper() == "JPEG" and image.mode == "RGBA":
            # Create white background
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])  # Use alpha channel as mask
            image = background

        save_kwargs = {"quality": quality}
        if format.upper() == "PNG":
            save_kwargs = {"compress_level": 9 - (quality // 12)}  # Map quality to compress level

        if exif_data and format.upper() == "JPEG":
            save_kwargs["exif"] = exif_data

        image.save(output_path, format=format.upper(), **save_kwargs)
        return output_path

    def get_font(self, font_family: str, font_size: int) -> ImageFont.FreeTypeFont:
        """
        Get font object, using cache for performance

        Args:
            font_family: Font family name
            font_size: Font size in pixels

        Returns:
            ImageFont object
        """
        cache_key = (font_family, font_size)
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]

        # Try to load system font
        font_paths = self._get_font_paths(font_family)

        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, font_size)
                self._font_cache[cache_key] = font
                return font
            except (OSError, IOError):
                continue

        # Fallback to default font
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except (OSError, IOError):
            font = ImageFont.load_default()

        self._font_cache[cache_key] = font
        return font

    def _get_font_paths(self, font_family: str) -> List[str]:
        """Get possible font file paths for a font family"""
        font_name = font_family.lower().replace(" ", "")

        # Common font file names
        font_files = [
            f"{font_name}.ttf",
            f"{font_name}.otf",
            f"{font_family}.ttf",
            f"{font_family}.otf",
        ]

        # System font directories
        if sys.platform == "win32":
            font_dirs = [
                "C:/Windows/Fonts/",
                str(Path.home() / "AppData/Local/Microsoft/Windows/Fonts/"),
            ]
        elif sys.platform == "darwin":
            font_dirs = [
                "/Library/Fonts/",
                "/System/Library/Fonts/",
                str(Path.home() / "Library/Fonts/"),
            ]
        else:
            font_dirs = [
                "/usr/share/fonts/",
                "/usr/local/share/fonts/",
                str(Path.home() / ".fonts/"),
                str(Path.home() / ".local/share/fonts/"),
            ]

        paths = []
        for font_dir in font_dirs:
            for font_file in font_files:
                paths.append(str(Path(font_dir) / font_file))

        return paths

    def calculate_position(
        self,
        image_size: Tuple[int, int],
        watermark_size: Tuple[int, int],
        position: str,
        margin: int = 20,
        custom_x: Optional[int] = None,
        custom_y: Optional[int] = None
    ) -> Tuple[int, int]:
        """
        Calculate watermark position on image

        Args:
            image_size: (width, height) of the image
            watermark_size: (width, height) of the watermark
            position: Position name from POSITION_MAP
            margin: Margin from edges
            custom_x: Custom X coordinate (for CUSTOM position)
            custom_y: Custom Y coordinate (for CUSTOM position)

        Returns:
            (x, y) coordinates for watermark placement
        """
        img_w, img_h = image_size
        wm_w, wm_h = watermark_size

        if position == "custom" and custom_x is not None and custom_y is not None:
            return (custom_x, custom_y)

        if position not in POSITION_MAP:
            position = "bottom-right"

        x_factor, y_factor = POSITION_MAP[position]

        # Calculate base position
        if x_factor == 0:
            x = margin
        elif x_factor == 0.5:
            x = (img_w - wm_w) // 2
        else:
            x = img_w - wm_w - margin

        if y_factor == 0:
            y = margin
        elif y_factor == 0.5:
            y = (img_h - wm_h) // 2
        else:
            y = img_h - wm_h - margin

        return (x, y)

    def apply_opacity(self, image: Image.Image, opacity: float) -> Image.Image:
        """
        Apply opacity to an image

        Args:
            image: PIL Image (must be RGBA)
            opacity: Opacity value (0-1)

        Returns:
            Image with adjusted opacity
        """
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        # Split into channels
        r, g, b, a = image.split()

        # Adjust alpha channel
        a = a.point(lambda x: int(x * opacity))

        # Merge back
        return Image.merge('RGBA', (r, g, b, a))

    def rotate_image(self, image: Image.Image, angle: float) -> Image.Image:
        """
        Rotate image by angle, expanding canvas to fit

        Args:
            image: PIL Image to rotate
            angle: Rotation angle in degrees

        Returns:
            Rotated image with transparent background
        """
        if angle == 0:
            return image

        return image.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)

    def create_tile_pattern(
        self,
        watermark: Image.Image,
        image_size: Tuple[int, int],
        spacing: int = 100
    ) -> Image.Image:
        """
        Create a tiled pattern from a watermark

        Args:
            watermark: Watermark image to tile
            image_size: Size of the target image
            spacing: Spacing between tiles

        Returns:
            Tiled watermark layer
        """
        img_w, img_h = image_size
        wm_w, wm_h = watermark.size

        # Create transparent layer for tiling
        tile_layer = Image.new('RGBA', image_size, (0, 0, 0, 0))

        # Calculate step size
        step_x = wm_w + spacing
        step_y = wm_h + spacing

        # Tile the watermark
        y = spacing
        row = 0
        while y < img_h:
            # Offset alternate rows for diagonal pattern
            x_offset = (step_x // 2) if row % 2 else 0
            x = spacing + x_offset

            while x < img_w:
                tile_layer.paste(watermark, (x, y), watermark)
                x += step_x

            y += step_y
            row += 1

        return tile_layer

    def composite_watermark(
        self,
        base_image: Image.Image,
        watermark: Image.Image,
        position: Tuple[int, int]
    ) -> Image.Image:
        """
        Composite watermark onto base image

        Args:
            base_image: Base image (RGBA)
            watermark: Watermark image (RGBA)
            position: (x, y) position for watermark

        Returns:
            Composited image
        """
        # Create a copy to avoid modifying original
        result = base_image.copy()

        # Create a layer for the watermark at the correct position
        watermark_layer = Image.new('RGBA', result.size, (0, 0, 0, 0))
        watermark_layer.paste(watermark, position, watermark)

        # Composite the layers
        result = Image.alpha_composite(result, watermark_layer)

        return result

    def resize_image(
        self,
        image: Image.Image,
        width: Optional[int] = None,
        height: Optional[int] = None,
        maintain_aspect: bool = True
    ) -> Image.Image:
        """
        Resize image

        Args:
            image: Image to resize
            width: Target width
            height: Target height
            maintain_aspect: Maintain aspect ratio

        Returns:
            Resized image
        """
        if width is None and height is None:
            return image

        orig_w, orig_h = image.size

        if maintain_aspect:
            if width and height:
                # Fit within bounds
                ratio = min(width / orig_w, height / orig_h)
                new_size = (int(orig_w * ratio), int(orig_h * ratio))
            elif width:
                ratio = width / orig_w
                new_size = (width, int(orig_h * ratio))
            else:
                ratio = height / orig_h
                new_size = (int(orig_w * ratio), height)
        else:
            new_size = (width or orig_w, height or orig_h)

        return image.resize(new_size, Image.Resampling.LANCZOS)

    def decode_base64_image(self, base64_string: str) -> Image.Image:
        """Decode a base64 string to PIL Image"""
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',', 1)[1]

        image_data = base64.b64decode(base64_string)
        return self.load_image(image_data)
