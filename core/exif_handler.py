"""
EXIF data extraction and handling module
"""
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from typing import Dict, Any, Optional, Union
from pathlib import Path
import io


class ExifHandler:
    """Handles EXIF data extraction from images"""

    def __init__(self):
        # Mapping of EXIF tag names to friendly names
        self.tag_mapping = {
            'DateTimeOriginal': 'datetime',
            'DateTime': 'datetime',
            'Make': 'camera_make',
            'Model': 'camera_model',
            'LensModel': 'lens_model',
            'FNumber': 'aperture',
            'ExposureTime': 'shutter_speed',
            'ISOSpeedRatings': 'iso',
            'FocalLength': 'focal_length',
            'Copyright': 'copyright',
            'Artist': 'artist',
            'ImageWidth': 'width',
            'ImageLength': 'height',
            'ExifImageWidth': 'width',
            'ExifImageHeight': 'height',
            'Orientation': 'orientation',
            'Software': 'software',
            'GPSInfo': 'gps_info',
        }

    def extract_exif(
        self,
        source: Union[str, Path, Image.Image, bytes, io.BytesIO],
        include_raw: bool = False
    ) -> Dict[str, Any]:
        """
        Extract EXIF data from an image

        Args:
            source: Image file path, PIL Image, bytes, or BytesIO
            include_raw: Include raw EXIF data in result

        Returns:
            Dictionary of EXIF data
        """
        # Load image if necessary
        if isinstance(source, Image.Image):
            img = source
        elif isinstance(source, (str, Path)):
            img = Image.open(source)
        elif isinstance(source, bytes):
            img = Image.open(io.BytesIO(source))
        elif isinstance(source, io.BytesIO):
            img = Image.open(source)
        else:
            raise TypeError(f"Unsupported source type: {type(source)}")

        result = {
            'filename': '',
            'width': img.width,
            'height': img.height,
            'format': img.format,
            'mode': img.mode,
        }

        # Get filename if available
        if isinstance(source, (str, Path)):
            result['filename'] = Path(source).name

        # Extract EXIF data
        exif_data = img.getexif()
        if not exif_data:
            return result

        raw_exif = {}

        for tag_id, value in exif_data.items():
            tag_name = TAGS.get(tag_id, str(tag_id))
            raw_exif[tag_name] = value

            # Map to friendly name
            if tag_name in self.tag_mapping:
                friendly_name = self.tag_mapping[tag_name]
                processed_value = self._process_exif_value(tag_name, value)
                result[friendly_name] = processed_value

        # Process datetime into date and time separately
        if 'datetime' in result:
            date_time = str(result['datetime'])
            if ' ' in date_time:
                date_part, time_part = date_time.split(' ', 1)
                result['date'] = date_part.replace(':', '-')
                result['time'] = time_part
            else:
                result['date'] = date_time.replace(':', '-')
                result['time'] = ''

        if include_raw:
            result['_raw'] = raw_exif

        return result

    def _process_exif_value(self, tag_name: str, value: Any) -> str:
        """
        Process EXIF value to human-readable format

        Args:
            tag_name: EXIF tag name
            value: Raw EXIF value

        Returns:
            Processed string value
        """
        try:
            if tag_name == 'FNumber':
                # Aperture value
                if hasattr(value, 'numerator') and hasattr(value, 'denominator'):
                    f_value = value.numerator / value.denominator
                    return f"f/{f_value:.1f}"
                return f"f/{value}"

            elif tag_name == 'ExposureTime':
                # Shutter speed
                if hasattr(value, 'numerator') and hasattr(value, 'denominator'):
                    if value.numerator == 1:
                        return f"1/{value.denominator}s"
                    else:
                        return f"{value.numerator}/{value.denominator}s"
                return f"{value}s"

            elif tag_name == 'FocalLength':
                # Focal length
                if hasattr(value, 'numerator') and hasattr(value, 'denominator'):
                    focal = value.numerator / value.denominator
                    return f"{focal:.0f}mm"
                return f"{value}mm"

            elif tag_name == 'ISOSpeedRatings':
                # ISO
                if isinstance(value, (list, tuple)):
                    return f"ISO {value[0]}"
                return f"ISO {value}"

            elif tag_name in ('DateTimeOriginal', 'DateTime'):
                # Date/Time
                return str(value)

            else:
                return str(value)

        except Exception:
            return str(value)

    def get_exif_bytes(self, image: Image.Image) -> Optional[bytes]:
        """
        Get raw EXIF bytes from image for preservation

        Args:
            image: PIL Image

        Returns:
            EXIF bytes or None
        """
        try:
            exif = image.getexif()
            if exif:
                return exif.tobytes()
        except Exception:
            pass
        return None

    def get_camera_info(self, source: Union[str, Path, Image.Image]) -> str:
        """
        Get formatted camera info string

        Args:
            source: Image source

        Returns:
            Formatted camera info string
        """
        exif = self.extract_exif(source)

        parts = []

        if exif.get('camera_make') and exif.get('camera_model'):
            model = exif['camera_model']
            make = exif['camera_make']
            # Avoid duplication if model contains make
            if make.lower() not in model.lower():
                parts.append(f"{make} {model}")
            else:
                parts.append(model)
        elif exif.get('camera_model'):
            parts.append(exif['camera_model'])

        if exif.get('lens_model'):
            parts.append(exif['lens_model'])

        return ' | '.join(parts) if parts else 'Unknown Camera'

    def get_exposure_info(self, source: Union[str, Path, Image.Image]) -> str:
        """
        Get formatted exposure info string

        Args:
            source: Image source

        Returns:
            Formatted exposure info string
        """
        exif = self.extract_exif(source)

        parts = []

        if exif.get('aperture'):
            parts.append(exif['aperture'])
        if exif.get('shutter_speed'):
            parts.append(exif['shutter_speed'])
        if exif.get('iso'):
            parts.append(exif['iso'])
        if exif.get('focal_length'):
            parts.append(exif['focal_length'])

        return ' | '.join(parts) if parts else ''

    def create_exif_watermark_text(
        self,
        source: Union[str, Path, Image.Image],
        template: str = "{camera} | {aperture} {shutter} {iso} {focal_length}"
    ) -> str:
        """
        Create watermark text from EXIF data using template

        Args:
            source: Image source
            template: Template string with placeholders

        Returns:
            Formatted watermark text
        """
        exif = self.extract_exif(source)

        # Replace placeholders
        result = template
        for key, value in exif.items():
            placeholder = "{" + key + "}"
            if placeholder in result:
                result = result.replace(placeholder, str(value) if value else '')

        # Clean up multiple spaces and separators
        result = ' '.join(result.split())
        result = result.replace('| |', '|')
        result = result.strip(' |')

        return result
