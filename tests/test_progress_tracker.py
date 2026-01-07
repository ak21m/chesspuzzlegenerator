"""
Tests for progress tracker component
"""

import pytest
import json
import os
import tempfile
from datetime import datetime

from core.progress_tracker import ProgressTracker
from data.models import ProgressEntry


@pytest.fixture
def temp_progress_file():
    """Create a temporary progress file"""
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
    temp_file.close()
    yield temp_file.name
    # Cleanup
    if os.path.exists(temp_file.name):
        os.remove(temp_file.name)


@pytest.fixture
def tracker(temp_progress_file):
    """Create a ProgressTracker instance"""
    return ProgressTracker(progress_file=temp_progress_file)


@pytest.fixture
def sample_entries():
    """Create sample progress entries"""
    return [
        ProgressEntry(
            puzzle_id="puzzle001",
            solved=True,
            attempts=1,
            time_taken=30.5,
            difficulty=2,
            timestamp=datetime.now().isoformat(),
            hints_used=0
        ),
        ProgressEntry(
            puzzle_id="puzzle002",
            solved=True,
            attempts=2,
            time_taken=45.2,
            difficulty=3,
            timestamp=datetime.now().isoformat(),
            hints_used=1
        ),
        ProgressEntry(
            puzzle_id="puzzle003",
            solved=False,
            attempts=3,
            time_taken=60.0,
            difficulty=3,
            timestamp=datetime.now().isoformat(),
            hints_used=2
        ),
        ProgressEntry(
            puzzle_id="puzzle004",
            solved=True,
            attempts=1,
            time_taken=25.0,
            difficulty=2,
            timestamp=datetime.now().isoformat(),
            hints_used=0
        ),
    ]


