"""
Move validation logic for puzzle solving
"""

import chess
from typing import Tuple, Optional
from data.models import Puzzle
from utils.exceptions import InvalidMoveError


class MoveValidator:
    """
    Validates player moves against puzzle solution
    Handles multiple notation formats
    """

    def __init__(self, puzzle: Puzzle):
        """
        Initialize validator with puzzle

        Args:
            puzzle: Puzzle instance to validate against
        """
        self.puzzle = puzzle
        self.board = self._setup_board()
        self.solution_moves = puzzle.solution_moves
        self.current_move_index = 0

    def _setup_board(self) -> chess.Board:
        """
        Setup board with initial position

        The puzzle FEN shows position before opponent's move.
        We need to apply that first move to show the position
        the player should respond to.

        Returns:
            chess.Board ready for player's move
        """
        board = chess.Board(self.puzzle.fen)

        # Apply opponent's first move (creates the tactical opportunity)
        first_move = chess.Move.from_uci(self.puzzle.moves[0])
        board.push(first_move)

        return board

    def validate_move(self, user_input: str) -> Tuple[bool, str]:
        """
        Validate user move against expected solution

        Args:
            user_input: User's move in SAN or UCI notation

        Returns:
            Tuple of (is_correct, feedback_message)
        """
        # Parse user input
        try:
            move = self._parse_move(user_input)
        except InvalidMoveError as e:
            return False, str(e)

        # Check if legal
        if move not in self.board.legal_moves:
            return False, "Illegal move. That move is not allowed in this position."

        # Get expected move from solution
        if self.current_move_index >= len(self.solution_moves):
            return False, "Puzzle already complete!"

        expected_uci = self.solution_moves[self.current_move_index]
        expected_move = chess.Move.from_uci(expected_uci)

        # Compare moves
        if move != expected_move:
            expected_san = self.board.san(expected_move)
            return False, f"Incorrect. Try again or type 'hint' for help."

        # Apply correct move
        self.board.push(move)
        self.current_move_index += 1

        # Check if puzzle complete
        if self.is_complete():
            return True, "Puzzle solved! Well done!"

        # Make opponent's response (if exists)
        if self.current_move_index < len(self.solution_moves):
            opponent_move_uci = self.solution_moves[self.current_move_index]
            opponent_move = chess.Move.from_uci(opponent_move_uci)
            self.board.push(opponent_move)
            self.current_move_index += 1

            # Check if that was the final move
            if self.is_complete():
                return True, "Puzzle solved! Well done!"
            else:
                return True, "Correct! Continue..."
        else:
            # Player's move was the final move
            return True, "Puzzle solved! Well done!"

    def _parse_move(self, user_input: str) -> chess.Move:
        """
        Parse move from user input (SAN or UCI)

        Args:
            user_input: User's move string

        Returns:
            chess.Move object

        Raises:
            InvalidMoveError: If move cannot be parsed
        """
        user_input = user_input.strip()

        # Try SAN first (most common format)
        try:
            move = self.board.parse_san(user_input)
            return move
        except ValueError:
            pass

        # Try UCI format
        try:
            move = chess.Move.from_uci(user_input)
            # Verify it's valid for this position
            if move in self.board.legal_moves:
                return move
        except ValueError:
            pass

        # Could not parse
        raise InvalidMoveError(
            f"Invalid move format: '{user_input}'. "
            "Use algebraic notation like 'Nf3', 'e4', 'Qxd5', or UCI like 'g1f3'"
        )

    def is_complete(self) -> bool:
        """Check if all solution moves have been played"""
        return self.current_move_index >= len(self.solution_moves)

    def get_current_board(self) -> chess.Board:
        """
        Get current board state (copy)

        Returns:
            Copy of current board
        """
        return self.board.copy()

    def get_current_solution_move(self) -> Optional[str]:
        """
        Get current expected solution move (UCI format)

        Returns:
            UCI move string or None if puzzle complete
        """
        if self.current_move_index >= len(self.solution_moves):
            return None
        return self.solution_moves[self.current_move_index]

    def get_moves_remaining(self) -> int:
        """Get number of moves remaining in solution"""
        return max(0, len(self.solution_moves) - self.current_move_index)

    def reset(self):
        """Reset validator to initial state"""
        self.board = self._setup_board()
        self.current_move_index = 0
