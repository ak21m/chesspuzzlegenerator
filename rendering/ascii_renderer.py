"""
ASCII board rendering with Unicode chess pieces
"""

import chess
from typing import Optional, List


class AsciiRenderer:
    """
    Renders chess boards as ASCII art with Unicode pieces
    Perfect for terminal display
    """

    # Unicode chess pieces
    PIECES = {
        chess.PAWN: {'white': '♙', 'black': '♟'},
        chess.KNIGHT: {'white': '♘', 'black': '♞'},
        chess.BISHOP: {'white': '♗', 'black': '♝'},
        chess.ROOK: {'white': '♖', 'black': '♜'},
        chess.QUEEN: {'white': '♕', 'black': '♛'},
        chess.KING: {'white': '♔', 'black': '♚'},
    }

    # ANSI color codes - High contrast for better visibility
    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'dim': '\033[2m',
        'light_square': '\033[48;5;255m\033[38;5;0m',  # White bg, black pieces
        'dark_square': '\033[48;5;94m\033[38;5;255m',   # Brown bg, white pieces
        'highlight': '\033[48;5;226m\033[38;5;0m',      # Bright yellow highlight, black pieces
        'arrow_color': '\033[38;5;33m',                  # Blue for arrows
        'coords': '\033[38;5;248m',                      # Light gray for coordinates
        'white_piece': '\033[1m',                        # Bold for white pieces
        'black_piece': '',                               # Normal for black pieces
    }

    def __init__(self, use_colors: bool = True):
        """
        Initialize ASCII renderer

        Args:
            use_colors: Whether to use ANSI color codes
        """
        self.use_colors = use_colors

    def render_board(
        self,
        board: chess.Board,
        orientation: chess.Color = chess.WHITE,
        highlight_squares: Optional[List[chess.Square]] = None,
        last_move: Optional[chess.Move] = None,
        show_coords: bool = True
    ) -> str:
        """
        Render board as ASCII string

        Args:
            board: chess.Board instance
            orientation: Board perspective (WHITE or BLACK)
            highlight_squares: List of squares to highlight
            last_move: Last move played (to show with markers)
            show_coords: Whether to show file/rank coordinates

        Returns:
            ASCII string representation of board
        """
        highlight_squares = highlight_squares or []
        lines = []

        # Top border
        if show_coords:
            lines.append(self._format_top_border())

        # Iterate through ranks
        ranks = range(7, -1, -1) if orientation == chess.WHITE else range(8)

        for rank in ranks:
            line_parts = []

            # Left rank label
            if show_coords:
                rank_label = f" {rank + 1} "
                if self.use_colors:
                    line_parts.append(f"{self.COLORS['coords']}{rank_label}{self.COLORS['reset']}")
                else:
                    line_parts.append(rank_label)

            # Squares in rank
            files = range(8) if orientation == chess.WHITE else range(7, -1, -1)

            for file in files:
                square = chess.square(file, rank)
                piece = board.piece_at(square)

                # Determine square color
                is_light = (file + rank) % 2 == 1
                is_highlighted = square in highlight_squares
                is_last_move = last_move and (square in [last_move.from_square, last_move.to_square])

                # Build square string
                square_str = self._render_square(piece, is_light, is_highlighted, is_last_move)
                line_parts.append(square_str)

            # Right border
            if show_coords:
                if self.use_colors:
                    line_parts.append(f" {self.COLORS['reset']}")
                else:
                    line_parts.append(" ")

            lines.append("".join(line_parts))

        # Bottom border with file labels
        if show_coords:
            lines.append(self._format_bottom_border(orientation))

        return "\n".join(lines)

    def _render_square(
        self,
        piece: Optional[chess.Piece],
        is_light: bool,
        is_highlighted: bool,
        is_last_move: bool
    ) -> str:
        """
        Render a single square

        Args:
            piece: Piece on square (or None)
            is_light: Whether square is light colored
            is_highlighted: Whether to highlight this square
            is_last_move: Whether this is part of last move

        Returns:
            Formatted square string
        """
        # Get piece symbol
        if piece:
            color_key = 'white' if piece.color == chess.WHITE else 'black'
            piece_symbol = self.PIECES[piece.piece_type][color_key]
        else:
            piece_symbol = ' '

        # Apply colors
        if self.use_colors:
            if is_highlighted:
                bg_color = self.COLORS['highlight']
            elif is_light:
                bg_color = self.COLORS['light_square']
            else:
                bg_color = self.COLORS['dark_square']

            # Make pieces bolder
            piece_style = self.COLORS['white_piece'] if (piece and piece.color == chess.WHITE) else self.COLORS['black_piece']

            # Add extra spacing and bold for last move
            if is_last_move:
                return f"{bg_color}{self.COLORS['bold']} {piece_symbol} {self.COLORS['reset']}"
            else:
                return f"{bg_color}{piece_style} {piece_symbol} {self.COLORS['reset']}"
        else:
            # No colors - use brackets for highlights
            if is_highlighted:
                return f"[{piece_symbol}]"
            elif is_last_move:
                return f"<{piece_symbol}>"
            else:
                return f" {piece_symbol} "

    def _format_top_border(self) -> str:
        """Format top border"""
        if self.use_colors:
            return f"\n{self.COLORS['coords']}   ╔{'═' * 24}╗{self.COLORS['reset']}"
        else:
            return "\n   +" + "─" * 24 + "+"

    def _format_bottom_border(self, orientation: chess.Color) -> str:
        """Format bottom border with file labels"""
        files = "abcdefgh" if orientation == chess.WHITE else "hgfedcba"

        if self.use_colors:
            border = f"{self.COLORS['coords']}   ╚{'═' * 24}╝{self.COLORS['reset']}\n"
            file_labels = f"{self.COLORS['coords']}     "
            file_labels += "  ".join(files)
            file_labels += f"{self.COLORS['reset']}\n"
            return border + file_labels
        else:
            border = "   +" + "─" * 24 + "+\n"
            file_labels = "     " + "  ".join(files) + "\n"
            return border + file_labels

    def render_compact_board(
        self,
        board: chess.Board,
        orientation: chess.Color = chess.WHITE
    ) -> str:
        """
        Render a more compact board (no borders)

        Args:
            board: chess.Board instance
            orientation: Board perspective

        Returns:
            Compact ASCII representation
        """
        lines = []
        ranks = range(7, -1, -1) if orientation == chess.WHITE else range(8)

        for rank in ranks:
            rank_str = f"{rank + 1} "
            files = range(8) if orientation == chess.WHITE else range(7, -1, -1)

            for file in files:
                square = chess.square(file, rank)
                piece = board.piece_at(square)

                if piece:
                    color_key = 'white' if piece.color == chess.WHITE else 'black'
                    rank_str += self.PIECES[piece.piece_type][color_key]
                else:
                    rank_str += "·"  # Empty square dot

                rank_str += " "

            lines.append(rank_str)

        # File labels
        files = "abcdefgh" if orientation == chess.WHITE else "hgfedcba"
        lines.append("  " + " ".join(files))

        return "\n".join(lines)

    def render_move_info(
        self,
        move: chess.Move,
        board: chess.Board,
        move_number: int
    ) -> str:
        """
        Render information about a move

        Args:
            move: The move
            board: Board position before move
            move_number: Move number in game

        Returns:
            Formatted move information
        """
        san = board.san(move)
        piece = board.piece_at(move.from_square)

        if piece:
            color_key = 'white' if piece.color == chess.WHITE else 'black'
            piece_symbol = self.PIECES[piece.piece_type][color_key]

            if self.use_colors:
                if piece.color == chess.WHITE:
                    return f"{self.COLORS['bold']}{move_number}. {piece_symbol} {san}{self.COLORS['reset']}"
                else:
                    return f"{self.COLORS['dim']}{move_number}... {piece_symbol} {san}{self.COLORS['reset']}"
            else:
                prefix = f"{move_number}." if piece.color == chess.WHITE else f"{move_number}..."
                return f"{prefix} {piece_symbol} {san}"

        return f"{move_number}. {san}"

    def render_hint_indicator(
        self,
        hint_level: int,
        from_square: Optional[str] = None,
        to_square: Optional[str] = None
    ) -> str:
        """
        Render hint indicator with arrows

        Args:
            hint_level: Current hint level
            from_square: Source square (e.g., "e2")
            to_square: Destination square (e.g., "e4")

        Returns:
            Formatted hint indicator
        """
        if hint_level >= 4 and from_square and to_square:
            if self.use_colors:
                arrow = f"{self.COLORS['arrow_color']}➔{self.COLORS['reset']}"
                return f"\n  Hint: {from_square} {arrow} {to_square}\n"
            else:
                return f"\n  Hint: {from_square} -> {to_square}\n"
        elif hint_level >= 3 and to_square:
            return f"\n  Hint destination: {to_square}\n"
        elif hint_level >= 2 and from_square:
            return f"\n  Hint source: {from_square}\n"
        else:
            return ""

    @staticmethod
    def supports_unicode() -> bool:
        """
        Check if terminal supports Unicode

        Returns:
            True if Unicode is supported
        """
        try:
            import sys
            import locale

            # Check encoding
            encoding = sys.stdout.encoding or locale.getpreferredencoding()
            if encoding and 'utf' in encoding.lower():
                return True

            # Test Unicode output
            sys.stdout.write('\u2654')
            sys.stdout.flush()
            return True
        except (UnicodeEncodeError, AttributeError):
            return False
