"""
Progressive hint system for puzzles
"""

import chess
from data.models import Hint


class HintSystem:
    """
    Progressive hint system with 4 levels
    Each hint reveals more information
    """

    def __init__(self, board: chess.Board, solution_move_uci: str):
        """
        Initialize hint system

        Args:
            board: Current board position
            solution_move_uci: Expected solution move in UCI format
        """
        self.board = board
        self.solution_move = chess.Move.from_uci(solution_move_uci)
        self.current_level = 0

    def get_next_hint(self) -> Hint:
        """
        Get next hint (increments level)

        Returns:
            Hint object with message and reveal data
        """
        self.current_level += 1

        if self.current_level > 4:
            self.current_level = 4  # Cap at level 4

        return self.get_hint(self.current_level)

    def get_hint(self, level: int) -> Hint:
        """
        Generate hint for specific level

        Args:
            level: Hint level (1-4)

        Returns:
            Hint object

        Levels:
        1. Piece type to move
        2. Source square
        3. Destination square
        4. Full move in SAN
        """
        move = self.solution_move
        piece = self.board.piece_at(move.from_square)

        if not piece:
            # Should not happen, but handle gracefully
            return Hint(
                level=4,
                message=f"Play {self.board.san(move)}",
                reveal_data={'move': self.board.san(move)}
            )

        if level == 1:
            # Piece to move
            piece_name = chess.piece_name(piece.piece_type).capitalize()
            return Hint(
                level=1,
                message=f"Move your {piece_name}",
                reveal_data={'piece_type': piece.piece_type}
            )

        elif level == 2:
            # Source square
            square_name = chess.square_name(move.from_square)
            piece_name = chess.piece_name(piece.piece_type).capitalize()
            return Hint(
                level=2,
                message=f"Move the {piece_name} from {square_name}",
                reveal_data={'from_square': square_name}
            )

        elif level == 3:
            # Destination square
            from_square = chess.square_name(move.from_square)
            to_square = chess.square_name(move.to_square)
            return Hint(
                level=3,
                message=f"Move from {from_square} to {to_square}",
                reveal_data={
                    'from_square': from_square,
                    'to_square': to_square
                }
            )

        else:  # level 4
            # Full move
            san = self.board.san(move)
            return Hint(
                level=4,
                message=f"Play {san}",
                reveal_data={
                    'move': san,
                    'from_square': chess.square_name(move.from_square),
                    'to_square': chess.square_name(move.to_square)
                }
            )

    def reset(self):
        """Reset hint level to 0"""
        self.current_level = 0
