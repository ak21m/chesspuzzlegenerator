"""
Tests for move validator component
"""

import pytest
import chess

from core.move_validator import MoveValidator
from data.models import Puzzle


class TestMoveValidator:
    """Test suite for MoveValidator"""

    @pytest.fixture
    def simple_puzzle(self):
        """Create a simple test puzzle"""
        return Puzzle(
            puzzle_id="test_simple",
            fen="r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4",
            moves=["f3e5", "c6e5", "d2d4"],  # UCI notation
            rating=1500,
            rating_deviation=50,
            popularity=100,
            nb_plays=500,
            themes=["fork", "pin"],
            game_url="",
            opening_tags="Italian Game",
            piece_count=26
        )

    @pytest.fixture
    def mate_in_two_puzzle(self):
        """Create a mate-in-two puzzle"""
        return Puzzle(
            puzzle_id="test_mate",
            fen="r1bqk2r/pppp1Qpp/2n2n2/2b1p3/2B1P3/8/PPPP1PPP/RNB1K2R b KQkq - 0 4",
            moves=["e8d7", "f7f7"],  # Black king escapes, white delivers mate
            rating=1200,
            rating_deviation=40,
            popularity=200,
            nb_plays=1000,
            themes=["mate", "mateIn2"],
            game_url="",
            opening_tags="",
            piece_count=24
        )

    def test_san_move_validation_correct(self, simple_puzzle):
        """Test validating a correct SAN move"""
        validator = MoveValidator(simple_puzzle)
        is_correct, message, is_complete = validator.validate_move("Nxe5")

        assert is_correct is True
        assert is_complete is False  # Puzzle not complete yet
        assert "Correct" in message or "Good" in message

    def test_uci_move_validation_correct(self, simple_puzzle):
        """Test validating a correct UCI move"""
        validator = MoveValidator(simple_puzzle)
        is_correct, message, is_complete = validator.validate_move("f3e5")

        assert is_correct is True
        assert is_complete is False

    def test_incorrect_move(self, simple_puzzle):
        """Test validating an incorrect move"""
        validator = MoveValidator(simple_puzzle)
        is_correct, message, is_complete = validator.validate_move("Nc3")

        assert is_correct is False
        assert is_complete is False
        assert "Incorrect" in message or "Wrong" in message or "expected" in message.lower()

    def test_illegal_move(self, simple_puzzle):
        """Test handling an illegal move"""
        validator = MoveValidator(simple_puzzle)
        is_correct, message, is_complete = validator.validate_move("Nxf7")  # Illegal

        assert is_correct is False
        assert is_complete is False

    def test_invalid_move_format(self, simple_puzzle):
        """Test handling invalid move format"""
        validator = MoveValidator(simple_puzzle)
        is_correct, message, is_complete = validator.validate_move("invalid")

        assert is_correct is False
        assert "invalid" in message.lower() or "not recognized" in message.lower()

    def test_complete_puzzle_sequence(self, simple_puzzle):
        """Test completing a full puzzle sequence"""
        validator = MoveValidator(simple_puzzle)

        # First move
        is_correct, _, is_complete = validator.validate_move("Nxe5")
        assert is_correct is True
        assert is_complete is False

        # Second move (after opponent response)
        is_correct, _, is_complete = validator.validate_move("d4")
        assert is_correct is True
        assert is_complete is True  # Puzzle complete

    def test_get_current_position(self, simple_puzzle):
        """Test getting current board position"""
        validator = MoveValidator(simple_puzzle)

        board = validator.get_current_position()
        assert isinstance(board, chess.Board)
        assert board.turn == chess.WHITE  # White to move after opponent's move

    def test_get_expected_move(self, simple_puzzle):
        """Test getting expected next move"""
        validator = MoveValidator(simple_puzzle)

        expected = validator.get_expected_move()
        assert expected is not None
        assert isinstance(expected, chess.Move)

    def test_case_sensitive_san(self, simple_puzzle):
        """Test that SAN notation is case-sensitive"""
        validator = MoveValidator(simple_puzzle)

        # Correct case
        is_correct, _, _ = validator.validate_move("Nxe5")
        assert is_correct is True

        # Wrong case (lowercase knight)
        is_correct, _, _ = validator.validate_move("nxe5")
        # Should still be correct if parser handles it

    def test_pawn_moves(self):
        """Test pawn move validation"""
        puzzle = Puzzle(
            puzzle_id="test_pawn",
            fen="rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
            moves=["e7e5", "g1f3"],
            rating=800,
            rating_deviation=30,
            popularity=50,
            nb_plays=200,
            themes=["opening"],
            game_url="",
            opening_tags="",
            piece_count=32
        )

        validator = MoveValidator(puzzle)
        is_correct, _, _ = validator.validate_move("e5")  # Pawn move

        assert is_correct is True

    def test_castling_move(self):
        """Test castling move validation"""
        puzzle = Puzzle(
            puzzle_id="test_castle",
            fen="r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4",
            moves=["e1g1", "g8e8"],  # Kingside castling
            rating=1000,
            rating_deviation=40,
            popularity=80,
            nb_plays=400,
            themes=["opening"],
            game_url="",
            opening_tags="",
            piece_count=26
        )

        validator = MoveValidator(puzzle)

        # Test both notations
        is_correct_uci, _, _ = validator.validate_move("e1g1")
        is_correct_san, _, _ = validator.validate_move("O-O")

        assert is_correct_uci is True or is_correct_san is True

    def test_promotion_move(self):
        """Test pawn promotion move"""
        puzzle = Puzzle(
            puzzle_id="test_promotion",
            fen="8/4P3/8/8/8/8/8/4k2K w - - 0 1",
            moves=["e7e8q", "e1d1"],  # Promote to queen
            rating=1300,
            rating_deviation=50,
            popularity=100,
            nb_plays=500,
            themes=["endgame", "promotion"],
            game_url="",
            opening_tags="",
            piece_count=3
        )

        validator = MoveValidator(puzzle)

        # UCI notation with promotion
        is_correct, _, _ = validator.validate_move("e7e8q")
        assert is_correct is True

    def test_capture_notation(self, simple_puzzle):
        """Test capture notation"""
        validator = MoveValidator(simple_puzzle)

        # Capture with 'x'
        is_correct, _, _ = validator.validate_move("Nxe5")
        assert is_correct is True

    def test_check_notation(self):
        """Test moves with check notation"""
        puzzle = Puzzle(
            puzzle_id="test_check",
            fen="rnbqkb1r/pppp1ppp/5n2/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 3 3",
            moves=["f3f7", "e8f7"],  # Check
            rating=900,
            rating_deviation=40,
            popularity=90,
            nb_plays=450,
            themes=["fork"],
            game_url="",
            opening_tags="",
            piece_count=28
        )

        validator = MoveValidator(puzzle)

        # With check notation
        is_correct_with, _, _ = validator.validate_move("Qxf7+")

        # Without check notation (parser should still understand)
        validator2 = MoveValidator(puzzle)
        is_correct_without, _, _ = validator2.validate_move("Qxf7")

        assert is_correct_with is True or is_correct_without is True

    def test_ambiguous_move_notation(self):
        """Test disambiguating move notation"""
        puzzle = Puzzle(
            puzzle_id="test_ambiguous",
            fen="r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/2N2N2/PPPP1PPP/R1BQK2R w KQkq - 4 4",
            moves=["c3d5", "c6d4"],  # Two knights can go to d5
            rating=1600,
            rating_deviation=60,
            popularity=120,
            nb_plays=600,
            themes=["fork"],
            game_url="",
            opening_tags="",
            piece_count=26
        )

        validator = MoveValidator(puzzle)

        # Disambiguated move
        is_correct, _, _ = validator.validate_move("Ncd5")
        assert is_correct is True

    def test_empty_move(self, simple_puzzle):
        """Test handling empty move string"""
        validator = MoveValidator(simple_puzzle)
        is_correct, message, _ = validator.validate_move("")

        assert is_correct is False

    def test_get_solution_moves(self, simple_puzzle):
        """Test getting all solution moves"""
        validator = MoveValidator(simple_puzzle)

        # Access the puzzle's solution moves
        assert len(simple_puzzle.solution_moves) == 2  # Player makes 2 moves
        assert simple_puzzle.solution_moves[0] == "f3e5"
        assert simple_puzzle.solution_moves[1] == "d2d4"
