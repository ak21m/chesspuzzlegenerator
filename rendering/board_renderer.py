"""
Board rendering - SVG to PNG conversion
"""

import chess
import chess.svg
import cairosvg
from pathlib import Path
from typing import List, Optional

from config.settings import Settings
from data.models import Hint
from utils.exceptions import RenderError
from utils.helpers import ensure_dir


class BoardRenderer:
    """
    Renders chess boards as PNG images
    Pipeline: chess.Board → SVG → PNG
    """

    def __init__(self, output_dir: str, size: int = None):
        """
        Initialize board renderer

        Args:
            output_dir: Directory for output PNG files
            size: Board size in pixels (default from settings)
        """
        self.output_dir = Path(output_dir)
        self.size = size or Settings.BOARD_SIZE
        ensure_dir(str(self.output_dir))

    def render_position(
        self,
        board: chess.Board,
        filename: str,
        orientation: chess.Color = chess.WHITE,
        highlight_squares: Optional[List[chess.Square]] = None,
        arrows: Optional[List[chess.svg.Arrow]] = None
    ) -> str:
        """
        Render board position to PNG file

        Args:
            board: chess.Board instance
            filename: Output filename (without path)
            orientation: Board perspective (WHITE or BLACK)
            highlight_squares: List of squares to highlight
            arrows: List of arrows to draw

        Returns:
            Full path to generated PNG file

        Raises:
            RenderError: If rendering fails
        """
        try:
            # Generate SVG
            # chess.svg.board needs lists (not None) for squares/arrows
            svg_data = chess.svg.board(
                board=board,
                orientation=orientation,
                size=self.size,
                coordinates=Settings.BOARD_COORDINATES,
                squares=highlight_squares if highlight_squares is not None else [],
                arrows=arrows if arrows is not None else []
            )

            # Convert SVG to PNG
            output_path = self.output_dir / filename

            cairosvg.svg2png(
                bytestring=svg_data.encode('utf-8'),
                write_to=str(output_path),
                output_width=self.size,
                output_height=self.size
            )

            return str(output_path)

        except Exception as e:
            raise RenderError(f"Failed to render board: {e}")

    def render_puzzle(
        self,
        board: chess.Board,
        puzzle_id: str,
        hint: Optional[Hint] = None
    ) -> str:
        """
        Render puzzle position with optional hint highlighting

        Args:
            board: Current board state
            puzzle_id: Puzzle ID for filename
            hint: Optional hint to visualize

        Returns:
            Path to PNG file
        """
        # Determine orientation (side to move)
        orientation = board.turn

        # Setup highlighting based on hint
        highlight_squares = []
        arrows = []

        if hint:
            reveal_data = hint.reveal_data

            # Highlight source square (hint levels 2+)
            if 'from_square' in reveal_data:
                try:
                    from_sq = chess.parse_square(reveal_data['from_square'])
                    highlight_squares.append(from_sq)
                except ValueError:
                    pass

            # Highlight destination square (hint levels 3+)
            if 'to_square' in reveal_data:
                try:
                    to_sq = chess.parse_square(reveal_data['to_square'])
                    highlight_squares.append(to_sq)
                except ValueError:
                    pass

            # Draw arrow for full move hint (level 4)
            if hint.level >= 4 and 'from_square' in reveal_data and 'to_square' in reveal_data:
                try:
                    from_sq = chess.parse_square(reveal_data['from_square'])
                    to_sq = chess.parse_square(reveal_data['to_square'])
                    arrows.append(chess.svg.Arrow(from_sq, to_sq))
                except ValueError:
                    pass

        # Generate filename
        hint_suffix = f"_hint{hint.level}" if hint else ""
        filename = f"puzzle_{puzzle_id}{hint_suffix}.png"

        return self.render_position(
            board=board,
            filename=filename,
            orientation=orientation,
            highlight_squares=highlight_squares,
            arrows=arrows
        )

    def render_solution(
        self,
        board: chess.Board,
        puzzle_id: str,
        solution_moves: List[str]
    ) -> str:
        """
        Render board with solution moves visualized

        Args:
            board: Board position
            puzzle_id: Puzzle ID
            solution_moves: List of moves in UCI format

        Returns:
            Path to PNG file
        """
        # Create arrows for solution moves
        arrows = []
        temp_board = board.copy()

        try:
            for move_uci in solution_moves[:3]:  # Show first 3 moves
                move = chess.Move.from_uci(move_uci)
                if move in temp_board.legal_moves:
                    # Alternate arrow colors for clarity
                    color = "#0000ff" if len(arrows) % 2 == 0 else "#ff0000"
                    arrows.append(chess.svg.Arrow(
                        move.from_square,
                        move.to_square,
                        color=color
                    ))
                    temp_board.push(move)
        except ValueError:
            pass  # Skip invalid moves

        filename = f"puzzle_{puzzle_id}_solution.png"

        return self.render_position(
            board=board,
            filename=filename,
            orientation=board.turn,
            arrows=arrows
        )

    def render_simple(
        self,
        fen: str,
        filename: str,
        orientation: chess.Color = chess.WHITE
    ) -> str:
        """
        Simple render from FEN string

        Args:
            fen: FEN position string
            filename: Output filename
            orientation: Board orientation

        Returns:
            Path to PNG file
        """
        try:
            board = chess.Board(fen)
        except ValueError as e:
            raise RenderError(f"Invalid FEN: {e}")

        return self.render_position(
            board=board,
            filename=filename,
            orientation=orientation
        )

    def cleanup_old_images(self, keep_count: int = 10):
        """
        Clean up old board images to save space

        Args:
            keep_count: Number of most recent images to keep
        """
        # Get all PNG files in output directory
        png_files = sorted(
            self.output_dir.glob("*.png"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        # Remove old files
        for old_file in png_files[keep_count:]:
            try:
                old_file.unlink()
            except OSError:
                pass  # Skip if file is in use
