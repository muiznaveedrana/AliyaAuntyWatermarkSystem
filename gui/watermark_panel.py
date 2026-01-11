"""
Watermark settings panel - configure text and image watermarks
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QLineEdit, QSpinBox, QDoubleSpinBox,
    QComboBox, QCheckBox, QPushButton, QColorDialog,
    QFileDialog, QGroupBox, QFormLayout, QSlider,
    QScrollArea, QFrame
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor
from pathlib import Path
from typing import Tuple

from models.schemas import (
    BatchProcessConfig, TextWatermarkConfig, ImageWatermarkConfig,
    WatermarkPosition, OutputFormat
)


class ColorButton(QPushButton):
    """Button that shows and allows selecting a color"""
    color_changed = pyqtSignal(tuple)

    def __init__(self, color: Tuple[int, int, int] = (255, 255, 255)):
        super().__init__()
        self._color = color
        self.setFixedSize(60, 30)
        self.update_style()
        self.clicked.connect(self.pick_color)

    def update_style(self):
        r, g, b = self._color
        # Calculate contrasting text color
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        text_color = "#000" if brightness > 128 else "#fff"
        self.setStyleSheet(
            f"background-color: rgb({r},{g},{b}); "
            f"border: 2px solid #555; "
            f"border-radius: 6px; "
            f"color: {text_color};"
        )
        self.setText("")

    def pick_color(self):
        color = QColorDialog.getColor(QColor(*self._color), self)
        if color.isValid():
            self._color = (color.red(), color.green(), color.blue())
            self.update_style()
            self.color_changed.emit(self._color)

    def get_color(self) -> Tuple[int, int, int]:
        return self._color

    def set_color(self, color: Tuple[int, int, int]):
        self._color = color
        self.update_style()


class TextWatermarkWidget(QWidget):
    """Widget for configuring text watermarks"""
    settings_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Enable checkbox
        self.enabled_check = QCheckBox("Enable Text Watermark")
        self.enabled_check.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.enabled_check.stateChanged.connect(self.settings_changed.emit)
        layout.addWidget(self.enabled_check)

        # Settings group
        self.settings_group = QGroupBox("Text Settings")
        form = QFormLayout(self.settings_group)

        # Text input
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Enter watermark text...")
        self.text_input.textChanged.connect(self.settings_changed.emit)
        form.addRow("Text:", self.text_input)

        # Font size
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 500)
        self.font_size.setValue(36)
        self.font_size.valueChanged.connect(self.settings_changed.emit)
        form.addRow("Font Size:", self.font_size)

        # Font color
        color_layout = QHBoxLayout()
        self.font_color = ColorButton((255, 255, 255))
        self.font_color.color_changed.connect(lambda: self.settings_changed.emit())
        color_layout.addWidget(self.font_color)
        color_layout.addStretch()
        form.addRow("Color:", color_layout)

        # Opacity
        opacity_layout = QHBoxLayout()
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(50)
        self.opacity_slider.valueChanged.connect(self.settings_changed.emit)
        self.opacity_label = QLabel("80%")
        self.opacity_slider.setValue(80)
        self.opacity_slider.valueChanged.connect(
            lambda v: self.opacity_label.setText(f"{v}%")
        )
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_label)
        form.addRow("Opacity:", opacity_layout)

        # Position
        self.position_combo = QComboBox()
        positions = [
            ("Top Left", "top-left"),
            ("Top Center", "top-center"),
            ("Top Right", "top-right"),
            ("Middle Left", "middle-left"),
            ("Center", "center"),
            ("Middle Right", "middle-right"),
            ("Bottom Left", "bottom-left"),
            ("Bottom Center", "bottom-center"),
            ("Bottom Right", "bottom-right"),
            ("Tile", "tile"),
        ]
        for name, value in positions:
            self.position_combo.addItem(name, value)
        self.position_combo.setCurrentIndex(8)  # Bottom Right
        self.position_combo.currentIndexChanged.connect(self.settings_changed.emit)
        form.addRow("Position:", self.position_combo)

        # Margin
        self.margin = QSpinBox()
        self.margin.setRange(0, 500)
        self.margin.setValue(20)
        self.margin.valueChanged.connect(self.settings_changed.emit)
        form.addRow("Margin:", self.margin)

        # Rotation
        self.rotation = QSpinBox()
        self.rotation.setRange(-360, 360)
        self.rotation.setValue(0)
        self.rotation.valueChanged.connect(self.settings_changed.emit)
        form.addRow("Rotation:", self.rotation)

        # Shadow
        self.shadow_check = QCheckBox("Drop Shadow")
        self.shadow_check.stateChanged.connect(self.settings_changed.emit)
        form.addRow("", self.shadow_check)

        # Scale with image
        self.scale_check = QCheckBox("Scale with Image")
        self.scale_check.setChecked(True)
        self.scale_check.stateChanged.connect(self.settings_changed.emit)
        form.addRow("", self.scale_check)

        layout.addWidget(self.settings_group)
        layout.addStretch()

    def is_enabled(self) -> bool:
        return self.enabled_check.isChecked()

    def get_config(self) -> TextWatermarkConfig:
        position_value = self.position_combo.currentData()
        return TextWatermarkConfig(
            text=self.text_input.text() or "Watermark",
            font_size=self.font_size.value(),
            font_color=self.font_color.get_color(),
            opacity=self.opacity_slider.value() / 100.0,
            position=WatermarkPosition(position_value),
            margin=self.margin.value(),
            rotation=self.rotation.value(),
            shadow=self.shadow_check.isChecked(),
            scale_with_image=self.scale_check.isChecked(),
        )

    def load_config(self, config: TextWatermarkConfig):
        self.enabled_check.setChecked(True)
        self.text_input.setText(config.text)
        self.font_size.setValue(config.font_size)
        self.font_color.set_color(config.font_color)
        self.opacity_slider.setValue(int(config.opacity * 100))
        index = self.position_combo.findData(config.position.value)
        if index >= 0:
            self.position_combo.setCurrentIndex(index)
        self.margin.setValue(config.margin)
        self.rotation.setValue(int(config.rotation))
        self.shadow_check.setChecked(config.shadow)
        self.scale_check.setChecked(config.scale_with_image)


class ImageWatermarkWidget(QWidget):
    """Widget for configuring image/logo watermarks"""
    settings_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.logo_path = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Enable checkbox
        self.enabled_check = QCheckBox("Enable Image Watermark")
        self.enabled_check.stateChanged.connect(self.settings_changed.emit)
        layout.addWidget(self.enabled_check)

        # Settings group
        self.settings_group = QGroupBox("Image Settings")
        form = QFormLayout(self.settings_group)

        # Logo file
        logo_layout = QHBoxLayout()
        self.logo_label = QLabel("No logo selected")
        self.logo_label.setStyleSheet("color: #888;")
        logo_layout.addWidget(self.logo_label, 1)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_logo)
        logo_layout.addWidget(browse_btn)
        form.addRow("Logo:", logo_layout)

        # Opacity
        opacity_layout = QHBoxLayout()
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(50)
        self.opacity_slider.valueChanged.connect(self.settings_changed.emit)
        self.opacity_label = QLabel("50%")
        self.opacity_slider.valueChanged.connect(
            lambda v: self.opacity_label.setText(f"{v}%")
        )
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_label)
        form.addRow("Opacity:", opacity_layout)

        # Scale
        scale_layout = QHBoxLayout()
        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setRange(1, 100)
        self.scale_slider.setValue(15)
        self.scale_slider.valueChanged.connect(self.settings_changed.emit)
        self.scale_label = QLabel("15%")
        self.scale_slider.valueChanged.connect(
            lambda v: self.scale_label.setText(f"{v}%")
        )
        scale_layout.addWidget(self.scale_slider)
        scale_layout.addWidget(self.scale_label)
        form.addRow("Scale:", scale_layout)

        # Position
        self.position_combo = QComboBox()
        positions = [
            ("Top Left", "top-left"),
            ("Top Center", "top-center"),
            ("Top Right", "top-right"),
            ("Middle Left", "middle-left"),
            ("Center", "center"),
            ("Middle Right", "middle-right"),
            ("Bottom Left", "bottom-left"),
            ("Bottom Center", "bottom-center"),
            ("Bottom Right", "bottom-right"),
            ("Tile", "tile"),
        ]
        for name, value in positions:
            self.position_combo.addItem(name, value)
        self.position_combo.setCurrentIndex(8)  # Bottom Right
        self.position_combo.currentIndexChanged.connect(self.settings_changed.emit)
        form.addRow("Position:", self.position_combo)

        # Margin
        self.margin = QSpinBox()
        self.margin.setRange(0, 500)
        self.margin.setValue(20)
        self.margin.valueChanged.connect(self.settings_changed.emit)
        form.addRow("Margin:", self.margin)

        # Rotation
        self.rotation = QSpinBox()
        self.rotation.setRange(-360, 360)
        self.rotation.setValue(0)
        self.rotation.valueChanged.connect(self.settings_changed.emit)
        form.addRow("Rotation:", self.rotation)

        # Grayscale
        self.grayscale_check = QCheckBox("Convert to Grayscale")
        self.grayscale_check.stateChanged.connect(self.settings_changed.emit)
        form.addRow("", self.grayscale_check)

        layout.addWidget(self.settings_group)
        layout.addStretch()

    def browse_logo(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Logo Image",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp);;All Files (*)"
        )
        if file:
            self.logo_path = Path(file)
            self.logo_label.setText(self.logo_path.name)
            self.logo_label.setStyleSheet("")
            self.settings_changed.emit()

    def is_enabled(self) -> bool:
        return self.enabled_check.isChecked() and self.logo_path is not None

    def get_config(self) -> ImageWatermarkConfig:
        position_value = self.position_combo.currentData()
        return ImageWatermarkConfig(
            logo_path=str(self.logo_path) if self.logo_path else None,
            opacity=self.opacity_slider.value() / 100.0,
            scale=self.scale_slider.value() / 100.0,
            position=WatermarkPosition(position_value),
            margin=self.margin.value(),
            rotation=self.rotation.value(),
            grayscale=self.grayscale_check.isChecked(),
        )

    def load_config(self, config: ImageWatermarkConfig):
        self.enabled_check.setChecked(True)
        if config.logo_path:
            self.logo_path = Path(config.logo_path)
            self.logo_label.setText(self.logo_path.name)
            self.logo_label.setStyleSheet("")
        self.opacity_slider.setValue(int(config.opacity * 100))
        self.scale_slider.setValue(int(config.scale * 100))
        index = self.position_combo.findData(config.position.value)
        if index >= 0:
            self.position_combo.setCurrentIndex(index)
        self.margin.setValue(config.margin)
        self.rotation.setValue(int(config.rotation))
        self.grayscale_check.setChecked(config.grayscale)


class OutputSettingsWidget(QWidget):
    """Widget for configuring output settings"""
    settings_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Output settings group
        group = QGroupBox("Output Settings")
        form = QFormLayout(group)

        # Format
        self.format_combo = QComboBox()
        self.format_combo.addItem("JPEG", "JPEG")
        self.format_combo.addItem("PNG", "PNG")
        self.format_combo.addItem("WebP", "WEBP")
        self.format_combo.currentIndexChanged.connect(self.settings_changed.emit)
        form.addRow("Format:", self.format_combo)

        # Quality
        quality_layout = QHBoxLayout()
        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(90)
        self.quality_slider.valueChanged.connect(self.settings_changed.emit)
        self.quality_label = QLabel("90%")
        self.quality_slider.valueChanged.connect(
            lambda v: self.quality_label.setText(f"{v}%")
        )
        quality_layout.addWidget(self.quality_slider)
        quality_layout.addWidget(self.quality_label)
        form.addRow("Quality:", quality_layout)

        # Filename prefix
        self.prefix_input = QLineEdit()
        self.prefix_input.setPlaceholderText("e.g., wm_")
        form.addRow("Prefix:", self.prefix_input)

        # Filename suffix
        self.suffix_input = QLineEdit()
        self.suffix_input.setText("_watermarked")
        form.addRow("Suffix:", self.suffix_input)

        # Preserve EXIF
        self.exif_check = QCheckBox("Preserve EXIF Data")
        self.exif_check.setChecked(True)
        form.addRow("", self.exif_check)

        layout.addWidget(group)
        layout.addStretch()

    def get_format(self) -> OutputFormat:
        return OutputFormat(self.format_combo.currentData())

    def get_quality(self) -> int:
        return self.quality_slider.value()

    def get_prefix(self) -> str:
        return self.prefix_input.text()

    def get_suffix(self) -> str:
        return self.suffix_input.text()

    def preserve_exif(self) -> bool:
        return self.exif_check.isChecked()


class WatermarkPanel(QWidget):
    """Main watermark settings panel with tabs"""
    settings_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Header
        header = QLabel("Watermark Settings")
        header.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header)

        # Tab widget
        self.tabs = QTabWidget()

        # Text watermark tab
        self.text_widget = TextWatermarkWidget()
        self.text_widget.settings_changed.connect(self.settings_changed.emit)
        self.tabs.addTab(self.text_widget, "Text")

        # Image watermark tab
        self.image_widget = ImageWatermarkWidget()
        self.image_widget.settings_changed.connect(self.settings_changed.emit)
        self.tabs.addTab(self.image_widget, "Image/Logo")

        # Output settings tab
        self.output_widget = OutputSettingsWidget()
        self.output_widget.settings_changed.connect(self.settings_changed.emit)
        self.tabs.addTab(self.output_widget, "Output")

        layout.addWidget(self.tabs)

    def get_config(self) -> BatchProcessConfig:
        """Get current configuration"""
        text_watermarks = []
        image_watermarks = []

        if self.text_widget.is_enabled():
            text_watermarks.append(self.text_widget.get_config())

        if self.image_widget.is_enabled():
            image_watermarks.append(self.image_widget.get_config())

        return BatchProcessConfig(
            text_watermarks=text_watermarks,
            image_watermarks=image_watermarks,
            output_format=self.output_widget.get_format(),
            output_quality=self.output_widget.get_quality(),
            prefix=self.output_widget.get_prefix(),
            suffix=self.output_widget.get_suffix(),
            preserve_exif=self.output_widget.preserve_exif(),
        )

    def load_config(self, config: BatchProcessConfig):
        """Load configuration into widgets"""
        if config.text_watermarks:
            self.text_widget.load_config(config.text_watermarks[0])

        if config.image_watermarks:
            self.image_widget.load_config(config.image_watermarks[0])
