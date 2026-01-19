"""
Tests for the watermark engine (core functionality)
"""
import pytest
from PIL import Image
from pathlib import Path

from core.watermark_engine import WatermarkEngine
from core.text_watermark import TextWatermark
from core.image_watermark import ImageWatermark
from core.batch_processor import BatchProcessor
from models.schemas import (
    TextWatermarkConfig,
    ImageWatermarkConfig,
    BatchProcessConfig,
    WatermarkPosition,
    OutputFormat,
)


class TestWatermarkEngine:
    """Test the core watermark engine"""

    def test_load_image(self, sample_image):
        """Test loading an image"""
        engine = WatermarkEngine()
        img = engine.load_image(sample_image)

        assert img is not None
        assert img.size == (800, 600)

    def test_load_invalid_image(self, tmp_path):
        """Test loading an invalid file"""
        invalid_file = tmp_path / "invalid.txt"
        invalid_file.write_text("not an image")

        engine = WatermarkEngine()
        with pytest.raises(Exception):
            engine.load_image(invalid_file)

    def test_save_image_jpeg(self, sample_image, output_folder):
        """Test saving image as JPEG"""
        engine = WatermarkEngine()
        img = engine.load_image(sample_image)

        output_path = output_folder / "output.jpg"
        engine.save_image(img, output_path, quality=85)

        assert output_path.exists()

    def test_save_image_png(self, sample_image, output_folder):
        """Test saving image as PNG"""
        engine = WatermarkEngine()
        img = engine.load_image(sample_image)

        output_path = output_folder / "output.png"
        engine.save_image(img, output_path, quality=95)

        assert output_path.exists()


class TestTextWatermark:
    """Test text watermark functionality"""

    def test_create_text_watermark(self, sample_image):
        """Test creating a text watermark"""
        engine = WatermarkEngine()
        text_wm = TextWatermark(engine)

        config = TextWatermarkConfig(
            text="Test Watermark",
            font_size=48,
            font_color=(255, 255, 255),
            opacity=0.8,
            position=WatermarkPosition.BOTTOM_RIGHT,
            margin=20
        )

        watermark = text_wm.create_text_watermark(config, (800, 600), {})

        assert watermark is not None
        assert watermark.mode == 'RGBA'

    def test_apply_text_watermark(self, sample_image):
        """Test applying text watermark to image"""
        engine = WatermarkEngine()
        text_wm = TextWatermark(engine)
        img = engine.load_image(sample_image)

        config = TextWatermarkConfig(
            text="Copyright 2024",
            font_size=36,
            font_color=(255, 255, 255),
            opacity=0.5,
            position=WatermarkPosition.CENTER,
            margin=10
        )

        result = text_wm.apply_text_watermark(img, config, {})

        assert result is not None
        assert result.size == img.size

    def test_text_watermark_positions(self, sample_image):
        """Test all 9 watermark positions"""
        engine = WatermarkEngine()
        text_wm = TextWatermark(engine)
        img = engine.load_image(sample_image)

        positions = [
            WatermarkPosition.TOP_LEFT,
            WatermarkPosition.TOP_CENTER,
            WatermarkPosition.TOP_RIGHT,
            WatermarkPosition.MIDDLE_LEFT,
            WatermarkPosition.CENTER,
            WatermarkPosition.MIDDLE_RIGHT,
            WatermarkPosition.BOTTOM_LEFT,
            WatermarkPosition.BOTTOM_CENTER,
            WatermarkPosition.BOTTOM_RIGHT,
        ]

        for pos in positions:
            config = TextWatermarkConfig(
                text="Test",
                font_size=24,
                position=pos,
                margin=10
            )
            result = text_wm.apply_text_watermark(img, config, {})
            assert result is not None, f"Failed for position {pos}"

    def test_text_watermark_with_rotation(self, sample_image):
        """Test text watermark with rotation"""
        engine = WatermarkEngine()
        text_wm = TextWatermark(engine)
        img = engine.load_image(sample_image)

        config = TextWatermarkConfig(
            text="Rotated",
            font_size=36,
            rotation=45,
            position=WatermarkPosition.CENTER
        )

        result = text_wm.apply_text_watermark(img, config, {})
        assert result is not None


