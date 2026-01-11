"""
Batch processing module with multi-threading support
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional, Callable, Dict, Any
from dataclasses import dataclass
import time
import logging

from PIL import Image

from .watermark_engine import WatermarkEngine
from .text_watermark import TextWatermark
from .image_watermark import ImageWatermark
from .exif_handler import ExifHandler
from models.schemas import (
    BatchProcessConfig,
    ProcessingResult,
    BatchProcessingResult,
    TextWatermarkConfig,
    ImageWatermarkConfig,
)
from config import (
    MAX_WORKERS,
    OUTPUT_FOLDER,
    SUPPORTED_INPUT_FORMATS,
)


logger = logging.getLogger(__name__)


class BatchProcessor:
    """Handles batch processing of images with watermarks"""

    def __init__(
        self,
        max_workers: Optional[int] = None,
        output_folder: Optional[Path] = None
    ):
        self.max_workers = max_workers or MAX_WORKERS
        self.output_folder = output_folder or OUTPUT_FOLDER
        self.engine = WatermarkEngine()
        self.text_watermark = TextWatermark(self.engine)
        self.image_watermark = ImageWatermark(self.engine)
        self.exif_handler = ExifHandler()

        # Progress tracking
        self._progress_callback: Optional[Callable[[int, int, str], None]] = None
        self._cancel_flag = False

    def set_progress_callback(
        self,
        callback: Callable[[int, int, str], None]
    ) -> None:
        """
        Set a callback for progress updates

        Args:
            callback: Function(current, total, filename) called on progress
        """
        self._progress_callback = callback

    def cancel(self) -> None:
        """Cancel ongoing batch processing"""
        self._cancel_flag = True

    def reset(self) -> None:
        """Reset cancel flag for new processing"""
        self._cancel_flag = False

    def process_single_image(
        self,
        input_path: Path,
        config: BatchProcessConfig,
        output_folder: Optional[Path] = None
    ) -> ProcessingResult:
        """
        Process a single image with watermarks

        Args:
            input_path: Path to input image
            config: Batch processing configuration
            output_folder: Optional output folder override

        Returns:
            ProcessingResult with status and details
        """
        start_time = time.time()
        output_folder = output_folder or self.output_folder

        try:
            # Load image
            image = self.engine.load_image(input_path)
            original_size = image.size

            # Extract EXIF data for potential use in watermarks
            exif_data = self.exif_handler.extract_exif(input_path)
            exif_bytes = None

            if config.preserve_exif:
                try:
                    original_img = Image.open(input_path)
                    exif_bytes = self.exif_handler.get_exif_bytes(original_img)
                except Exception:
                    pass

            # Apply all text watermarks
            for text_config in config.text_watermarks:
                image = self.text_watermark.apply_text_watermark(
                    image,
                    text_config,
                    exif_data
                )

            # Apply all image watermarks
            for img_config in config.image_watermarks:
                image = self.image_watermark.apply_image_watermark(
                    image,
                    img_config
                )

            # Resize if requested
            if config.resize_output:
                image = self.engine.resize_image(
                    image,
                    config.resize_width,
                    config.resize_height,
                    config.maintain_aspect_ratio
                )

            # Generate output filename
            output_filename = self._generate_output_filename(
                input_path,
                config.prefix,
                config.suffix,
                config.output_format.value
            )
            output_path = output_folder / output_filename

            # Save image
            self.engine.save_image(
                image,
                output_path,
                config.output_format.value,
                config.output_quality,
                exif_bytes
            )

            processing_time = (time.time() - start_time) * 1000

            return ProcessingResult(
                input_file=input_path.name,
                output_file=output_filename,
                success=True,
                processing_time_ms=processing_time,
                original_size=original_size,
                output_size=image.size
            )

        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            logger.error(f"Error processing {input_path}: {str(e)}")

            return ProcessingResult(
                input_file=input_path.name,
                success=False,
                error=str(e),
                processing_time_ms=processing_time
            )

    def process_batch(
        self,
        input_paths: List[Path],
        config: BatchProcessConfig,
        output_folder: Optional[Path] = None
    ) -> BatchProcessingResult:
        """
        Process multiple images in parallel

        Args:
            input_paths: List of input image paths
            config: Batch processing configuration
            output_folder: Optional output folder override

        Returns:
            BatchProcessingResult with all results
        """
        self.reset()
        start_time = time.time()
        output_folder = output_folder or self.output_folder
        output_folder.mkdir(parents=True, exist_ok=True)

        results: List[ProcessingResult] = []
        successful = 0
        failed = 0

        # Filter valid image files
        valid_paths = [
            p for p in input_paths
            if p.suffix.lower() in SUPPORTED_INPUT_FORMATS
        ]

        total = len(valid_paths)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_path = {
                executor.submit(
                    self.process_single_image,
                    path,
                    config,
                    output_folder
                ): path
                for path in valid_paths
            }

            # Process completed tasks
            for i, future in enumerate(as_completed(future_to_path)):
                if self._cancel_flag:
                    # Cancel remaining futures
                    for f in future_to_path:
                        f.cancel()
                    break

                path = future_to_path[future]

                try:
                    result = future.result()
                    results.append(result)

                    if result.success:
                        successful += 1
                    else:
                        failed += 1

                except Exception as e:
                    logger.error(f"Future error for {path}: {str(e)}")
                    results.append(ProcessingResult(
                        input_file=path.name,
                        success=False,
                        error=str(e)
                    ))
                    failed += 1

                # Report progress
                if self._progress_callback:
                    self._progress_callback(i + 1, total, path.name)

        total_time = (time.time() - start_time) * 1000

        return BatchProcessingResult(
            total_images=total,
            successful=successful,
            failed=failed,
            total_time_ms=total_time,
            results=results
        )

    def process_folder(
        self,
        input_folder: Path,
        config: BatchProcessConfig,
        output_folder: Optional[Path] = None,
        recursive: bool = False
    ) -> BatchProcessingResult:
        """
        Process all images in a folder

        Args:
            input_folder: Path to input folder
            config: Batch processing configuration
            output_folder: Optional output folder override
            recursive: Process subfolders recursively

        Returns:
            BatchProcessingResult with all results
        """
        input_folder = Path(input_folder)

        if not input_folder.exists():
            raise FileNotFoundError(f"Input folder not found: {input_folder}")

        # Collect all image files
        if recursive:
            image_files = []
            for ext in SUPPORTED_INPUT_FORMATS:
                image_files.extend(input_folder.rglob(f"*{ext}"))
                image_files.extend(input_folder.rglob(f"*{ext.upper()}"))
        else:
            image_files = []
            for ext in SUPPORTED_INPUT_FORMATS:
                image_files.extend(input_folder.glob(f"*{ext}"))
                image_files.extend(input_folder.glob(f"*{ext.upper()}"))

        # Remove duplicates and sort
        image_files = sorted(set(image_files))

        return self.process_batch(image_files, config, output_folder)

    def _generate_output_filename(
        self,
        input_path: Path,
        prefix: str,
        suffix: str,
        output_format: str
    ) -> str:
        """
        Generate output filename

        Args:
            input_path: Original input path
            prefix: Filename prefix
            suffix: Filename suffix
            output_format: Output format extension

        Returns:
            Generated filename
        """
        stem = input_path.stem
        ext = self._format_to_extension(output_format)

        return f"{prefix}{stem}{suffix}{ext}"

    def _format_to_extension(self, format: str) -> str:
        """Convert format name to file extension"""
        format_map = {
            'JPEG': '.jpg',
            'PNG': '.png',
            'WEBP': '.webp',
        }
        return format_map.get(format.upper(), '.jpg')

    def estimate_processing_time(
        self,
        num_images: int,
        config: BatchProcessConfig
    ) -> float:
        """
        Estimate processing time in seconds

        Args:
            num_images: Number of images to process
            config: Batch processing configuration

        Returns:
            Estimated time in seconds
        """
        # Base time per image (rough estimate)
        base_time = 0.5  # seconds

        # Add time for each watermark
        watermark_count = len(config.text_watermarks) + len(config.image_watermarks)
        watermark_time = watermark_count * 0.1

        # Adjust for parallel processing
        parallel_factor = min(num_images, self.max_workers)

        time_per_image = base_time + watermark_time
        total_time = (num_images * time_per_image) / parallel_factor

        return total_time