class TestProgressTracker:
    """Test suite for ProgressTracker"""

    def test_initial_stats_empty(self, tracker):
        """Test initial stats are empty"""
        stats = tracker.get_stats()

        assert stats["total_attempts"] == 0
        assert stats["total_solved"] == 0
        assert stats["success_rate"] == 0.0
        assert stats["current_streak"] == 0
        assert stats["best_streak"] == 0

    def test_add_single_entry(self, tracker):
        """Test adding a single progress entry"""
        entry = ProgressEntry(
            puzzle_id="test001",
            solved=True,
            attempts=1,
            time_taken=30.0,
            difficulty=2,
            timestamp=datetime.now().isoformat(),
            hints_used=0
        )

        tracker.add_entry(entry)
        stats = tracker.get_stats()

        assert stats["total_attempts"] == 1
        assert stats["total_solved"] == 1
        assert stats["success_rate"] == 100.0

    def test_add_multiple_entries(self, tracker, sample_entries):
        """Test adding multiple entries"""
        for entry in sample_entries:
            tracker.add_entry(entry)

        stats = tracker.get_stats()

        assert stats["total_attempts"] == 4
        assert stats["total_solved"] == 3
        assert stats["success_rate"] == 75.0  # 3 out of 4

    def test_current_streak_calculation(self, tracker):
        """Test current streak calculation"""
        # Add 3 consecutive solved puzzles
        for i in range(3):
            entry = ProgressEntry(
                puzzle_id=f"puzzle{i}",
                solved=True,
                attempts=1,
                time_taken=30.0,
                difficulty=2,
                timestamp=datetime.now().isoformat(),
                hints_used=0
            )
            tracker.add_entry(entry)

        stats = tracker.get_stats()
        assert stats["current_streak"] == 3

    def test_streak_breaks_on_failure(self, tracker):
        """Test that streak breaks when a puzzle is not solved"""
        # Add 2 solved
        for i in range(2):
            tracker.add_entry(ProgressEntry(
                puzzle_id=f"puzzle{i}",
                solved=True,
                attempts=1,
                time_taken=30.0,
                difficulty=2,
                timestamp=datetime.now().isoformat(),
                hints_used=0
            ))

        # Add 1 failed
        tracker.add_entry(ProgressEntry(
            puzzle_id="puzzle_fail",
            solved=False,
            attempts=2,
            time_taken=45.0,
            difficulty=3,
            timestamp=datetime.now().isoformat(),
            hints_used=1
        ))

        # Add 1 more solved
        tracker.add_entry(ProgressEntry(
            puzzle_id="puzzle3",
            solved=True,
            attempts=1,
            time_taken=30.0,
            difficulty=2,
            timestamp=datetime.now().isoformat(),
            hints_used=0
        ))

        stats = tracker.get_stats()
        assert stats["current_streak"] == 1  # Only the last one
        assert stats["best_streak"] == 2  # The first two

    def test_best_streak_tracking(self, tracker):
        """Test best streak is tracked correctly"""
        # Streak of 3
        for i in range(3):
            tracker.add_entry(ProgressEntry(
                puzzle_id=f"puzzle{i}",
                solved=True,
                attempts=1,
                time_taken=30.0,
                difficulty=2,
                timestamp=datetime.now().isoformat(),
                hints_used=0
            ))

        # Break
        tracker.add_entry(ProgressEntry(
            puzzle_id="break",
            solved=False,
            attempts=2,
            time_taken=45.0,
            difficulty=3,
            timestamp=datetime.now().isoformat(),
            hints_used=1
        ))

        # Streak of 5
        for i in range(5):
            tracker.add_entry(ProgressEntry(
                puzzle_id=f"puzzle_new{i}",
                solved=True,
                attempts=1,
                time_taken=30.0,
                difficulty=2,
                timestamp=datetime.now().isoformat(),
                hints_used=0
            ))

        stats = tracker.get_stats()
        assert stats["current_streak"] == 5
        assert stats["best_streak"] == 5  # Best is 5, not 3

    def test_difficulty_breakdown(self, tracker, sample_entries):
        """Test difficulty breakdown statistics"""
        for entry in sample_entries:
            tracker.add_entry(entry)

        stats = tracker.get_stats()
        breakdown = stats["by_difficulty"]

        # 2 difficulty-2 puzzles (both solved)
        assert breakdown[2]["solved"] == 2
        assert breakdown[2]["attempted"] == 2

        # 2 difficulty-3 puzzles (1 solved, 1 failed)
        assert breakdown[3]["solved"] == 1
        assert breakdown[3]["attempted"] == 2

    def test_get_solved_puzzle_ids(self, tracker, sample_entries):
        """Test retrieving set of solved puzzle IDs"""
        for entry in sample_entries:
            tracker.add_entry(entry)

        solved_ids = tracker.get_solved_puzzle_ids()

        assert "puzzle001" in solved_ids
        assert "puzzle002" in solved_ids
        assert "puzzle003" not in solved_ids  # This one failed
        assert "puzzle004" in solved_ids

    def test_persistence_saves_to_file(self, tracker, temp_progress_file):
        """Test that progress is saved to file"""
        entry = ProgressEntry(
            puzzle_id="test_persist",
            solved=True,
            attempts=1,
            time_taken=30.0,
            difficulty=2,
            timestamp=datetime.now().isoformat(),
            hints_used=0
        )

        tracker.add_entry(entry)

        # Check file exists and has content
        assert os.path.exists(temp_progress_file)
        with open(temp_progress_file, 'r') as f:
            data = json.load(f)
            assert "entries" in data
            assert len(data["entries"]) == 1

    def test_persistence_loads_from_file(self, temp_progress_file):
        """Test that progress is loaded from existing file"""
        # Create initial data
        initial_data = {
            "entries": [
                {
                    "puzzle_id": "existing001",
                    "solved": True,
                    "attempts": 1,
                    "time_taken": 30.0,
                    "difficulty": 2,
                    "timestamp": datetime.now().isoformat(),
                    "hints_used": 0
                }
            ]
        }

        with open(temp_progress_file, 'w') as f:
            json.dump(initial_data, f)

        # Create tracker (should load existing data)
        tracker = ProgressTracker(progress_file=temp_progress_file)
        stats = tracker.get_stats()

        assert stats["total_attempts"] == 1
        assert stats["total_solved"] == 1

    def test_average_time_calculation(self, tracker, sample_entries):
        """Test average time calculation"""
        for entry in sample_entries:
            tracker.add_entry(entry)

        stats = tracker.get_stats()

        # Average of [30.5, 45.2, 60.0, 25.0]
        expected_avg = (30.5 + 45.2 + 60.0 + 25.0) / 4
        assert abs(stats["avg_time"] - expected_avg) < 0.1

    def test_average_attempts_calculation(self, tracker, sample_entries):
        """Test average attempts calculation"""
        for entry in sample_entries:
            tracker.add_entry(entry)

        stats = tracker.get_stats()

        # Average of [1, 2, 3, 1]
        expected_avg = (1 + 2 + 3 + 1) / 4
        assert abs(stats["avg_attempts"] - expected_avg) < 0.1

    def test_total_hints_used(self, tracker, sample_entries):
        """Test total hints used calculation"""
        for entry in sample_entries:
            tracker.add_entry(entry)

        stats = tracker.get_stats()

        # Total: 0 + 1 + 2 + 0 = 3
        assert stats["total_hints_used"] == 3

    def test_empty_stats_structure(self, tracker):
        """Test that stats have correct structure even when empty"""
        stats = tracker.get_stats()

        required_keys = [
            "total_attempts",
            "total_solved",
            "success_rate",
            "current_streak",
            "best_streak",
            "by_difficulty",
            "avg_time",
            "avg_attempts",
            "total_hints_used"
        ]

        for key in required_keys:
            assert key in stats

    def test_difficulty_breakdown_structure(self, tracker):
        """Test difficulty breakdown has correct structure"""
        # Add entry for difficulty 3
        tracker.add_entry(ProgressEntry(
            puzzle_id="test",
            solved=True,
            attempts=1,
            time_taken=30.0,
            difficulty=3,
            timestamp=datetime.now().isoformat(),
            hints_used=0
        ))

        stats = tracker.get_stats()
        breakdown = stats["by_difficulty"]

        # Should have entries for all 5 difficulty levels
        for i in range(1, 6):
            assert i in breakdown
            assert "attempted" in breakdown[i]
            assert "solved" in breakdown[i]

    def test_success_rate_with_no_attempts(self, tracker):
        """Test success rate when no attempts"""
        stats = tracker.get_stats()
        assert stats["success_rate"] == 0.0

    def test_success_rate_with_all_failed(self, tracker):
        """Test success rate when all puzzles failed"""
        for i in range(3):
            tracker.add_entry(ProgressEntry(
                puzzle_id=f"fail{i}",
                solved=False,
                attempts=2,
                time_taken=45.0,
                difficulty=2,
                timestamp=datetime.now().isoformat(),
                hints_used=1
            ))

        stats = tracker.get_stats()
        assert stats["success_rate"] == 0.0
        assert stats["total_attempts"] == 3
        assert stats["total_solved"] == 0

    def test_success_rate_with_all_solved(self, tracker):
        """Test success rate when all puzzles solved"""
        for i in range(3):
            tracker.add_entry(ProgressEntry(
                puzzle_id=f"solve{i}",
                solved=True,
                attempts=1,
                time_taken=30.0,
                difficulty=2,
                timestamp=datetime.now().isoformat(),
                hints_used=0
            ))

        stats = tracker.get_stats()
        assert stats["success_rate"] == 100.0

    def test_data_integrity_after_multiple_operations(self, tracker):
        """Test data remains consistent after multiple operations"""
        # Add some entries
        for i in range(5):
            tracker.add_entry(ProgressEntry(
                puzzle_id=f"puzzle{i}",
                solved=i % 2 == 0,  # Alternate solved/failed
                attempts=1,
                time_taken=30.0,
                difficulty=2,
                timestamp=datetime.now().isoformat(),
                hints_used=0
            ))

        # Get stats multiple times
        stats1 = tracker.get_stats()
        stats2 = tracker.get_stats()

        # Should be consistent
        assert stats1 == stats2