class TestImageWatermark:
    """Test image/logo watermark functionality"""

    def test_load_logo(self, sample_logo):
        """Test loading a logo"""
        engine = WatermarkEngine()
        img_wm = ImageWatermark(engine)

        config = ImageWatermarkConfig(logo_path=str(sample_logo))
        logo = img_wm.load_logo(config)

        assert logo is not None
        assert logo.mode == 'RGBA'

    def test_apply_image_watermark(self, sample_image, sample_logo):
        """Test applying image watermark"""
        engine = WatermarkEngine()
        img_wm = ImageWatermark(engine)
        img = engine.load_image(sample_image)

        config = ImageWatermarkConfig(
            logo_path=str(sample_logo),
            scale=0.2,
            opacity=0.8,
            position=WatermarkPosition.BOTTOM_RIGHT,
            margin=20
        )

        result = img_wm.apply_image_watermark(img, config)

        assert result is not None
        assert result.size == img.size

    def test_image_watermark_scaling(self, sample_image, sample_logo):
        """Test image watermark scaling"""
        engine = WatermarkEngine()
        img_wm = ImageWatermark(engine)
        img = engine.load_image(sample_image)

        # Test different scales
        for scale in [0.1, 0.25, 0.5]:
            config = ImageWatermarkConfig(
                logo_path=str(sample_logo),
                scale=scale,
                position=WatermarkPosition.CENTER
            )
            result = img_wm.apply_image_watermark(img, config)
            assert result is not None


class TestBatchProcessor:
    """Test batch processing functionality"""

    def test_process_single_image(self, sample_image, output_folder):
        """Test processing a single image"""
        processor = BatchProcessor()

        config = BatchProcessConfig(
            text_watermarks=[
                TextWatermarkConfig(
                    text="Batch Test",
                    font_size=36,
                    position=WatermarkPosition.BOTTOM_RIGHT
                )
            ],
            output_format=OutputFormat.PNG,
            output_quality=95,
            suffix='_watermarked'
        )

        result = processor.process_batch([sample_image], config, output_folder)

        assert result.total_images == 1
        assert result.successful == 1
        assert result.failed == 0

        # Check output file exists
        output_file = output_folder / f"{sample_image.stem}_watermarked.png"
        assert output_file.exists()

    def test_process_multiple_images(self, sample_images, output_folder):
        """Test processing multiple images"""
        processor = BatchProcessor()

        config = BatchProcessConfig(
            text_watermarks=[
                TextWatermarkConfig(
                    text="Batch",
                    font_size=24,
                    position=WatermarkPosition.CENTER
                )
            ],
            output_format=OutputFormat.PNG,
            suffix='_wm'
        )

        result = processor.process_batch(sample_images, config, output_folder)

        assert result.total_images == 5
        assert result.successful == 5
        assert result.failed == 0

    def test_process_with_text_and_image_watermark(self, sample_image, sample_logo, output_folder):
        """Test processing with both text and image watermarks"""
        processor = BatchProcessor()

        config = BatchProcessConfig(
            text_watermarks=[
                TextWatermarkConfig(
                    text="Text",
                    font_size=24,
                    position=WatermarkPosition.TOP_LEFT
                )
            ],
            image_watermarks=[
                ImageWatermarkConfig(
                    logo_path=str(sample_logo),
                    scale=0.15,
                    position=WatermarkPosition.BOTTOM_RIGHT
                )
            ],
            output_format=OutputFormat.PNG
        )

        result = processor.process_batch([sample_image], config, output_folder)

        assert result.successful == 1

    def test_progress_callback(self, sample_images, output_folder):
        """Test progress callback is called"""
        processor = BatchProcessor()
        progress_calls = []

        def on_progress(current, total, filename):
            progress_calls.append((current, total, filename))

        processor.set_progress_callback(on_progress)

        config = BatchProcessConfig(
            text_watermarks=[
                TextWatermarkConfig(text="Test", font_size=24)
            ]
        )

        processor.process_batch(sample_images, config, output_folder)

        assert len(progress_calls) == 5
        assert progress_calls[-1][0] == 5  # Final progress should be 5
