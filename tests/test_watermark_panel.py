"""
Tests for the watermark settings panel
"""
import pytest
from PyQt6.QtCore import Qt
from models.schemas import WatermarkPosition


class TestWatermarkPanel:
    """Test the watermark settings panel"""

    def test_panel_has_tabs(self, main_window):
        """Test that panel has all tabs"""
        panel = main_window.watermark_panel
        assert panel.tabs is not None
        assert panel.tabs.count() == 3  # Text, Image/Logo, Output

    def test_get_default_config(self, main_window):
        """Test getting default configuration"""
        panel = main_window.watermark_panel
        config = panel.get_config()

        assert config is not None
        assert hasattr(config, 'text_watermarks')
        assert hasattr(config, 'image_watermarks')
        assert hasattr(config, 'output_format')
        assert hasattr(config, 'output_quality')

    def test_text_input_updates_config(self, main_window, qtbot):
        """Test that text input updates configuration"""
        panel = main_window.watermark_panel
        text_widget = panel.text_widget

        # Enable text watermark and set text
        text_widget.enabled_check.setChecked(True)
        text_widget.text_input.setText("My Watermark")
        qtbot.wait(50)

        config = panel.get_config()

        # Check text is in config
        assert len(config.text_watermarks) > 0
        assert config.text_watermarks[0].text == "My Watermark"

    def test_font_size_updates_config(self, main_window, qtbot):
        """Test that font size updates configuration"""
        panel = main_window.watermark_panel
        text_widget = panel.text_widget

        text_widget.enabled_check.setChecked(True)
        text_widget.text_input.setText("Test")
        text_widget.font_size.setValue(72)
        qtbot.wait(50)

        config = panel.get_config()

        assert config.text_watermarks[0].font_size == 72

    def test_opacity_updates_config(self, main_window, qtbot):
        """Test that opacity updates configuration"""
        panel = main_window.watermark_panel
        text_widget = panel.text_widget

        text_widget.enabled_check.setChecked(True)
        text_widget.text_input.setText("Test")
        text_widget.opacity_slider.setValue(50)
        qtbot.wait(50)

        config = panel.get_config()

        # Opacity is stored as 0-1 float, slider is 0-100
        assert config.text_watermarks[0].opacity == 0.5

    def test_position_updates_config(self, main_window, qtbot):
        """Test that position selection updates configuration"""
        panel = main_window.watermark_panel
        text_widget = panel.text_widget

        text_widget.enabled_check.setChecked(True)
        text_widget.text_input.setText("Test")

        # Select a different position (index 4 = CENTER)
        text_widget.position_combo.setCurrentIndex(4)
        qtbot.wait(50)

        config = panel.get_config()

        assert config.text_watermarks[0].position == WatermarkPosition.CENTER

    def test_output_format_options(self, main_window):
        """Test output format options"""
        panel = main_window.watermark_panel
        output_widget = panel.output_widget

        # Check format combo has expected options
        formats = [
            output_widget.format_combo.itemText(i)
            for i in range(output_widget.format_combo.count())
        ]

        assert 'JPEG' in formats or 'jpeg' in [f.lower() for f in formats]
        assert 'PNG' in formats or 'png' in [f.lower() for f in formats]

    def test_quality_slider_range(self, main_window):
        """Test quality slider has correct range"""
        panel = main_window.watermark_panel
        output_widget = panel.output_widget

        assert output_widget.quality_slider.minimum() >= 1
        assert output_widget.quality_slider.maximum() <= 100

    def test_disable_removes_from_config(self, main_window, qtbot):
        """Test that disabling text watermark removes it from config"""
        panel = main_window.watermark_panel
        text_widget = panel.text_widget

        # Enable and set text
        text_widget.enabled_check.setChecked(True)
        text_widget.text_input.setText("Test")
        qtbot.wait(50)

        config = panel.get_config()
        assert len(config.text_watermarks) == 1

        # Disable
        text_widget.enabled_check.setChecked(False)
        qtbot.wait(50)

        config = panel.get_config()
        assert len(config.text_watermarks) == 0


class TestWatermarkPanelSignals:
    """Test watermark panel signals"""

    def test_settings_changed_signal_on_text_change(self, main_window, qtbot):
        """Test that settings_changed signal is emitted on text change"""
        panel = main_window.watermark_panel
        signals_received = []

        panel.settings_changed.connect(lambda: signals_received.append(True))

        panel.text_widget.text_input.setText("New Text")
        qtbot.wait(100)

        assert len(signals_received) > 0

    def test_settings_changed_signal_on_slider_change(self, main_window, qtbot):
        """Test that settings_changed signal is emitted on slider change"""
        panel = main_window.watermark_panel
        signals_received = []

        panel.settings_changed.connect(lambda: signals_received.append(True))

        panel.text_widget.opacity_slider.setValue(75)
        qtbot.wait(100)

        assert len(signals_received) > 0
