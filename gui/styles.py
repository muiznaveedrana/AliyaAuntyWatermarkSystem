"""
Modern dark theme styles for the application
"""

DARK_THEME = """
/* Main Window */
QMainWindow {
    background-color: #1e1e1e;
}

QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 13px;
}

/* Menu Bar */
QMenuBar {
    background-color: #2d2d2d;
    border-bottom: 1px solid #3d3d3d;
    padding: 4px;
}

QMenuBar::item {
    background-color: transparent;
    padding: 6px 12px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #0078d4;
}

QMenu {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    padding: 4px;
}

QMenu::item {
    padding: 8px 24px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #0078d4;
}

QMenu::separator {
    height: 1px;
    background-color: #3d3d3d;
    margin: 4px 8px;
}

/* Toolbar */
QToolBar {
    background-color: #252526;
    border: none;
    border-bottom: 1px solid #3d3d3d;
    padding: 6px;
    spacing: 6px;
}

QToolBar QToolButton {
    background-color: #3c3c3c;
    border: 1px solid #4d4d4d;
    border-radius: 6px;
    padding: 8px 16px;
    color: #e0e0e0;
    font-weight: 500;
}

QToolBar QToolButton:hover {
    background-color: #4d4d4d;
    border-color: #0078d4;
}

QToolBar QToolButton:pressed {
    background-color: #0078d4;
}

QToolBar QToolButton:disabled {
    background-color: #2d2d2d;
    color: #666666;
    border-color: #3d3d3d;
}

QToolBar::separator {
    width: 1px;
    background-color: #3d3d3d;
    margin: 4px 8px;
}

/* Splitter */
QSplitter::handle {
    background-color: #3d3d3d;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}

/* Group Box */
QGroupBox {
    border: 1px solid #3d3d3d;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 12px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 8px;
    color: #0078d4;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #3d3d3d;
    border-radius: 8px;
    background-color: #252526;
    top: -1px;
}

QTabBar::tab {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 10px 20px;
    margin-right: 2px;
    color: #a0a0a0;
}

QTabBar::tab:selected {
    background-color: #252526;
    color: #ffffff;
    border-bottom: 2px solid #0078d4;
}

QTabBar::tab:hover:!selected {
    background-color: #3d3d3d;
    color: #e0e0e0;
}

/* Scroll Area */
QScrollArea {
    border: 1px solid #3d3d3d;
    border-radius: 8px;
    background-color: #1a1a1a;
}

QScrollBar:vertical {
    background-color: #2d2d2d;
    width: 12px;
    border-radius: 6px;
    margin: 2px;
}

QScrollBar::handle:vertical {
    background-color: #4d4d4d;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #5d5d5d;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #2d2d2d;
    height: 12px;
    border-radius: 6px;
    margin: 2px;
}

QScrollBar::handle:horizontal {
    background-color: #4d4d4d;
    border-radius: 5px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #5d5d5d;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* List Widget */
QListWidget {
    background-color: #252526;
    border: 1px solid #3d3d3d;
    border-radius: 8px;
    padding: 4px;
    outline: none;
}

QListWidget::item {
    padding: 8px 12px;
    border-radius: 4px;
    margin: 2px;
}

QListWidget::item:selected {
    background-color: #0078d4;
    color: #ffffff;
}

QListWidget::item:hover:!selected {
    background-color: #3d3d3d;
}

/* Line Edit */
QLineEdit {
    background-color: #3c3c3c;
    border: 1px solid #4d4d4d;
    border-radius: 6px;
    padding: 8px 12px;
    color: #e0e0e0;
    selection-background-color: #0078d4;
}

QLineEdit:focus {
    border-color: #0078d4;
}

QLineEdit:disabled {
    background-color: #2d2d2d;
    color: #666666;
}

/* Spin Box */
QSpinBox, QDoubleSpinBox {
    background-color: #3c3c3c;
    border: 1px solid #4d4d4d;
    border-radius: 6px;
    padding: 6px 10px;
    color: #e0e0e0;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #0078d4;
}

QSpinBox::up-button, QDoubleSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    border-left: 1px solid #4d4d4d;
    border-top-right-radius: 5px;
    width: 20px;
    background-color: #4d4d4d;
}

QSpinBox::down-button, QDoubleSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    border-left: 1px solid #4d4d4d;
    border-bottom-right-radius: 5px;
    width: 20px;
    background-color: #4d4d4d;
}

QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #5d5d5d;
}

QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 6px solid #e0e0e0;
    width: 0;
    height: 0;
}

QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid #e0e0e0;
    width: 0;
    height: 0;
}

/* Combo Box */
QComboBox {
    background-color: #3c3c3c;
    border: 1px solid #4d4d4d;
    border-radius: 6px;
    padding: 8px 12px;
    color: #e0e0e0;
    min-width: 100px;
}

QComboBox:focus {
    border-color: #0078d4;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 24px;
    border: none;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #e0e0e0;
    width: 0;
    height: 0;
}

QComboBox QAbstractItemView {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    selection-background-color: #0078d4;
    padding: 4px;
}

/* Check Box */
QCheckBox {
    spacing: 8px;
    color: #e0e0e0;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #4d4d4d;
    border-radius: 4px;
    background-color: #3c3c3c;
}

QCheckBox::indicator:checked {
    background-color: #0078d4;
    border-color: #0078d4;
}

QCheckBox::indicator:hover {
    border-color: #0078d4;
}

/* Slider */
QSlider::groove:horizontal {
    height: 6px;
    background-color: #3c3c3c;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    width: 18px;
    height: 18px;
    margin: -6px 0;
    background-color: #0078d4;
    border-radius: 9px;
}

QSlider::handle:horizontal:hover {
    background-color: #1a8cd8;
}

QSlider::sub-page:horizontal {
    background-color: #0078d4;
    border-radius: 3px;
}

/* Push Button */
QPushButton {
    background-color: #3c3c3c;
    border: 1px solid #4d4d4d;
    border-radius: 6px;
    padding: 8px 16px;
    color: #e0e0e0;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #4d4d4d;
    border-color: #0078d4;
}

QPushButton:pressed {
    background-color: #0078d4;
}

QPushButton:disabled {
    background-color: #2d2d2d;
    color: #666666;
}

/* Primary Button */
QPushButton[primary="true"] {
    background-color: #0078d4;
    border-color: #0078d4;
    color: #ffffff;
}

QPushButton[primary="true"]:hover {
    background-color: #1a8cd8;
}

/* Status Bar */
QStatusBar {
    background-color: #007acc;
    color: #ffffff;
    border: none;
    padding: 4px;
}

QStatusBar::item {
    border: none;
}

/* Progress Bar */
QProgressBar {
    background-color: #3c3c3c;
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #0078d4;
    border-radius: 4px;
}

/* Labels */
QLabel {
    color: #e0e0e0;
}

QLabel[header="true"] {
    font-size: 15px;
    font-weight: bold;
    color: #ffffff;
    padding: 8px 0;
}

/* Message Box */
QMessageBox {
    background-color: #2d2d2d;
}

QMessageBox QLabel {
    color: #e0e0e0;
}

/* Input Dialog */
QInputDialog {
    background-color: #2d2d2d;
}

/* Tool Tip */
QToolTip {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    padding: 6px;
}

/* File Dialog */
QFileDialog {
    background-color: #2d2d2d;
}

/* Color Dialog */
QColorDialog {
    background-color: #2d2d2d;
}
"""

# Accent colors for different elements
ACCENT_COLORS = {
    'primary': '#0078d4',
    'success': '#28a745',
    'warning': '#ffc107',
    'danger': '#dc3545',
    'info': '#17a2b8',
}
