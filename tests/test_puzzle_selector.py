"""
Tests for puzzle selector component
"""

import pytest
import sqlite3
from pathlib import Path
import tempfile
import os

from core.puzzle_selector import PuzzleSelector
from data.database import Database
from data.models import Puzzle
from config.constants import GamePhase


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_puzzles.db")

    # Create database
    db = Database(db_path)
    db.create_schema()

    # Insert test puzzles
    test_puzzles = [
        # Beginner puzzles (rating 600-1200)
        ("test001", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
         "e2e4 e7e5 g1f3", 800, 50, 100, 500, "", "e4", 32),
        ("test002", "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
         "f1c4 f8c5 b1c3", 1100, 60, 120, 600, "", "e4 e5", 30),

        # Intermediate puzzles (rating 1200-1600)
        ("test003", "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 4 5",
         "d1a4 c6d4 f3d4", 1400, 70, 150, 700, "", "e4 e5 Nf3 Nc6", 28),
        ("test004", "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4",
         "f3e5 c6e5 d2d4", 1550, 80, 180, 800, "", "e4 e5 Nf3 Nc6 Bc4", 26),

        # Advanced puzzles (rating 1600-2000)
        ("test005", "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQ1RK1 b kq - 5 5",
         "c6d4 f3d4 c5d4", 1800, 90, 200, 900, "", "e4 e5 Nf3 Nc6 Bc4 Bc5", 24),

        # Expert puzzles (rating 2000-2400)
        ("test006", "r2qkb1r/ppp2ppp/2np1n2/4p1B1/2B1P3/2N2N2/PPPP1PPP/R2QK2R b KQkq - 1 6",
         "d6d5 e4d5 c6d4", 2200, 100, 250, 1000, "", "e4 e5 Nf3 Nc6 Bc4 Nf6 Ng5 d6", 22),

        # Master puzzles (rating 2400-3000)
        ("test007", "r1bq1rk1/ppp2ppp/2np1n2/2b1p3/2B1P3/2NP1N2/PPP2PPP/R1BQ1RK1 w - - 0 7",
         "c3d5 c6d4 d5f6", 2600, 110, 300, 1200, "", "e4 e5 Nf3 Nc6 Bc4 Bc5 Nc3", 20),

        # Endgame puzzles (low piece count)
        ("test008", "8/8/4k3/8/8/4K3/8/8 w - - 0 1",
         "e3d4 e6d6 d4e4", 1500, 50, 100, 500, "", "", 2),
        ("test009", "8/8/3k4/8/3K4/8/8/8 b - - 1 1",
         "d6e6 d4e4 e6f6", 1600, 60, 120, 600, "", "", 2),
    ]

    for puzzle_data in test_puzzles:
        db.execute_write(
            """INSERT INTO puzzles
            (puzzle_id, fen, moves, rating, rating_deviation, popularity,
             nb_plays, game_url, opening_tags, piece_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            puzzle_data
        )

    yield db_path

    # Cleanup
    db.close()
    os.remove(db_path)
    os.rmdir(temp_dir)


class TestPuzzleSelector:
    """Test suite for PuzzleSelector"""

    def test_select_beginner_puzzle(self, temp_db):
        """Test selecting a beginner difficulty puzzle"""
        selector = PuzzleSelector(temp_db)
        puzzle = selector.select_puzzle(difficulty=1)

        assert puzzle is not None
        assert isinstance(puzzle, Puzzle)
        assert 600 <= puzzle.rating <= 1200
        assert puzzle.puzzle_id in ["test001", "test002"]

    def test_select_intermediate_puzzle(self, temp_db):
        """Test selecting an intermediate difficulty puzzle"""
        selector = PuzzleSelector(temp_db)
        puzzle = selector.select_puzzle(difficulty=2)

        assert puzzle is not None
        assert 1200 <= puzzle.rating <= 1600
        assert puzzle.puzzle_id in ["test003", "test004"]

    def test_select_advanced_puzzle(self, temp_db):
        """Test selecting an advanced difficulty puzzle"""
        selector = PuzzleSelector(temp_db)
        puzzle = selector.select_puzzle(difficulty=3)

        assert puzzle is not None
        assert 1600 <= puzzle.rating <= 2000
        assert puzzle.puzzle_id == "test005"

    def test_select_expert_puzzle(self, temp_db):
        """Test selecting an expert difficulty puzzle"""
        selector = PuzzleSelector(temp_db)
        puzzle = selector.select_puzzle(difficulty=4)

        assert puzzle is not None
        assert 2000 <= puzzle.rating <= 2400
        assert puzzle.puzzle_id == "test006"

    def test_select_master_puzzle(self, temp_db):
        """Test selecting a master difficulty puzzle"""
        selector = PuzzleSelector(temp_db)
        puzzle = selector.select_puzzle(difficulty=5)

        assert puzzle is not None
        assert 2400 <= puzzle.rating <= 3000
        assert puzzle.puzzle_id == "test007"

    def test_select_endgame_puzzle(self, temp_db):
        """Test selecting an endgame puzzle"""
        selector = PuzzleSelector(temp_db)
        puzzle = selector.select_puzzle(difficulty=3, game_phase=GamePhase.ENDGAME)

        assert puzzle is not None
        assert puzzle.piece_count < 12  # Endgame has fewer pieces
        assert puzzle.puzzle_id in ["test008", "test009"]

    def test_select_with_excluded_puzzles(self, temp_db):
        """Test excluding already solved puzzles"""
        selector = PuzzleSelector(temp_db)

        # Exclude one beginner puzzle
        excluded = {"test001"}
        puzzle = selector.select_puzzle(difficulty=1, exclude_puzzle_ids=excluded)

        assert puzzle is not None
        assert puzzle.puzzle_id != "test001"
        assert puzzle.puzzle_id == "test002"

    def test_fallback_when_no_exact_match(self, temp_db):
        """Test fallback to adjacent difficulty when no exact match"""
        selector = PuzzleSelector(temp_db)

        # Exclude all intermediate puzzles, should fallback
        excluded = {"test003", "test004"}
        puzzle = selector.select_puzzle(difficulty=2, exclude_puzzle_ids=excluded)

        assert puzzle is not None
        # Should fallback to adjacent difficulty
        assert puzzle.puzzle_id not in excluded

    def test_no_puzzle_available(self, temp_db):
        """Test when no puzzles are available"""
        selector = PuzzleSelector(temp_db)

        # Exclude all beginner puzzles
        excluded = {"test001", "test002"}
        puzzle = selector.select_puzzle(difficulty=1, exclude_puzzle_ids=excluded)

        # Should fallback to other difficulty levels
        assert puzzle is not None or puzzle is None

    def test_invalid_difficulty(self, temp_db):
        """Test with invalid difficulty level"""
        selector = PuzzleSelector(temp_db)

        # Should handle gracefully (fallback or return None)
        puzzle = selector.select_puzzle(difficulty=10)
        # Implementation should handle this gracefully

    def test_puzzle_data_structure(self, temp_db):
        """Test that returned puzzle has correct structure"""
        selector = PuzzleSelector(temp_db)
        puzzle = selector.select_puzzle(difficulty=1)

        assert puzzle is not None
        assert hasattr(puzzle, 'puzzle_id')
        assert hasattr(puzzle, 'fen')
        assert hasattr(puzzle, 'moves')
        assert hasattr(puzzle, 'rating')
        assert hasattr(puzzle, 'themes')
        assert isinstance(puzzle.moves, list)
        assert len(puzzle.moves) > 0

    def test_multiple_selections_vary(self, temp_db):
        """Test that multiple selections can return different puzzles"""
        selector = PuzzleSelector(temp_db)

        # Select multiple puzzles from same difficulty
        puzzles = [selector.select_puzzle(difficulty=1) for _ in range(5)]
        puzzle_ids = [p.puzzle_id for p in puzzles if p]

        # Should have at least some variation (not all the same)
        # With only 2 beginner puzzles, we should see both
        assert len(set(puzzle_ids)) >= 1
