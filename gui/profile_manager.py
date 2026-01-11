"""
Profile manager - save and load watermark configurations
"""
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton,
    QLabel, QLineEdit, QTextEdit, QMessageBox,
    QFileDialog, QInputDialog
)
from PyQt6.QtCore import Qt

from config import PROFILES_FOLDER
from models.schemas import BatchProcessConfig, WatermarkProfile


class ProfileManager:
    """Manages saving and loading of watermark profiles"""

    def __init__(self, profiles_folder: Optional[Path] = None):
        self.profiles_folder = profiles_folder or PROFILES_FOLDER
        self.profiles_folder.mkdir(parents=True, exist_ok=True)

    def save_profile(self, name: str, config: BatchProcessConfig, description: str = "") -> Path:
        """Save a profile to disk"""
        profile = WatermarkProfile(
            name=name,
            description=description,
            config=config,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )

        # Create safe filename
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
        file_path = self.profiles_folder / f"{safe_name}.json"

        with open(file_path, 'w') as f:
            json.dump(profile.model_dump(), f, indent=2)

        return file_path

    def load_profile(self, file_path: Path) -> Optional[WatermarkProfile]:
        """Load a profile from disk"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return WatermarkProfile(**data)
        except Exception as e:
            print(f"Error loading profile: {e}")
            return None

    def list_profiles(self) -> list:
        """List all saved profiles"""
        profiles = []
        for file_path in self.profiles_folder.glob("*.json"):
            try:
                profile = self.load_profile(file_path)
                if profile:
                    profiles.append((file_path, profile))
            except Exception:
                pass
        return profiles

    def delete_profile(self, file_path: Path) -> bool:
        """Delete a profile"""
        try:
            file_path.unlink()
            return True
        except Exception:
            return False

    def save_profile_dialog(self, parent: QWidget, config: BatchProcessConfig) -> Optional[Path]:
        """Show dialog to save profile"""
        name, ok = QInputDialog.getText(
            parent,
            "Save Profile",
            "Profile name:",
            QLineEdit.EchoMode.Normal
        )

        if ok and name:
            try:
                path = self.save_profile(name, config)
                QMessageBox.information(
                    parent,
                    "Profile Saved",
                    f"Profile '{name}' saved successfully."
                )
                return path
            except Exception as e:
                QMessageBox.warning(
                    parent,
                    "Error",
                    f"Failed to save profile: {str(e)}"
                )
        return None

    def load_profile_dialog(self, parent: QWidget) -> Optional[BatchProcessConfig]:
        """Show dialog to load profile"""
        dialog = LoadProfileDialog(self, parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.selected_config
        return None


class LoadProfileDialog(QDialog):
    """Dialog for loading a saved profile"""

    def __init__(self, manager: ProfileManager, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.manager = manager
        self.selected_config: Optional[BatchProcessConfig] = None
        self.profiles = {}
        self.setup_ui()
        self.load_profiles()

    def setup_ui(self):
        self.setWindowTitle("Load Profile")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout(self)

        # Profile list
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.accept)
        self.list_widget.currentItemChanged.connect(self.on_selection_changed)
        layout.addWidget(self.list_widget)

        # Description
        self.desc_label = QLabel("")
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("color: #888; padding: 5px;")
        layout.addWidget(self.desc_label)

        # Buttons
        btn_layout = QHBoxLayout()

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_profile)
        btn_layout.addWidget(delete_btn)

        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        load_btn = QPushButton("Load")
        load_btn.setDefault(True)
        load_btn.clicked.connect(self.accept)
        btn_layout.addWidget(load_btn)

        layout.addLayout(btn_layout)

    def load_profiles(self):
        """Load all profiles into the list"""
        self.list_widget.clear()
        self.profiles.clear()

        for file_path, profile in self.manager.list_profiles():
            item = QListWidgetItem(profile.name)
            item.setData(Qt.ItemDataRole.UserRole, file_path)
            self.list_widget.addItem(item)
            self.profiles[str(file_path)] = profile

    def on_selection_changed(self, current, previous):
        """Handle selection change"""
        if current:
            file_path = str(current.data(Qt.ItemDataRole.UserRole))
            profile = self.profiles.get(file_path)
            if profile and profile.description:
                self.desc_label.setText(profile.description)
            else:
                self.desc_label.setText("")

    def delete_profile(self):
        """Delete selected profile"""
        current = self.list_widget.currentItem()
        if current:
            file_path = current.data(Qt.ItemDataRole.UserRole)
            name = current.text()

            reply = QMessageBox.question(
                self,
                "Delete Profile",
                f"Delete profile '{name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                if self.manager.delete_profile(file_path):
                    self.load_profiles()

    def accept(self):
        """Handle accept (load selected profile)"""
        current = self.list_widget.currentItem()
        if current:
            file_path = current.data(Qt.ItemDataRole.UserRole)
            profile = self.manager.load_profile(file_path)
            if profile:
                self.selected_config = profile.config
                super().accept()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Failed to load profile."
                )
        else:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select a profile to load."
            )
