"""
Pytest configuration and fixtures for GUI testing
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import QApplication
from PIL import Image
import tempfile
import os


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for all tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def main_window(qtbot, qapp):
    """Create main window for testing"""
    from gui.main_window import MainWindow
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    return window


@pytest.fixture
def sample_image(tmp_path):
    """Create a sample image for testing"""
    img_path = tmp_path / "test_image.png"
    # Create a simple test image
    img = Image.new('RGB', (800, 600), color='blue')
    img.save(img_path)
    return img_path


@pytest.fixture
def sample_images(tmp_path):
    """Create multiple sample images for batch testing"""
    paths = []
    colors = ['red', 'green', 'blue', 'yellow', 'purple']
    for i, color in enumerate(colors):
        img_path = tmp_path / f"test_image_{i}.png"
        img = Image.new('RGB', (800, 600), color=color)
        img.save(img_path)
        paths.append(img_path)
    return paths


@pytest.fixture
def sample_logo(tmp_path):
    """Create a sample logo for watermark testing"""
    logo_path = tmp_path / "logo.png"
    # Create a simple logo with transparency
    img = Image.new('RGBA', (100, 100), color=(255, 255, 255, 0))
    # Draw a simple shape
    for x in range(20, 80):
        for y in range(20, 80):
            img.putpixel((x, y), (255, 0, 0, 200))
    img.save(logo_path)
    return logo_path


@pytest.fixture
def output_folder(tmp_path):
    """Create output folder for processed images"""
    output = tmp_path / "output"
    output.mkdir()
    return output
