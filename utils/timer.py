"""
Timer utilities for puzzle solving
"""

import time
from typing import Optional
from datetime import timedelta


class PuzzleTimer:
    """
    Timer for tracking puzzle solve time
    Supports both countdown and stopwatch modes
    """

    def __init__(self, time_limit: Optional[int] = None):
        """
        Initialize timer

        Args:
            time_limit: Optional time limit in seconds (countdown mode)
                       If None, runs as stopwatch
        """
        self.time_limit = time_limit
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.is_running = False
        self.is_countdown = time_limit is not None

    def start(self):
        """Start the timer"""
        self.start_time = time.time()
        self.is_running = True
        self.end_time = None

    def stop(self) -> float:
        """
        Stop the timer

        Returns:
            Elapsed time in seconds
        """
        if not self.is_running:
            return 0.0

        self.end_time = time.time()
        self.is_running = False
        return self.get_elapsed()

    def get_elapsed(self) -> float:
        """
        Get elapsed time in seconds

        Returns:
            Elapsed time (or 0 if not started)
        """
        if not self.start_time:
            return 0.0

        end = self.end_time if self.end_time else time.time()
        return end - self.start_time

    def get_remaining(self) -> Optional[float]:
        """
        Get remaining time in countdown mode

        Returns:
            Remaining seconds or None if not countdown mode
        """
        if not self.is_countdown or not self.time_limit:
            return None

        if not self.is_running:
            return 0.0

        elapsed = self.get_elapsed()
        remaining = self.time_limit - elapsed
        return max(0.0, remaining)

    def is_time_up(self) -> bool:
        """
        Check if time limit has been reached (countdown mode)

        Returns:
            True if time is up, False otherwise
        """
        if not self.is_countdown:
            return False

        remaining = self.get_remaining()
        return remaining is not None and remaining <= 0

    def format_time(self, seconds: float) -> str:
        """
        Format time as MM:SS or HH:MM:SS

        Args:
            seconds: Time in seconds

        Returns:
            Formatted time string
        """
        td = timedelta(seconds=int(seconds))
        total_seconds = int(td.total_seconds())

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

    def get_formatted_elapsed(self) -> str:
        """
        Get formatted elapsed time

        Returns:
            Formatted elapsed time string
        """
        return self.format_time(self.get_elapsed())

    def get_formatted_remaining(self) -> str:
        """
        Get formatted remaining time (countdown mode)

        Returns:
            Formatted remaining time or empty string if not countdown
        """
        remaining = self.get_remaining()
        if remaining is None:
            return ""
        return self.format_time(remaining)

    def get_status(self) -> str:
        """
        Get timer status string

        Returns:
            Status string showing elapsed or remaining time
        """
        if not self.is_running:
            if self.end_time:
                return f"Completed in {self.get_formatted_elapsed()}"
            else:
                return "Not started"

        if self.is_countdown:
            remaining = self.get_remaining()
            if remaining is not None and remaining <= 0:
                return "Time's up!"
            return f"Time remaining: {self.get_formatted_remaining()}"
        else:
            return f"Elapsed: {self.get_formatted_elapsed()}"

    def reset(self):
        """Reset the timer"""
        self.start_time = None
        self.end_time = None
        self.is_running = False


class TimerStats:
    """
    Statistics for timed puzzle solving
    """

    def __init__(self):
        """Initialize timer stats"""
        self.times: list[float] = []
        self.fastest_time: Optional[float] = None
        self.slowest_time: Optional[float] = None
        self.average_time: float = 0.0

    def add_time(self, time_seconds: float):
        """
        Add a solve time

        Args:
            time_seconds: Time taken in seconds
        """
        self.times.append(time_seconds)

        # Update stats
        self.fastest_time = min(self.times)
        self.slowest_time = max(self.times)
        self.average_time = sum(self.times) / len(self.times)

    def get_stats_summary(self) -> dict:
        """
        Get statistics summary

        Returns:
            Dictionary with timing statistics
        """
        if not self.times:
            return {
                'count': 0,
                'fastest': None,
                'slowest': None,
                'average': None,
                'total': 0.0
            }

        return {
            'count': len(self.times),
            'fastest': self.fastest_time,
            'slowest': self.slowest_time,
            'average': self.average_time,
            'total': sum(self.times)
        }

    def format_stats(self) -> str:
        """
        Format statistics as string

        Returns:
            Formatted statistics string
        """
        if not self.times:
            return "No timed puzzles solved yet"

        stats = self.get_stats_summary()
        timer = PuzzleTimer()  # For formatting

        lines = [
            f"Puzzles solved: {stats['count']}",
            f"Fastest time: {timer.format_time(stats['fastest'])}",
            f"Slowest time: {timer.format_time(stats['slowest'])}",
            f"Average time: {timer.format_time(stats['average'])}",
            f"Total time: {timer.format_time(stats['total'])}"
        ]

        return "\n".join(lines)
