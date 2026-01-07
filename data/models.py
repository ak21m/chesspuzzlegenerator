"""
Data models for chess puzzle generator
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import chess


@dataclass
class Puzzle:
    """Represents a chess puzzle"""
    puzzle_id: str
    fen: str                           # Position before opponent's move
    moves: List[str]                   # UCI format moves (solution sequence)
    rating: int
    rating_deviation: int
    popularity: int
    nb_plays: int
    themes: List[str]
    game_url: str
    opening_tags: List[str]
    piece_count: int                   # Calculated on import

    @property
    def initial_position_fen(self) -> str:
        """
        FEN after applying first move (position player sees)
        The first move is the opponent's move that creates the tactical opportunity
        """
        board = chess.Board(self.fen)
        first_move = chess.Move.from_uci(self.moves[0])
        board.push(first_move)
        return board.fen()

    @property
    def solution_moves(self) -> List[str]:
        """
        Solution moves (all moves except first)
        These are the moves the player needs to find
        """
        return self.moves[1:]

    @property
    def themes_str(self) -> str:
        """Comma-separated themes for display"""
        return ", ".join(self.themes)


@dataclass
class ProgressEntry:
    """Represents a solved puzzle attempt"""
    puzzle_id: str
    solved: bool
    attempts: int
    time_taken: float                  # Seconds
    difficulty: int                    # 1-5
    timestamp: datetime
    hints_used: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'puzzle_id': self.puzzle_id,
            'solved': self.solved,
            'attempts': self.attempts,
            'time_taken': self.time_taken,
            'difficulty': self.difficulty,
            'timestamp': self.timestamp.isoformat(),
            'hints_used': self.hints_used
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ProgressEntry':
        """Create from dictionary (JSON deserialization)"""
        return cls(
            puzzle_id=data['puzzle_id'],
            solved=data['solved'],
            attempts=data['attempts'],
            time_taken=data['time_taken'],
            difficulty=data['difficulty'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            hints_used=data.get('hints_used', 0)
        )


@dataclass
class UserProgress:
    """Aggregated user statistics"""
    total_solved: int = 0
    total_attempts: int = 0
    success_rate: float = 0.0
    current_streak: int = 0
    best_streak: int = 0
    solved_by_difficulty: dict = field(default_factory=lambda: {1: 0, 2: 0, 3: 0, 4: 0, 5: 0})
    solved_puzzles: set = field(default_factory=set)

    def __str__(self) -> str:
        """String representation for display"""
        lines = [
            "\n=== Your Statistics ===",
            f"Total Puzzles Solved: {self.total_solved}",
            f"Total Attempts: {self.total_attempts}",
            f"Success Rate: {self.success_rate:.1f}%",
            f"Current Streak: {self.current_streak}",
            f"Best Streak: {self.best_streak}",
            "",
            "Solved by Difficulty:",
        ]

        for diff in range(1, 6):
            count = self.solved_by_difficulty.get(diff, 0)
            lines.append(f"  Level {diff}: {count}")

        return "\n".join(lines)


@dataclass
class Hint:
    """Represents a hint for a puzzle"""
    level: int                         # 1-4
    message: str                       # Display message
    reveal_data: dict                  # Additional data for highlighting

    def __str__(self) -> str:
        return f"Hint: {self.message}"
