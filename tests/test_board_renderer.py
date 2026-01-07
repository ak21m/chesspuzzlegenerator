"""
Tests for board renderer component
"""

import pytest
import chess
import os
import tempfile
from pathlib import Path

from rendering.board_renderer import BoardRenderer
from data.models import Hint


@pytest.fixture
def temp_output_dir():
    """Create a temporary output directory"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir

    # Cleanup - remove all PNG files
    for file in Path(temp_dir).glob("*.png"):
        file.unlink()
    os.rmdir(temp_dir)


@pytest.fixture
def renderer(temp_output_dir):
    """Create a BoardRenderer instance"""
    return BoardRenderer(output_dir=temp_output_dir, size=512)


@pytest.fixture
def starting_board():
    """Create a starting position board"""
    return chess.Board()


@pytest.fixture
def test_board():
    """Create a test board position"""
    return chess.Board("r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4")


class TestBoardRenderer:
    """Test suite for BoardRenderer"""

    def test_render_starting_position(self, renderer, starting_board, temp_output_dir):
        """Test rendering the starting chess position"""
        output_path = renderer.render_position(
            board=starting_board,
            filename="start.png"
        )

        assert os.path.exists(output_path)
        assert output_path == os.path.join(temp_output_dir, "start.png")

        # Check file size (should be non-empty)
        assert os.path.getsize(output_path) > 0

    def test_render_with_orientation_white(self, renderer, test_board, temp_output_dir):
        """Test rendering from white's perspective"""
        output_path = renderer.render_position(
            board=test_board,
            filename="white_view.png",
            orientation=chess.WHITE
        )

        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0

    def test_render_with_orientation_black(self, renderer, test_board, temp_output_dir):
        """Test rendering from black's perspective"""
        output_path = renderer.render_position(
            board=test_board,
            filename="black_view.png",
            orientation=chess.BLACK
        )

        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0

    def test_render_with_highlighted_squares(self, renderer, test_board, temp_output_dir):
        """Test rendering with highlighted squares"""
        highlight_squares = [chess.E4, chess.E5]  # Highlight e4 and e5

        output_path = renderer.render_position(
            board=test_board,
            filename="highlighted.png",
            highlight_squares=highlight_squares
        )

        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0

    def test_render_with_arrows(self, renderer, test_board, temp_output_dir):
        """Test rendering with arrows"""
        arrows = [chess.svg.Arrow(chess.E2, chess.E4)]  # Arrow from e2 to e4

        output_path = renderer.render_position(
            board=test_board,
            filename="with_arrows.png",
            arrows=arrows
        )

        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0

    def test_render_puzzle_without_hint(self, renderer, test_board, temp_output_dir):
        """Test rendering a puzzle without hints"""
        output_path = renderer.render_puzzle(
            board=test_board,
            puzzle_id="test123"
        )

        assert os.path.exists(output_path)
        assert "puzzle_test123.png" in output_path

    def test_render_puzzle_with_hint_level_1(self, renderer, test_board, temp_output_dir):
        """Test rendering puzzle with level 1 hint (no visual changes)"""
        hint = Hint(
            level=1,
            message="Move your knight",
            reveal_data={"piece_type": "knight"}
        )

        output_path = renderer.render_puzzle(
            board=test_board,
            puzzle_id="test123",
            hint=hint
        )

        assert os.path.exists(output_path)
        assert "puzzle_test123_hint1.png" in output_path

    def test_render_puzzle_with_hint_level_2(self, renderer, test_board, temp_output_dir):
        """Test rendering puzzle with level 2 hint (source square highlighted)"""
        hint = Hint(
            level=2,
            message="From f3",
            reveal_data={"piece_type": "knight", "from_square": "f3"}
        )

        output_path = renderer.render_puzzle(
            board=test_board,
            puzzle_id="test123",
            hint=hint
        )

        assert os.path.exists(output_path)
        assert "puzzle_test123_hint2.png" in output_path

    def test_render_puzzle_with_hint_level_3(self, renderer, test_board, temp_output_dir):
        """Test rendering puzzle with level 3 hint (both squares highlighted)"""
        hint = Hint(
            level=3,
            message="To e5",
            reveal_data={"piece_type": "knight", "from_square": "f3", "to_square": "e5"}
        )

        output_path = renderer.render_puzzle(
            board=test_board,
            puzzle_id="test123",
            hint=hint
        )

        assert os.path.exists(output_path)
        assert "puzzle_test123_hint3.png" in output_path

    def test_render_puzzle_with_hint_level_4(self, renderer, test_board, temp_output_dir):
        """Test rendering puzzle with level 4 hint (arrow shown)"""
        hint = Hint(
            level=4,
            message="Play Nxe5",
            reveal_data={"piece_type": "knight", "from_square": "f3", "to_square": "e5", "move_san": "Nxe5"}
        )

        output_path = renderer.render_puzzle(
            board=test_board,
            puzzle_id="test123",
            hint=hint
        )

        assert os.path.exists(output_path)
        assert "puzzle_test123_hint4.png" in output_path

    def test_render_solution(self, renderer, test_board, temp_output_dir):
        """Test rendering solution with arrows"""
        solution_moves = ["f3e5", "c6e5", "d2d4"]

        output_path = renderer.render_solution(
            board=test_board,
            puzzle_id="test123",
            solution_moves=solution_moves
        )

        assert os.path.exists(output_path)
        assert "puzzle_test123_solution.png" in output_path

    def test_render_simple_from_fen(self, renderer, temp_output_dir):
        """Test rendering from FEN string"""
        fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"

        output_path = renderer.render_simple(
            fen=fen,
            filename="from_fen.png"
        )

        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0

    def test_render_simple_invalid_fen(self, renderer):
        """Test rendering with invalid FEN string"""
        from utils.exceptions import RenderError

        invalid_fen = "invalid fen string"

        with pytest.raises(RenderError):
            renderer.render_simple(
                fen=invalid_fen,
                filename="invalid.png"
            )

    def test_cleanup_old_images(self, renderer, test_board, temp_output_dir):
        """Test cleaning up old images"""
        # Create multiple images
        for i in range(15):
            renderer.render_position(
                board=test_board,
                filename=f"test_{i}.png"
            )

        # Should have 15 images
        images_before = list(Path(temp_output_dir).glob("*.png"))
        assert len(images_before) == 15

        # Cleanup, keep only 10
        renderer.cleanup_old_images(keep_count=10)

        # Should have exactly 10 images
        images_after = list(Path(temp_output_dir).glob("*.png"))
        assert len(images_after) == 10

    def test_board_size(self, temp_output_dir):
        """Test custom board size"""
        custom_renderer = BoardRenderer(output_dir=temp_output_dir, size=256)
        board = chess.Board()

        output_path = custom_renderer.render_position(
            board=board,
            filename="small_board.png"
        )

        assert os.path.exists(output_path)
        # Size check would require image library to verify dimensions

    def test_multiple_renders_same_filename(self, renderer, test_board, temp_output_dir):
        """Test that rendering overwrites existing file"""
        filename = "overwrite_test.png"

        # First render
        path1 = renderer.render_position(board=test_board, filename=filename)
        size1 = os.path.getsize(path1)

        # Second render (different position)
        different_board = chess.Board()
        path2 = renderer.render_position(board=different_board, filename=filename)
        size2 = os.path.getsize(path2)

        # Same path, possibly different size
        assert path1 == path2
        assert os.path.exists(path1)

    def test_output_directory_creation(self, temp_output_dir):
        """Test that output directory is created if it doesn't exist"""
        new_dir = os.path.join(temp_output_dir, "new_subdir")
        renderer = BoardRenderer(output_dir=new_dir)

        assert os.path.exists(new_dir)
        assert os.path.isdir(new_dir)

        # Cleanup
        os.rmdir(new_dir)

    def test_render_endgame_position(self, renderer, temp_output_dir):
        """Test rendering an endgame position"""
        endgame_board = chess.Board("8/5k2/8/8/8/8/5K2/8 w - - 0 1")

        output_path = renderer.render_position(
            board=endgame_board,
            filename="endgame.png"
        )

        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0

    def test_render_complex_position(self, renderer, temp_output_dir):
        """Test rendering a complex middlegame position"""
        complex_board = chess.Board(
            "r1bq1rk1/ppp2ppp/2np1n2/2b1p3/2B1P3/2NP1N2/PPP2PPP/R1BQ1RK1 w - - 0 7"
        )

        output_path = renderer.render_position(
            board=complex_board,
            filename="complex.png",
            highlight_squares=[chess.E4, chess.E5, chess.C4, chess.C5]
        )

        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0
