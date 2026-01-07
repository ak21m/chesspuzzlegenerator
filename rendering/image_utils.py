"""
Image utility functions
"""

import os
import subprocess
import platform
from pathlib import Path
from typing import Optional


def open_image(image_path: str) -> bool:
    """
    Open image with default system viewer

    Args:
        image_path: Path to image file

    Returns:
        True if successful, False otherwise
    """
    path = Path(image_path)

    if not path.exists():
        return False

    try:
        system = platform.system()

        if system == 'Darwin':  # macOS
            subprocess.run(['open', str(path)], check=True)
        elif system == 'Windows':
            os.startfile(str(path))
        elif system == 'Linux':
            subprocess.run(['xdg-open', str(path)], check=True)
        else:
            return False

        return True

    except (subprocess.CalledProcessError, OSError, FileNotFoundError):
        return False


def get_image_size(image_path: str) -> Optional[tuple[int, int]]:
    """
    Get image dimensions

    Args:
        image_path: Path to image file

    Returns:
        Tuple of (width, height) or None if error
    """
    try:
        from PIL import Image

        with Image.open(image_path) as img:
            return img.size

    except (ImportError, OSError):
        return None


def image_exists(image_path: str) -> bool:
    """
    Check if image file exists and is valid

    Args:
        image_path: Path to image file

    Returns:
        True if exists and is valid PNG
    """
    path = Path(image_path)

    if not path.exists():
        return False

    if path.suffix.lower() != '.png':
        return False

    # Quick validation - check file is not empty
    if path.stat().st_size == 0:
        return False

    return True


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0

    return f"{size_bytes:.1f} TB"


def get_file_info(file_path: str) -> dict:
    """
    Get file information

    Args:
        file_path: Path to file

    Returns:
        Dictionary with file info
    """
    path = Path(file_path)

    if not path.exists():
        return {'exists': False}

    stat = path.stat()
    size = get_image_size(str(path))

    return {
        'exists': True,
        'size_bytes': stat.st_size,
        'size_formatted': format_file_size(stat.st_size),
        'dimensions': size,
        'path': str(path.absolute())
    }
