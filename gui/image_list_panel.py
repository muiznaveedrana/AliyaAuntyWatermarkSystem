"""
Image list panel - displays and manages the list of images to process
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


class ImageListPanel(QFrame):
    """Panel for displaying and managing the image list"""

    selection_changed = pyqtSignal(object)  # Emits Path or None

    def __init__(self):
        super().__init__()
        self.image_paths: List[Path] = []
        self.setup_ui()

    def setup_ui(self):
        """Setup the panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Header
        header = QLabel("Images to Process")
        header.setProperty("header", True)
        layout.addWidget(header)

        # Image count label
        self.count_label = QLabel("No images added")
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
        """Add images to the list"""
        for path in paths:
            if path not in self.image_paths:
                self.image_paths.append(path)
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
        if count == 0:
            self.count_label.setText("No images added")
        elif count == 1:
            self.count_label.setText("1 image")
        else:
            self.count_label.setText(f"{count} images")

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
