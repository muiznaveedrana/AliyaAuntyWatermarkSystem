"""
Main application window
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QStatusBar, QMenuBar, QMenu, QToolBar,
    QFileDialog, QMessageBox, QProgressBar, QLabel
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from pathlib import Path
from typing import List

from config import APP_NAME, APP_VERSION, OUTPUT_FOLDER
from .image_list_panel import ImageListPanel
from .watermark_panel import WatermarkPanel
from .preview_panel import PreviewPanel
from .profile_manager import ProfileManager
from core.batch_processor import BatchProcessor
from models.schemas import BatchProcessConfig


class ProcessingThread(QThread):
    """Thread for batch processing images"""
    progress = pyqtSignal(int, int, str)  # current, total, filename
    finished = pyqtSignal(object)  # BatchProcessingResult
    error = pyqtSignal(str)

    def __init__(self, processor: BatchProcessor, paths: List[Path], config: BatchProcessConfig, output_folder: Path):
        super().__init__()
        self.processor = processor
        self.paths = paths
        self.config = config
        self.output_folder = output_folder

    def run(self):
        try:
            self.processor.set_progress_callback(
                lambda c, t, f: self.progress.emit(c, t, f)
            )
            result = self.processor.process_batch(
                self.paths,
                self.config,
                self.output_folder
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.processor = BatchProcessor()
        self.profile_manager = ProfileManager()
        self.processing_thread = None
        self.current_images: List[Path] = []

        self.setup_ui()
        self.setup_toolbar()
        self.setup_statusbar()
        self.connect_signals()

    def setup_ui(self):
        """Setup the main UI layout"""
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(1100, 750)
        self.resize(1300, 850)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout with splitter
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(3)

        # Left panel - Image list
        self.image_list_panel = ImageListPanel()
        self.image_list_panel.setMinimumWidth(250)
        splitter.addWidget(self.image_list_panel)

        # Middle panel - Watermark settings
        self.watermark_panel = WatermarkPanel()
        self.watermark_panel.setMinimumWidth(320)
        splitter.addWidget(self.watermark_panel)

        # Right panel - Preview
        self.preview_panel = PreviewPanel()
        self.preview_panel.setMinimumWidth(350)
        splitter.addWidget(self.preview_panel)

        # Set splitter sizes (25%, 35%, 40%)
        splitter.setSizes([280, 380, 440])

        main_layout.addWidget(splitter)

    def setup_toolbar(self):
        """Setup toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.addToolBar(toolbar)

        # Add images button
        add_btn = QAction("Add Images", self)
        add_btn.setToolTip("Add image files to process")
        add_btn.triggered.connect(self.add_images)
        toolbar.addAction(add_btn)

        # Add folder button
        folder_btn = QAction("Add Folder", self)
        folder_btn.setToolTip("Add all images from a folder")
        folder_btn.triggered.connect(self.add_folder)
        toolbar.addAction(folder_btn)

        toolbar.addSeparator()

        # Process button
        self.process_btn = QAction("Process All", self)
        self.process_btn.setToolTip("Apply watermarks to all images")
        self.process_btn.triggered.connect(self.start_processing)
        toolbar.addAction(self.process_btn)

        # Cancel button
        self.cancel_btn = QAction("Cancel", self)
        self.cancel_btn.setToolTip("Cancel processing")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.triggered.connect(self.cancel_processing)
        toolbar.addAction(self.cancel_btn)

        toolbar.addSeparator()

        # Output folder button
        output_btn = QAction("Output Folder", self)
        output_btn.setToolTip("Choose where to save watermarked images")
        output_btn.triggered.connect(self.set_output_folder)
        toolbar.addAction(output_btn)

        toolbar.addSeparator()

        # Save preset button
        save_btn = QAction("Save Preset", self)
        save_btn.setToolTip("Save current watermark settings as a reusable preset")
        save_btn.triggered.connect(self.save_profile)
        toolbar.addAction(save_btn)

        # Load preset button
        load_btn = QAction("Load Preset", self)
        load_btn.setToolTip("Load a saved watermark preset")
        load_btn.triggered.connect(self.load_profile)
        toolbar.addAction(load_btn)

    def setup_statusbar(self):
        """Setup status bar"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.statusbar.addPermanentWidget(self.progress_bar)

        # Image count label
        self.count_label = QLabel("0 images")
        self.statusbar.addPermanentWidget(self.count_label)

        self.statusbar.showMessage("Ready")

    def connect_signals(self):
        """Connect signals between panels"""
        # Image selection changed -> update preview
        self.image_list_panel.selection_changed.connect(self.on_image_selected)

        # Watermark settings changed -> update preview
        self.watermark_panel.settings_changed.connect(self.update_preview)

    def add_images(self):
        """Add images via file dialog"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Images",
            "",
            "Images (*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.tif *.webp);;All Files (*)"
        )

        if files:
            paths = [Path(f) for f in files]
            self.image_list_panel.add_images(paths)
            self.current_images.extend(paths)
            self.update_count()
            self.statusbar.showMessage(f"Added {len(files)} images")

    def add_folder(self):
        """Add all images from a folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")

        if folder:
            folder_path = Path(folder)
            extensions = ('*.jpg', '*.jpeg', '*.png', '*.bmp', '*.gif', '*.tiff', '*.tif', '*.webp')
            paths = []
            for ext in extensions:
                paths.extend(folder_path.glob(ext))
                paths.extend(folder_path.glob(ext.upper()))

            paths = list(set(paths))
            if paths:
                self.image_list_panel.add_images(paths)
                self.current_images.extend(paths)
                self.update_count()
                self.statusbar.showMessage(f"Added {len(paths)} images from folder")
            else:
                self.statusbar.showMessage("No images found in folder")

    def clear_images(self):
        """Clear all images"""
        self.image_list_panel.clear()
        self.current_images.clear()
        self.preview_panel.clear()
        self.update_count()
        self.statusbar.showMessage("Cleared all images")

    def update_count(self):
        """Update image count label"""
        count = len(self.current_images)
        self.count_label.setText(f"{count} image{'s' if count != 1 else ''}")

    def on_image_selected(self, path: Path):
        """Handle image selection"""
        if path:
            self.preview_panel.load_image(path)
            self.update_preview()

    def update_preview(self):
        """Update preview with current watermark settings"""
        config = self.watermark_panel.get_config()
        self.preview_panel.apply_watermark_preview(config)

    def set_output_folder(self):
        """Set output folder"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            str(OUTPUT_FOLDER)
        )
        if folder:
            self.output_folder = Path(folder)
            self.statusbar.showMessage(f"Output folder: {folder}")

    def start_processing(self):
        """Start batch processing"""
        if not self.current_images:
            QMessageBox.warning(self, "No Images", "Please add images to process.")
            return

        config = self.watermark_panel.get_config()

        # Check if at least one watermark is configured
        if not config.text_watermarks and not config.image_watermarks:
            QMessageBox.warning(
                self,
                "No Watermark",
                "Please configure at least one text or image watermark."
            )
            return

        output_folder = getattr(self, 'output_folder', OUTPUT_FOLDER)

        # Update UI for processing
        self.process_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Start processing thread
        self.processing_thread = ProcessingThread(
            self.processor,
            self.current_images,
            config,
            output_folder
        )
        self.processing_thread.progress.connect(self.on_progress)
        self.processing_thread.finished.connect(self.on_processing_finished)
        self.processing_thread.error.connect(self.on_processing_error)
        self.processing_thread.start()

    def cancel_processing(self):
        """Cancel processing"""
        if self.processing_thread:
            self.processor.cancel()
            self.statusbar.showMessage("Cancelling...")

    def on_progress(self, current: int, total: int, filename: str):
        """Handle progress update"""
        percent = int((current / total) * 100)
        self.progress_bar.setValue(percent)
        self.statusbar.showMessage(f"Processing: {filename} ({current}/{total})")

    def on_processing_finished(self, result):
        """Handle processing completion"""
        self.process_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setVisible(False)

        QMessageBox.information(
            self,
            "Processing Complete",
            f"Processed {result.total_images} images:\n"
            f"- Successful: {result.successful}\n"
            f"- Failed: {result.failed}\n"
            f"- Time: {result.total_time_ms / 1000:.1f} seconds"
        )
        self.statusbar.showMessage(f"Completed: {result.successful}/{result.total_images} images")

    def on_processing_error(self, error: str):
        """Handle processing error"""
        self.process_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setVisible(False)

        QMessageBox.critical(self, "Error", f"Processing failed: {error}")
        self.statusbar.showMessage("Processing failed")

    def save_profile(self):
        """Save current settings as profile"""
        config = self.watermark_panel.get_config()
        self.profile_manager.save_profile_dialog(self, config)

    def load_profile(self):
        """Load profile"""
        config = self.profile_manager.load_profile_dialog(self)
        if config:
            self.watermark_panel.load_config(config)
            self.update_preview()
            self.statusbar.showMessage("Profile loaded")

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            f"About {APP_NAME}",
            f"<h3>{APP_NAME} v{APP_VERSION}</h3>"
            "<p>A powerful batch watermarking tool for images.</p>"
            "<p>Features:</p>"
            "<ul>"
            "<li>Text and image watermarks</li>"
            "<li>Batch processing with multi-threading</li>"
            "<li>9-point positioning system</li>"
            "<li>EXIF data integration</li>"
            "<li>Profile/template saving</li>"
            "</ul>"
        )
