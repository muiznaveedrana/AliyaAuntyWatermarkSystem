"""
Preview panel - shows image preview with watermark applied
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea,
    QSizePolicy
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


class PreviewPanel(QWidget):
    """Panel for previewing watermarked images"""

    def __init__(self):
        super().__init__()
        self.engine = WatermarkEngine()
        self.text_watermark = TextWatermark(self.engine)
        self.image_watermark = ImageWatermark(self.engine)
        self.current_image: Image.Image = None
        self.current_path: Path = None
        self.current_config: BatchProcessConfig = None
        self.watermarked_image: Image.Image = None
        self.current_pixmap: QPixmap = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Header
        header = QLabel("Preview")
        header.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header)

        # Scroll area for image
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet(
            "background-color: #2a2a2a; "
            "color: #888; "
        )
        self.image_label.setText("Select an image to preview")

        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setStyleSheet("border: 1px solid #444;")
        layout.addWidget(self.scroll_area)

        # Info label
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(self.info_label)

    def load_image(self, path: Path):
        """Load an image for preview"""
        try:
            self.current_path = path
            self.current_image = self.engine.load_image(path)
            self.watermarked_image = None
            self._update_pixmap(self.current_image)
            self._display_scaled()

            # Update info
            w, h = self.current_image.size
            size_kb = path.stat().st_size / 1024
            self.info_label.setText(f"{w} x {h} px | {size_kb:.1f} KB | {path.name}")

        except Exception as e:
            self.image_label.setText(f"Error loading image:\n{str(e)}")
            self.current_image = None
            self.current_pixmap = None
            self.info_label.setText("")

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
        self.image_label.clear()
        self.image_label.setText("Select an image to preview")
        self.info_label.setText("")

    def resizeEvent(self, event):
        """Handle resize to update preview"""
        super().resizeEvent(event)
        if self.current_pixmap:
            self._display_scaled()
