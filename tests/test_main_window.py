"""
Tests for the main window GUI
"""
import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from pathlib import Path


class TestMainWindow:
    """Test the main application window"""

    def test_window_opens(self, main_window):
        """Test that the main window opens correctly"""
        assert main_window.isVisible()
        assert "Batch Watermark" in main_window.windowTitle()

    def test_window_has_panels(self, main_window):
        """Test that all three panels exist"""
        assert main_window.image_list_panel is not None
        assert main_window.watermark_panel is not None
        assert main_window.preview_panel is not None

    def test_toolbar_exists(self, main_window):
        """Test that toolbar buttons exist"""
        toolbar = main_window.findChild(main_window.__class__.__bases__[0])
        assert main_window.process_btn is not None
        assert main_window.cancel_btn is not None

    def test_initial_state(self, main_window):
        """Test initial window state"""
        # No images loaded
        assert len(main_window.current_images) == 0
        # Process button should be enabled (but will warn if no images)
        assert main_window.process_btn.isEnabled()
        # Cancel button should be disabled
        assert not main_window.cancel_btn.isEnabled()

    def test_add_single_image(self, main_window, sample_image, qtbot, monkeypatch):
        """Test adding a single image"""
        # Mock the file dialog to return our sample image
        monkeypatch.setattr(
            QFileDialog, 'getOpenFileNames',
            lambda *args, **kwargs: ([str(sample_image)], "")
        )

        # Trigger add images
        main_window.add_images()

        # Check image was added
        assert len(main_window.current_images) == 1
        assert main_window.current_images[0] == sample_image

    def test_add_multiple_images(self, main_window, sample_images, qtbot, monkeypatch):
        """Test adding multiple images"""
        # Mock the file dialog
        monkeypatch.setattr(
            QFileDialog, 'getOpenFileNames',
            lambda *args, **kwargs: ([str(p) for p in sample_images], "")
        )

        main_window.add_images()

        assert len(main_window.current_images) == 5

    def test_add_folder(self, main_window, sample_images, qtbot, monkeypatch):
        """Test adding images from a folder"""
        folder = sample_images[0].parent

        monkeypatch.setattr(
            QFileDialog, 'getExistingDirectory',
            lambda *args, **kwargs: str(folder)
        )

        main_window.add_folder()

        assert len(main_window.current_images) == 5

    def test_clear_images(self, main_window, sample_images, qtbot, monkeypatch):
        """Test clearing all images"""
        # First add images
        monkeypatch.setattr(
            QFileDialog, 'getOpenFileNames',
            lambda *args, **kwargs: ([str(p) for p in sample_images], "")
        )
        main_window.add_images()
        assert len(main_window.current_images) == 5

        # Clear images
        main_window.clear_images()
        assert len(main_window.current_images) == 0

    def test_image_count_updates(self, main_window, sample_images, qtbot, monkeypatch):
        """Test that image count label updates"""
        monkeypatch.setattr(
            QFileDialog, 'getOpenFileNames',
            lambda *args, **kwargs: ([str(p) for p in sample_images], "")
        )

        main_window.add_images()

        assert "5" in main_window.count_label.text()

    def test_process_without_images_shows_warning(self, main_window, qtbot, monkeypatch):
        """Test that processing without images shows a warning"""
        warning_shown = []

        def mock_warning(*args, **kwargs):
            warning_shown.append(True)
            return QMessageBox.StandardButton.Ok

        monkeypatch.setattr(QMessageBox, 'warning', mock_warning)

        main_window.start_processing()

        assert len(warning_shown) == 1

    def test_process_without_watermark_shows_warning(self, main_window, sample_image, qtbot, monkeypatch):
        """Test that processing without watermark configured shows warning"""
        # Add an image
        monkeypatch.setattr(
            QFileDialog, 'getOpenFileNames',
            lambda *args, **kwargs: ([str(sample_image)], "")
        )
        main_window.add_images()

        warning_shown = []

        def mock_warning(*args, **kwargs):
            warning_shown.append(True)
            return QMessageBox.StandardButton.Ok

        monkeypatch.setattr(QMessageBox, 'warning', mock_warning)

        # Clear any default watermark text and disable
        main_window.watermark_panel.text_widget.text_input.clear()
        main_window.watermark_panel.text_widget.enabled_check.setChecked(False)

        main_window.start_processing()

        assert len(warning_shown) == 1

    def test_set_output_folder(self, main_window, output_folder, qtbot, monkeypatch):
        """Test setting output folder"""
        monkeypatch.setattr(
            QFileDialog, 'getExistingDirectory',
            lambda *args, **kwargs: str(output_folder)
        )

        main_window.set_output_folder()

        assert main_window.output_folder == output_folder


class TestImageSelection:
    """Test image selection and preview"""

    def test_selecting_image_updates_preview(self, main_window, sample_image, qtbot, monkeypatch):
        """Test that selecting an image updates the preview"""
        # Add image
        monkeypatch.setattr(
            QFileDialog, 'getOpenFileNames',
            lambda *args, **kwargs: ([str(sample_image)], "")
        )
        main_window.add_images()

        # Select the image
        main_window.on_image_selected(sample_image)

        # Preview should have loaded the image
        assert main_window.preview_panel.current_image is not None
        assert main_window.preview_panel.current_path == sample_image
