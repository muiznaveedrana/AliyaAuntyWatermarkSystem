# Image Batch Watermarking Tool

A powerful desktop application for batch watermarking images, inspired by popular tools like Visual Watermark, uMark, and PhotoMarks.

## Features

### Core Features
- [x] **Batch Processing** - Process hundreds of images simultaneously with multi-threading
- [x] **Text Watermarks** - Add customizable text with fonts, colors, shadows, and effects
- [x] **Image/Logo Watermarks** - Overlay logos and images as watermarks
- [x] **Smart Positioning** - 9-point positioning system (corners, edges, center)
- [x] **Opacity Control** - Adjustable transparency for watermarks
- [x] **Rotation** - Rotate watermarks at any angle
- [x] **Tiling** - Repeat watermarks across the entire image
- [x] **EXIF Data Integration** - Use photo metadata in watermarks
- [x] **Profile/Template System** - Save and reuse watermark configurations
- [x] **Live Preview** - See watermark changes in real-time
- [x] **Multi-threaded Processing** - Utilize multiple CPU cores for speed

### Supported Formats
- **Input**: JPEG, PNG, BMP, GIF, TIFF, WebP
- **Output**: JPEG, PNG, WebP

## Screenshots

*The application features a clean three-panel layout:*
1. **Left Panel** - Image list with drag-and-drop support
2. **Middle Panel** - Watermark settings (Text, Image, Output tabs)
3. **Right Panel** - Live preview

## Project Structure

```
AliyaAuntyWatermarkSystem/
├── README.md
├── requirements.txt
├── config.py                  # Application configuration
├── main.py                    # Application entry point
├── core/
│   ├── __init__.py
│   ├── watermark_engine.py    # Core watermarking logic
│   ├── text_watermark.py      # Text watermark processing
│   ├── image_watermark.py     # Image/logo watermark processing
│   ├── batch_processor.py     # Batch processing with threading
│   └── exif_handler.py        # EXIF data extraction
├── gui/
│   ├── __init__.py
│   ├── main_window.py         # Main application window
│   ├── image_list_panel.py    # Image list management
│   ├── watermark_panel.py     # Watermark settings UI
│   ├── preview_panel.py       # Live preview
│   └── profile_manager.py     # Profile save/load dialogs
├── models/
│   ├── __init__.py
│   └── schemas.py             # Pydantic models for validation
├── profiles/                  # Saved watermark profiles (JSON)
└── output/                    # Processed images output
```

## Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Setup

```bash
# Navigate to the project directory
cd AliyaAuntyWatermarkSystem

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Running the Application

```bash
python main.py
```

### Quick Start Guide

1. **Add Images**: Click "Add Images" or "Add Folder" to load images
2. **Configure Watermark**:
   - Go to "Text" tab to add text watermark
   - Go to "Image/Logo" tab to add logo watermark
   - Adjust position, opacity, size, and rotation
3. **Preview**: Select an image to see live preview with watermark
4. **Set Output**: Click "Set Output Folder" to choose destination
5. **Process**: Click "Process All" to batch watermark all images

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+O | Add Images |
| Ctrl+Shift+O | Add Folder |
| Ctrl+S | Save Profile |
| Ctrl+L | Load Profile |
| Ctrl+Q | Exit |

## Text Watermark Options

| Option | Description |
|--------|-------------|
| Text | The watermark text content |
| Font Size | Size in pixels (8-500) |
| Color | RGB color picker |
| Opacity | Transparency (0-100%) |
| Position | 9-point system or tile mode |
| Margin | Distance from edges |
| Rotation | Angle in degrees (-360 to 360) |
| Shadow | Drop shadow effect |
| Scale with Image | Auto-scale based on image size |

## Image Watermark Options

| Option | Description |
|--------|-------------|
| Logo | PNG, JPG, or other image file |
| Opacity | Transparency (0-100%) |
| Scale | Size relative to image (1-100%) |
| Position | 9-point system or tile mode |
| Margin | Distance from edges |
| Rotation | Angle in degrees |
| Grayscale | Convert logo to grayscale |

## Output Options

| Option | Description |
|--------|-------------|
| Format | JPEG, PNG, or WebP |
| Quality | Compression quality (1-100%) |
| Prefix | Add prefix to filenames |
| Suffix | Add suffix to filenames (default: _watermarked) |
| Preserve EXIF | Keep original metadata |

## Tech Stack

- **GUI Framework**: PyQt6
- **Image Processing**: Pillow (PIL)
- **Data Validation**: Pydantic
- **Concurrency**: concurrent.futures (ThreadPoolExecutor)

## Building Executable (Optional)

To create a standalone executable:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "BatchWatermark" main.py
```

The executable will be in the `dist/` folder.

