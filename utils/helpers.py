"""
Common utility functions
"""

import os
from pathlib import Path
from typing import Optional


def ensure_dir(directory: str) -> Path:
    """
    Ensure directory exists, create if not

    Args:
        directory: Directory path

    Returns:
        Path object
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def format_time(seconds: float) -> str:
    """
    Format seconds into human-readable time

    Args:
        seconds: Time in seconds

    Returns:
        Formatted string (e.g., "1m 30s" or "45s")
    """
    if seconds < 60:
        return f"{seconds:.1f}s"

    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}m {secs}s"


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate string to max length

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def clear_screen():
    """Clear console screen (cross-platform)"""
    os.system('cls' if os.name == 'nt' else 'clear')


def get_ordinal_suffix(number: int) -> str:
    """
    Get ordinal suffix for number (1st, 2nd, 3rd, etc.)

    Args:
        number: Number

    Returns:
        Ordinal suffix
    """
    if 10 <= number % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(number % 10, 'th')

    return f"{number}{suffix}"
