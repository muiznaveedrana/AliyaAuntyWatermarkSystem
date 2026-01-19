"""
Media list panel - displays and manages the list of images and videos to process
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QHBoxLayout, QAbstractItemView,
    QFrame
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QIcon, QPixmap
from pathlib import Path
from typing import List

from config import SUPPORTED_IMAGE_FORMATS, SUPPORTED_VIDEO_FORMATS


class ImageListPanel(QFrame):
    """Panel for displaying and managing the media list (images and videos)"""

    selection_changed = pyqtSignal(object)  # Emits Path or None

    def __init__(self):
        super().__init__()
        self.image_paths: List[Path] = []  # Keep name for compatibility, but holds all media
        self.setup_ui()

    def _is_video(self, path: Path) -> bool:
        """Check if file is a video"""
        return path.suffix.lower() in SUPPORTED_VIDEO_FORMATS

    def _is_image(self, path: Path) -> bool:
        """Check if file is an image"""
        return path.suffix.lower() in SUPPORTED_IMAGE_FORMATS

    def setup_ui(self):
        """Setup the panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Header
        header = QLabel("Files to Process")
        header.setProperty("header", True)
        layout.addWidget(header)

        # File count label
        self.count_label = QLabel("No files added")
        self.count_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(self.count_label)

        # Image list
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.list_widget.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.list_widget.currentItemChanged.connect(self.on_selection_changed)
        self.list_widget.setMinimumHeight(200)
        layout.addWidget(self.list_widget, 1)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_selected)
        btn_layout.addWidget(remove_btn)

        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear)
        btn_layout.addWidget(clear_btn)

        layout.addLayout(btn_layout)

    def add_images(self, paths: List[Path]):
        """Add images/videos to the list"""
        for path in paths:
            if path not in self.image_paths:
                self.image_paths.append(path)
                # Add icon indicator for videos
                if self._is_video(path):
                    item = QListWidgetItem(f"  [VIDEO] {path.name}")
                else:
                    item = QListWidgetItem(f"  {path.name}")
                item.setData(Qt.ItemDataRole.UserRole, path)
                item.setToolTip(str(path))
                self.list_widget.addItem(item)
        self._update_count()

    def remove_selected(self):
        """Remove selected images"""
        for item in self.list_widget.selectedItems():
            path = item.data(Qt.ItemDataRole.UserRole)
            if path in self.image_paths:
                self.image_paths.remove(path)
            self.list_widget.takeItem(self.list_widget.row(item))
        self._update_count()

    def clear(self):
        """Clear all images"""
        self.list_widget.clear()
        self.image_paths.clear()
        self.selection_changed.emit(None)
        self._update_count()

    def _update_count(self):
        """Update the count label"""
        count = len(self.image_paths)
        image_count = sum(1 for p in self.image_paths if self._is_image(p))
        video_count = sum(1 for p in self.image_paths if self._is_video(p))

        if count == 0:
            self.count_label.setText("No files added")
        else:
            parts = []
            if image_count > 0:
                parts.append(f"{image_count} image{'s' if image_count != 1 else ''}")
            if video_count > 0:
                parts.append(f"{video_count} video{'s' if video_count != 1 else ''}")
            self.count_label.setText(" | ".join(parts))

    def on_selection_changed(self, current, previous):
        """Handle selection change"""
        if current:
            path = current.data(Qt.ItemDataRole.UserRole)
            self.selection_changed.emit(path)
        else:
            self.selection_changed.emit(None)

    def get_all_paths(self) -> List[Path]:
        """Get all image paths"""
        return self.image_paths.copy()

    def get_selected_paths(self) -> List[Path]:
        """Get selected image paths"""
        paths = []
        for item in self.list_widget.selectedItems():
            paths.append(item.data(Qt.ItemDataRole.UserRole))
        return paths

    def count(self) -> int:
        """Get number of images"""
        return len(self.image_paths)
