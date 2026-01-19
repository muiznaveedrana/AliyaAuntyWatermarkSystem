"""
Preview panel - shows image/video preview with watermark applied
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea,
    QSizePolicy, QSlider, QHBoxLayout
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QImage
from PIL import Image
from pathlib import Path
import io

from models.schemas import BatchProcessConfig
from core.text_watermark import TextWatermark
from core.image_watermark import ImageWatermark
from core.watermark_engine import WatermarkEngine
from core.video_processor import VideoProcessor
from config import SUPPORTED_VIDEO_FORMATS


class PreviewPanel(QWidget):
    """Panel for previewing watermarked images and videos"""

    def __init__(self):
        super().__init__()
        self.engine = WatermarkEngine()
        self.text_watermark = TextWatermark(self.engine)
        self.image_watermark = ImageWatermark(self.engine)
        self.video_processor = VideoProcessor()
        self.current_image: Image.Image = None
        self.current_path: Path = None
        self.current_config: BatchProcessConfig = None
        self.watermarked_image: Image.Image = None
        self.current_pixmap: QPixmap = None
        self.is_video: bool = False
        self.video_duration: float = 0
        self.setup_ui()

    def _is_video_file(self, path: Path) -> bool:
        """Check if file is a video"""
        return path.suffix.lower() in SUPPORTED_VIDEO_FORMATS

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Header
        header = QLabel("Preview")
        header.setProperty("header", True)
        layout.addWidget(header)

        # Scroll area for image
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet(
            "background-color: #1a1a1a; "
            "color: #666; "
            "font-size: 14px;"
        )
        self.image_label.setText("Select an image or video to preview")
        self.image_label.setMinimumSize(300, 300)

        self.scroll_area.setWidget(self.image_label)
        layout.addWidget(self.scroll_area, 1)

        # Video scrubber (hidden by default)
        self.scrubber_widget = QWidget()
        scrubber_layout = QHBoxLayout(self.scrubber_widget)
        scrubber_layout.setContentsMargins(0, 0, 0, 0)

        self.time_label = QLabel("0:00")
        self.time_label.setStyleSheet("color: #888; font-size: 11px; min-width: 40px;")
        scrubber_layout.addWidget(self.time_label)

        self.video_slider = QSlider(Qt.Orientation.Horizontal)
        self.video_slider.setMinimum(0)
        self.video_slider.setMaximum(100)
        self.video_slider.setValue(0)
        self.video_slider.valueChanged.connect(self._on_slider_change)
        scrubber_layout.addWidget(self.video_slider, 1)

        self.duration_label = QLabel("0:00")
        self.duration_label.setStyleSheet("color: #888; font-size: 11px; min-width: 40px;")
        scrubber_layout.addWidget(self.duration_label)

        self.scrubber_widget.setVisible(False)
        layout.addWidget(self.scrubber_widget)

        # Info label
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: #888; font-size: 12px; padding: 4px;")
        layout.addWidget(self.info_label)

    def load_image(self, path: Path):
        """Load an image or video for preview"""
        try:
            self.current_path = path
            self.is_video = self._is_video_file(path)

            if self.is_video:
                self._load_video(path)
            else:
                self._load_image(path)

        except Exception as e:
            self.image_label.setText(f"Error loading file:\n{str(e)}")
            self.current_image = None
            self.current_pixmap = None
            self.info_label.setText("")
            self.scrubber_widget.setVisible(False)

    def _load_image(self, path: Path):
        """Load an image file"""
        self.current_image = self.engine.load_image(path)
        self.watermarked_image = None
        self._update_pixmap(self.current_image)
        self._display_scaled()

        # Update info
        w, h = self.current_image.size
        size_kb = path.stat().st_size / 1024
        self.info_label.setText(f"{w} x {h} px | {size_kb:.1f} KB | {path.name}")

        # Hide video scrubber
        self.scrubber_widget.setVisible(False)

    def _load_video(self, path: Path):
        """Load a video file and show first frame"""
        # Get video info
        video_info = self.video_processor.get_video_info(path)
        if not video_info:
            self.image_label.setText("Error: Could not read video file")
            return

        self.video_duration = video_info.get('duration', 0)

        # Extract first frame
        frame = self.video_processor.extract_frame(path, 0)
        if frame is None:
            self.image_label.setText("Error: Could not extract video frame")
            return

        self.current_image = frame
        self.watermarked_image = None
        self._update_pixmap(self.current_image)
        self._display_scaled()

        # Update info
        w, h = video_info['width'], video_info['height']
        fps = video_info.get('fps', 0)
        size_mb = path.stat().st_size / (1024 * 1024)
        duration_str = self._format_time(self.video_duration)
        self.info_label.setText(
            f"[VIDEO] {w} x {h} px | {fps:.1f} fps | {duration_str} | {size_mb:.1f} MB | {path.name}"
        )

        # Show and configure video scrubber
        self.scrubber_widget.setVisible(True)
        self.video_slider.setValue(0)
        self.time_label.setText("0:00")
        self.duration_label.setText(duration_str)

    def _format_time(self, seconds: float) -> str:
        """Format seconds as mm:ss"""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}:{secs:02d}"

    def _on_slider_change(self, value: int):
        """Handle video slider change - extract new frame"""
        if not self.is_video or not self.current_path or self.video_duration <= 0:
            return

        # Calculate time from slider position
        time_sec = (value / 100.0) * self.video_duration
        self.time_label.setText(self._format_time(time_sec))

        # Extract frame at this time
        frame = self.video_processor.extract_frame(self.current_path, time_sec)
        if frame:
            self.current_image = frame
            self.watermarked_image = None

            # Re-apply watermark if config exists
            if self.current_config:
                self.apply_watermark_preview(self.current_config)
            else:
                self._update_pixmap(self.current_image)
                self._display_scaled()

    def _update_pixmap(self, pil_image: Image.Image):
        """Convert PIL image to QPixmap and store it"""
        if pil_image.mode != 'RGBA':
            pil_image = pil_image.convert('RGBA')

        # Get data
        data = pil_image.tobytes("raw", "RGBA")
        qimage = QImage(
            data,
            pil_image.width,
            pil_image.height,
            pil_image.width * 4,  # bytes per line
            QImage.Format.Format_RGBA8888
        )
        self.current_pixmap = QPixmap.fromImage(qimage)

    def _display_scaled(self):
        """Display the current pixmap scaled to fit the viewport"""
        if self.current_pixmap is None:
            return

        # Use scroll area viewport size for consistent scaling
        viewport_size = self.scroll_area.viewport().size()
        # Subtract a bit for padding
        available_size = QSize(viewport_size.width() - 10, viewport_size.height() - 10)

        scaled = self.current_pixmap.scaled(
            available_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.image_label.setPixmap(scaled)

    def apply_watermark_preview(self, config: BatchProcessConfig):
        """Apply watermark to current image for preview"""
        self.current_config = config

        if self.current_image is None:
            return

        try:
            # Work with a copy
            preview_image = self.current_image.copy()

            # Apply text watermarks
            for text_config in config.text_watermarks:
                preview_image = self.text_watermark.apply_text_watermark(
                    preview_image,
                    text_config,
                    {'filename': self.current_path.name if self.current_path else ''}
                )

            # Apply image watermarks
            for img_config in config.image_watermarks:
                if img_config.logo_path:
                    preview_image = self.image_watermark.apply_image_watermark(
                        preview_image,
                        img_config
                    )

            self.watermarked_image = preview_image
            self._update_pixmap(preview_image)
            self._display_scaled()

        except Exception as e:
            # If watermark fails, just show original
            self.watermarked_image = self.current_image
            self._update_pixmap(self.current_image)
            self._display_scaled()
            print(f"Preview error: {e}")

    def clear(self):
        """Clear the preview"""
        self.current_image = None
        self.current_path = None
        self.current_pixmap = None
        self.watermarked_image = None
        self.is_video = False
        self.video_duration = 0
        self.image_label.clear()
        self.image_label.setText("Select an image or video to preview")
        self.info_label.setText("")
        self.scrubber_widget.setVisible(False)

    def resizeEvent(self, event):
        """Handle resize to update preview"""
        super().resizeEvent(event)
        if self.current_pixmap:
            self._display_scaled()
