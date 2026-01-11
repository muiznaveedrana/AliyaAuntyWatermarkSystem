"""
Image list panel - displays and manages the list of images to process
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QHBoxLayout, QAbstractItemView
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QIcon, QPixmap
from pathlib import Path
from typing import List


class ImageListPanel(QWidget):
    """Panel for displaying and managing the image list"""

    selection_changed = pyqtSignal(object)  # Emits Path or None

    def __init__(self):
        super().__init__()
        self.image_paths: List[Path] = []
        self.setup_ui()

    def setup_ui(self):
        """Setup the panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Header
        header = QLabel("Images to Process")
        header.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header)

        # Image list
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.list_widget.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.list_widget.currentItemChanged.connect(self.on_selection_changed)
        layout.addWidget(self.list_widget)

        # Buttons
        btn_layout = QHBoxLayout()

        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_selected)
        btn_layout.addWidget(remove_btn)

        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear)
        btn_layout.addWidget(clear_btn)

        layout.addLayout(btn_layout)

    def add_images(self, paths: List[Path]):
        """Add images to the list"""
        for path in paths:
            if path not in self.image_paths:
                self.image_paths.append(path)
                item = QListWidgetItem(path.name)
                item.setData(Qt.ItemDataRole.UserRole, path)
                item.setToolTip(str(path))
                self.list_widget.addItem(item)

    def remove_selected(self):
        """Remove selected images"""
        for item in self.list_widget.selectedItems():
            path = item.data(Qt.ItemDataRole.UserRole)
            if path in self.image_paths:
                self.image_paths.remove(path)
            self.list_widget.takeItem(self.list_widget.row(item))

    def clear(self):
        """Clear all images"""
        self.list_widget.clear()
        self.image_paths.clear()
        self.selection_changed.emit(None)

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
