"""
Progress tracking and statistics
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Set
from data.models import ProgressEntry, UserProgress


class ProgressTracker:
    """
    Tracks and persists user progress
    Calculates statistics
    """

    def __init__(self, storage_path: str):
        """
        Initialize progress tracker

        Args:
            storage_path: Path to JSON file for storing progress
        """
        self.storage_path = Path(storage_path)
        self.entries: List[ProgressEntry] = []
        self.load()

    def load(self):
        """Load progress from JSON file"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.entries = [
                        ProgressEntry.from_dict(entry)
                        for entry in data.get('entries', [])
                    ]
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not load progress file: {e}")
                self.entries = []
        else:
            # Create empty file
            self.entries = []
            self.save()

    def save(self):
        """Persist progress to JSON file"""
        # Ensure directory exists
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'entries': [entry.to_dict() for entry in self.entries]
        }

        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)

    def record_attempt(
        self,
        puzzle_id: str,
        solved: bool,
        attempts: int,
        time_taken: float,
        difficulty: int,
        hints_used: int = 0
    ):
        """
        Record a puzzle attempt

        Args:
            puzzle_id: Puzzle ID
            solved: Whether puzzle was solved
            attempts: Number of move attempts
            time_taken: Time in seconds
            difficulty: Difficulty level (1-5)
            hints_used: Number of hints used
        """
        entry = ProgressEntry(
            puzzle_id=puzzle_id,
            solved=solved,
            attempts=attempts,
            time_taken=time_taken,
            difficulty=difficulty,
            timestamp=datetime.now(),
            hints_used=hints_used
        )
        self.entries.append(entry)
        self.save()

    def get_statistics(self) -> UserProgress:
        """
        Calculate comprehensive statistics

        Returns:
            UserProgress object with all statistics
        """
        solved_entries = [e for e in self.entries if e.solved]

        total_solved = len(solved_entries)
        total_attempts = len(self.entries)
        success_rate = (total_solved / total_attempts * 100) if total_attempts > 0 else 0.0

        # Calculate streaks
        current_streak = self._calculate_current_streak()
        best_streak = self._calculate_best_streak()

        # Breakdown by difficulty
        solved_by_diff = {i: 0 for i in range(1, 6)}
        for entry in solved_entries:
            if entry.difficulty in solved_by_diff:
                solved_by_diff[entry.difficulty] += 1

        # Get unique solved puzzle IDs
        solved_puzzles = {e.puzzle_id for e in solved_entries}

        return UserProgress(
            total_solved=total_solved,
            total_attempts=total_attempts,
            success_rate=success_rate,
            current_streak=current_streak,
            best_streak=best_streak,
            solved_by_difficulty=solved_by_diff,
            solved_puzzles=solved_puzzles
        )

    def _calculate_current_streak(self) -> int:
        """
        Count consecutive solved puzzles from most recent

        Returns:
            Current streak count
        """
        streak = 0
        for entry in reversed(self.entries):
            if entry.solved:
                streak += 1
            else:
                break
        return streak

    def _calculate_best_streak(self) -> int:
        """
        Find longest streak in history

        Returns:
            Best streak count
        """
        current = 0
        best = 0
        for entry in self.entries:
            if entry.solved:
                current += 1
                best = max(best, current)
            else:
                current = 0
        return best

    def get_solved_puzzle_ids(self) -> Set[str]:
        """
        Get set of solved puzzle IDs

        Returns:
            Set of puzzle IDs that have been solved
        """
        return {e.puzzle_id for e in self.entries if e.solved}

    def has_attempted_puzzle(self, puzzle_id: str) -> bool:
        """
        Check if puzzle has been attempted

        Args:
            puzzle_id: Puzzle ID

        Returns:
            True if attempted before
        """
        return any(e.puzzle_id == puzzle_id for e in self.entries)

    def has_solved_puzzle(self, puzzle_id: str) -> bool:
        """
        Check if puzzle has been solved

        Args:
            puzzle_id: Puzzle ID

        Returns:
            True if solved before
        """
        return any(e.puzzle_id == puzzle_id and e.solved for e in self.entries)

    def get_average_time(self, difficulty: int = None) -> float:
        """
        Get average solving time

        Args:
            difficulty: Optional difficulty filter

        Returns:
            Average time in seconds
        """
        entries = [e for e in self.entries if e.solved]

        if difficulty:
            entries = [e for e in entries if e.difficulty == difficulty]

        if not entries:
            return 0.0

        total_time = sum(e.time_taken for e in entries)
        return total_time / len(entries)

    def get_success_rate_by_difficulty(self, difficulty: int) -> float:
        """
        Get success rate for specific difficulty

        Args:
            difficulty: Difficulty level (1-5)

        Returns:
            Success rate as percentage
        """
        attempts = [e for e in self.entries if e.difficulty == difficulty]

        if not attempts:
            return 0.0

        solved = sum(1 for e in attempts if e.solved)
        return (solved / len(attempts)) * 100
