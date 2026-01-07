"""
Terminal inline image display
Supports iTerm2, Kitty, and other protocols
"""

import os
import sys
import base64
from pathlib import Path


class TerminalImageRenderer:
    """
    Renders images inline in terminal
    Supports multiple terminal protocols
    """

    def __init__(self):
        """Initialize and detect terminal capabilities"""
        self.terminal = os.environ.get('TERM_PROGRAM', '')
        self.term = os.environ.get('TERM', '')

    def can_display_images(self) -> bool:
        """
        Check if terminal supports inline images

        Returns:
            True if images can be displayed inline
        """
        # iTerm2
        if 'iTerm' in self.terminal:
            return True

        # Kitty
        if 'kitty' in self.term.lower():
            return True

        # WezTerm
        if 'wezterm' in self.terminal.lower():
            return True

        return False

    def display_image(self, image_path: str, width: int = 512) -> bool:
        """
        Display image inline in terminal

        Args:
            image_path: Path to PNG image
            width: Display width in pixels (default 512)

        Returns:
            True if successfully displayed
        """
        if not Path(image_path).exists():
            return False

        # Try iTerm2 protocol first
        if 'iTerm' in self.terminal:
            return self._display_iterm2(image_path, width)

        # Try Kitty protocol
        if 'kitty' in self.term.lower():
            return self._display_kitty(image_path, width)

        return False

    def _display_iterm2(self, image_path: str, width: int) -> bool:
        """
        Display image using iTerm2 inline image protocol

        Args:
            image_path: Path to image
            width: Display width in pixels

        Returns:
            True if successful
        """
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()

            # Encode to base64
            encoded = base64.b64encode(image_data).decode('ascii')

            # iTerm2 inline image protocol
            # Format: ESC ] 1337 ; File=inline=1;width=<width>px:<base64> BEL
            print(f"\033]1337;File=inline=1;width={width}px:{encoded}\007")
            print()  # Add newline after image

            return True
        except Exception as e:
            print(f"Error displaying image: {e}", file=sys.stderr)
            return False

    def _display_kitty(self, image_path: str, width: int) -> bool:
        """
        Display image using Kitty graphics protocol

        Args:
            image_path: Path to image
            width: Display width in pixels

        Returns:
            True if successful
        """
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()

            # Encode to base64
            encoded = base64.b64encode(image_data).decode('ascii')

            # Kitty graphics protocol
            # Split into chunks (4096 bytes max per chunk)
            chunk_size = 4096
            chunks = [encoded[i:i+chunk_size] for i in range(0, len(encoded), chunk_size)]

            # Send first chunk with metadata
            print(f"\033_Ga=T,f=100,t=f,m=1;{chunks[0]}\033\\", end='')

            # Send remaining chunks
            for chunk in chunks[1:-1]:
                print(f"\033_Gm=1;{chunk}\033\\", end='')

            # Send last chunk
            if len(chunks) > 1:
                print(f"\033_Gm=0;{chunks[-1]}\033\\")
            else:
                print()

            return True
        except Exception as e:
            print(f"Error displaying image: {e}", file=sys.stderr)
            return False

    def get_fallback_message(self, image_path: str) -> str:
        """
        Get fallback message when inline display is not supported

        Args:
            image_path: Path to image

        Returns:
            Message to display
        """
        return f"\n📷 Board image saved: {image_path}\n   Open it to see the position.\n"


def display_board_image(image_path: str, width: int = 512) -> bool:
    """
    Convenience function to display board image

    Args:
        image_path: Path to PNG image
        width: Display width in pixels

    Returns:
        True if displayed inline, False if fallback to file path
    """
    renderer = TerminalImageRenderer()

    if renderer.can_display_images():
        return renderer.display_image(image_path, width)
    else:
        print(renderer.get_fallback_message(image_path))
        return False
