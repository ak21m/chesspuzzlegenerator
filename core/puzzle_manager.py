"""
Puzzle manager - orchestrates all game components
"""

import time
from typing import Optional, Tuple
import chess

from data.database import Database
from data.models import Puzzle, Hint, UserProgress
from core.puzzle_selector import PuzzleSelector
from core.move_validator import MoveValidator
from core.hint_system import HintSystem
from core.progress_tracker import ProgressTracker
from utils.exceptions import PuzzleNotFoundError
from utils.timer import PuzzleTimer


class PuzzleManager:
    """
    Main orchestrator for puzzle game
    Coordinates puzzle selection, validation, hints, and progress tracking
    """

    def __init__(self, db_path: str, progress_path: str, images_dir: str):
        """
        Initialize puzzle manager

        Args:
            db_path: Path to SQLite database
            progress_path: Path to progress JSON file
            images_dir: Directory for board images
        """
        self.db = Database(db_path)
        self.selector = PuzzleSelector(self.db)
        self.progress_tracker = ProgressTracker(progress_path)
        self.images_dir = images_dir

        # Current puzzle state
        self.current_puzzle: Optional[Puzzle] = None
        self.move_validator: Optional[MoveValidator] = None
        self.hint_system: Optional[HintSystem] = None
        self.start_time: Optional[float] = None
        self.move_attempts: int = 0
        self.hints_used: int = 0
        self.timer: Optional[PuzzleTimer] = None

    def start_puzzle(self, difficulty: int, game_phase: str, theme: Optional[str] = None,
                     timer_config: Optional[dict] = None) -> Puzzle:
        """
        Start a new puzzle

        Args:
            difficulty: Difficulty level (1-5)
            game_phase: Game phase ('opening', 'middlegame', 'endgame')
            theme: Optional theme filter
            timer_config: Optional timer configuration dict with 'enabled' and 'time_limit'

        Returns:
            Selected puzzle

        Raises:
            PuzzleNotFoundError: If no puzzle available
        """
        # Get solved puzzle IDs to avoid repetition
        solved_ids = self.progress_tracker.get_solved_puzzle_ids()

        # Select puzzle
        puzzle = self.selector.select_puzzle(difficulty, game_phase, solved_ids, theme=theme)

        if not puzzle:
            raise PuzzleNotFoundError(
                f"No puzzles found for difficulty {difficulty} and phase {game_phase}"
            )

        # Initialize puzzle state
        self.current_puzzle = puzzle
        self.move_validator = MoveValidator(puzzle)
        self.start_time = time.time()
        self.move_attempts = 0
        self.hints_used = 0

        # Initialize hint system with first expected move
        current_move = self.move_validator.get_current_solution_move()
        if current_move:
            current_board = self.move_validator.get_current_board()
            self.hint_system = HintSystem(current_board, current_move)

        # Initialize timer if configured
        if timer_config and timer_config.get('enabled'):
            time_limit = timer_config.get('time_limit')
            self.timer = PuzzleTimer(time_limit=time_limit)
            self.timer.start()

        return puzzle

    def validate_move(self, user_input: str) -> Tuple[bool, str]:
        """
        Validate user's move

        Args:
            user_input: User's move input

        Returns:
            Tuple of (is_correct, feedback_message)
        """
        if not self.move_validator:
            return False, "No active puzzle"

        self.move_attempts += 1
        is_correct, message = self.move_validator.validate_move(user_input)

        # Update hint system if move was correct and puzzle continues
        if is_correct and not self.move_validator.is_complete():
            current_move = self.move_validator.get_current_solution_move()
            if current_move:
                current_board = self.move_validator.get_current_board()
                self.hint_system = HintSystem(current_board, current_move)

        return is_correct, message

    def get_hint(self) -> Optional[Hint]:
        """
        Get next hint for current position

        Returns:
            Hint object or None if no puzzle active
        """
        if not self.hint_system:
            return None

        self.hints_used += 1
        return self.hint_system.get_next_hint()

    def is_puzzle_complete(self) -> bool:
        """Check if current puzzle is complete"""
        if not self.move_validator:
            return False
        return self.move_validator.is_complete()

    def is_time_up(self) -> bool:
        """Check if time limit has been reached"""
        if not self.timer:
            return False
        return self.timer.is_time_up()

    def get_timer_status(self) -> str:
        """Get current timer status string"""
        if not self.timer:
            return ""
        return self.timer.get_status()

    def get_current_board(self) -> Optional[chess.Board]:
        """Get current board position"""
        if not self.move_validator:
            return None
        return self.move_validator.get_current_board()

    def finish_puzzle(self, quit_early: bool = False) -> dict:
        """
        Finish current puzzle and record progress

        Args:
            quit_early: If True, puzzle was not completed

        Returns:
            Dictionary with puzzle results
        """
        if not self.current_puzzle:
            return {}

        # Calculate time taken
        if self.timer:
            self.timer.stop()
            time_taken = self.timer.get_elapsed()
        else:
            time_taken = time.time() - self.start_time if self.start_time else 0.0

        # Determine if solved
        solved = self.move_validator.is_complete() if self.move_validator else False

        # Get difficulty from puzzle rating
        difficulty = self._rating_to_difficulty(self.current_puzzle.rating)

        # Record in progress tracker
        if not quit_early:
            self.progress_tracker.record_attempt(
                puzzle_id=self.current_puzzle.puzzle_id,
                solved=solved,
                attempts=self.move_attempts,
                time_taken=time_taken,
                difficulty=difficulty,
                hints_used=self.hints_used
            )

        # Build results
        results = {
            'puzzle': self.current_puzzle,
            'solved': solved,
            'attempts': self.move_attempts,
            'time_taken': time_taken,
            'hints_used': self.hints_used,
            'difficulty': difficulty
        }

        # Clear state
        self.current_puzzle = None
        self.move_validator = None
        self.hint_system = None
        self.start_time = None
        self.move_attempts = 0
        self.hints_used = 0
        self.timer = None

        return results

    def get_available_themes(self) -> list[tuple[str, int]]:
        """
        Get list of available themes with counts

        Returns:
            List of (theme_name, count) tuples
        """
        return self.selector.get_available_themes()

    def get_statistics(self) -> UserProgress:
        """
        Get user statistics

        Returns:
            UserProgress object
        """
        return self.progress_tracker.get_statistics()

    def _rating_to_difficulty(self, rating: int) -> int:
        """
        Convert rating to difficulty level

        Args:
            rating: Puzzle rating

        Returns:
            Difficulty level (1-5)
        """
        if rating < 1200:
            return 1
        elif rating < 1600:
            return 2
        elif rating < 2000:
            return 3
        elif rating < 2400:
            return 4
        else:
            return 5

    def close(self):
        """Close database connection"""
        self.db.close()

    def __enter__(self):
        """Context manager support"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        self.close()
