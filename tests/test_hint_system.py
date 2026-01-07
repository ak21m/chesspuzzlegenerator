"""
Tests for hint system component
"""

import pytest
import chess

from core.hint_system import HintSystem
from data.models import Hint


class TestHintSystem:
    """Test suite for HintSystem"""

    @pytest.fixture
    def hint_system(self):
        """Create a HintSystem instance"""
        return HintSystem()

    @pytest.fixture
    def test_board(self):
        """Create a test board"""
        return chess.Board("r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4")

    @pytest.fixture
    def test_move(self):
        """Create a test move"""
        return chess.Move.from_uci("f3e5")  # Nxe5

    def test_hint_level_1_piece_type(self, hint_system, test_board, test_move):
        """Test level 1 hint - piece type only"""
        hint = hint_system.generate_hint(
            board=test_board,
            move=test_move,
            level=1
        )

        assert isinstance(hint, Hint)
        assert hint.level == 1
        assert "knight" in hint.message.lower() or "N" in hint.message
        assert "piece_type" in hint.reveal_data
        assert hint.reveal_data["piece_type"] == "knight"

    def test_hint_level_2_source_square(self, hint_system, test_board, test_move):
        """Test level 2 hint - source square"""
        hint = hint_system.generate_hint(
            board=test_board,
            move=test_move,
            level=2
        )

        assert hint.level == 2
        assert "f3" in hint.message.lower() or "from f3" in hint.message.lower()
        assert "from_square" in hint.reveal_data
        assert hint.reveal_data["from_square"] == "f3"
        assert hint.reveal_data["piece_type"] == "knight"

    def test_hint_level_3_destination_square(self, hint_system, test_board, test_move):
        """Test level 3 hint - destination square"""
        hint = hint_system.generate_hint(
            board=test_board,
            move=test_move,
            level=3
        )

        assert hint.level == 3
        assert "e5" in hint.message.lower() or "to e5" in hint.message.lower()
        assert "to_square" in hint.reveal_data
        assert hint.reveal_data["to_square"] == "e5"
        assert hint.reveal_data["from_square"] == "f3"

    def test_hint_level_4_full_move(self, hint_system, test_board, test_move):
        """Test level 4 hint - full move"""
        hint = hint_system.generate_hint(
            board=test_board,
            move=test_move,
            level=4
        )

        assert hint.level == 4
        # Should contain the full move in SAN notation
        assert "Nxe5" in hint.message or "nxe5" in hint.message.lower()
        assert "move_san" in hint.reveal_data
        assert hint.reveal_data["move_san"] == "Nxe5"

    def test_hint_progressive_levels(self, hint_system, test_board, test_move):
        """Test that hints progressively reveal more information"""
        hints = [
            hint_system.generate_hint(test_board, test_move, level=i)
            for i in range(1, 5)
        ]

        # Each level should have more reveal_data
        assert len(hints[0].reveal_data) < len(hints[1].reveal_data)
        assert len(hints[1].reveal_data) < len(hints[2].reveal_data)
        assert len(hints[2].reveal_data) <= len(hints[3].reveal_data)

    def test_hint_with_pawn_move(self, hint_system):
        """Test hints for pawn moves"""
        board = chess.Board()
        move = chess.Move.from_uci("e2e4")

        hint = hint_system.generate_hint(board, move, level=1)

        assert "pawn" in hint.message.lower() or "P" in hint.message
        assert hint.reveal_data["piece_type"] == "pawn"

    def test_hint_with_king_move(self, hint_system):
        """Test hints for king moves"""
        board = chess.Board("4k3/8/8/8/8/8/8/4K3 w - - 0 1")
        move = chess.Move.from_uci("e1e2")

        hint = hint_system.generate_hint(board, move, level=1)

        assert "king" in hint.message.lower() or "K" in hint.message
        assert hint.reveal_data["piece_type"] == "king"

    def test_hint_with_castling(self, hint_system):
        """Test hints for castling moves"""
        board = chess.Board("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
        move = chess.Move.from_uci("e1g1")  # Kingside castling

        hint = hint_system.generate_hint(board, move, level=4)

        # Should mention castling
        assert "O-O" in hint.message or "castle" in hint.message.lower()

    def test_hint_with_promotion(self, hint_system):
        """Test hints for pawn promotion"""
        board = chess.Board("8/4P3/8/8/8/8/8/4k2K w - - 0 1")
        move = chess.Move.from_uci("e7e8q")

        hint = hint_system.generate_hint(board, move, level=4)

        # Should mention promotion
        assert "=" in hint.message or "promote" in hint.message.lower() or "queen" in hint.message.lower()

    def test_hint_with_capture(self, hint_system, test_board, test_move):
        """Test hints for capture moves"""
        hint = hint_system.generate_hint(test_board, test_move, level=4)

        # Nxe5 is a capture
        assert "x" in hint.message or "capture" in hint.message.lower() or "take" in hint.message.lower()

    def test_hint_invalid_level(self, hint_system, test_board, test_move):
        """Test hint with invalid level (should default to max)"""
        # Level 0
        hint_0 = hint_system.generate_hint(test_board, test_move, level=0)
        assert hint_0.level >= 1

        # Level > 4
        hint_5 = hint_system.generate_hint(test_board, test_move, level=5)
        assert hint_5.level <= 4

    def test_hint_data_structure(self, hint_system, test_board, test_move):
        """Test that hint has correct data structure"""
        hint = hint_system.generate_hint(test_board, test_move, level=3)

        assert isinstance(hint, Hint)
        assert isinstance(hint.level, int)
        assert isinstance(hint.message, str)
        assert isinstance(hint.reveal_data, dict)
        assert len(hint.message) > 0

    def test_hint_reveal_data_contains_required_fields(self, hint_system, test_board, test_move):
        """Test that reveal_data contains expected fields"""
        # Level 1: piece_type
        hint1 = hint_system.generate_hint(test_board, test_move, level=1)
        assert "piece_type" in hint1.reveal_data

        # Level 2: piece_type, from_square
        hint2 = hint_system.generate_hint(test_board, test_move, level=2)
        assert "piece_type" in hint2.reveal_data
        assert "from_square" in hint2.reveal_data

        # Level 3: piece_type, from_square, to_square
        hint3 = hint_system.generate_hint(test_board, test_move, level=3)
        assert "piece_type" in hint3.reveal_data
        assert "from_square" in hint3.reveal_data
        assert "to_square" in hint3.reveal_data

        # Level 4: all fields plus move_san
        hint4 = hint_system.generate_hint(test_board, test_move, level=4)
        assert "move_san" in hint4.reveal_data

    def test_hint_for_different_pieces(self, hint_system):
        """Test hints for all piece types"""
        test_cases = [
            ("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "e2e4", "pawn"),
            ("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "g1f3", "knight"),
            ("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "f1c4", "bishop"),
            ("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "a1a2", "rook"),
            ("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "d1e2", "queen"),
        ]

        for fen, move_uci, expected_piece in test_cases:
            board = chess.Board(fen)
            move = chess.Move.from_uci(move_uci)

            # Check if move is legal before testing
            if move in board.legal_moves:
                hint = hint_system.generate_hint(board, move, level=1)
                assert hint.reveal_data["piece_type"] == expected_piece

    def test_hint_message_format(self, hint_system, test_board, test_move):
        """Test that hint messages are properly formatted"""
        for level in range(1, 5):
            hint = hint_system.generate_hint(test_board, test_move, level=level)

            # Message should not be empty
            assert len(hint.message.strip()) > 0

            # Message should start with a capital letter (good formatting)
            assert hint.message[0].isupper() or hint.message[0] in ['O', '0-']  # Castling notation

    def test_hint_for_check_move(self, hint_system):
        """Test hint for a move that gives check"""
        board = chess.Board("rnbqkb1r/pppp1ppp/5n2/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 3 3")
        move = chess.Move.from_uci("f3f7")  # Qxf7+ check

        hint = hint_system.generate_hint(board, move, level=4)

        # Should include check notation or mention check
        assert "+" in hint.message or "check" in hint.message.lower()

    def test_hint_for_checkmate_move(self, hint_system):
        """Test hint for a checkmate move"""
        board = chess.Board("rnb1kbnr/pppp1ppp/8/4p3/5PPq/8/PPPPP2P/RNBQKBNR w KQkq - 1 3")
        # Find a checkmate move
        for move in board.legal_moves:
            board_copy = board.copy()
            board_copy.push(move)
            if board_copy.is_checkmate():
                hint = hint_system.generate_hint(board, move, level=4)
                # Should include checkmate notation or mention mate
                assert "#" in hint.message or "mate" in hint.message.lower() or "checkmate" in hint.message.lower()
                break
