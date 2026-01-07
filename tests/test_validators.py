"""
Tests for input validators
"""

import pytest

from utils.validators import InputValidator
from utils.exceptions import InvalidDifficultyError, InvalidGamePhaseError


class TestInputValidator:
    """Test suite for InputValidator"""

    @pytest.fixture
    def validator(self):
        """Create an InputValidator instance"""
        return InputValidator()

    # ===== Difficulty Validation Tests =====

    def test_valid_difficulty_string(self, validator):
        """Test valid difficulty strings (1-5)"""
        for i in range(1, 6):
            difficulty = validator.validate_difficulty(str(i))
            assert difficulty == i

    def test_valid_difficulty_integer(self, validator):
        """Test valid difficulty as integers"""
        for i in range(1, 6):
            difficulty = validator.validate_difficulty(i)
            assert difficulty == i

    def test_invalid_difficulty_zero(self, validator):
        """Test difficulty level 0 (invalid)"""
        with pytest.raises(InvalidDifficultyError):
            validator.validate_difficulty("0")

    def test_invalid_difficulty_six(self, validator):
        """Test difficulty level 6 (invalid)"""
        with pytest.raises(InvalidDifficultyError):
            validator.validate_difficulty("6")

    def test_invalid_difficulty_negative(self, validator):
        """Test negative difficulty"""
        with pytest.raises(InvalidDifficultyError):
            validator.validate_difficulty("-1")

    def test_invalid_difficulty_non_numeric(self, validator):
        """Test non-numeric difficulty input"""
        with pytest.raises(InvalidDifficultyError):
            validator.validate_difficulty("easy")

    def test_invalid_difficulty_float(self, validator):
        """Test float difficulty input"""
        with pytest.raises(InvalidDifficultyError):
            validator.validate_difficulty("2.5")

    def test_invalid_difficulty_empty(self, validator):
        """Test empty difficulty string"""
        with pytest.raises(InvalidDifficultyError):
            validator.validate_difficulty("")

    # ===== Game Phase Validation Tests =====

    def test_valid_game_phase_opening(self, validator):
        """Test valid 'opening' game phase"""
        phase = validator.validate_game_phase("opening")
        assert phase == "opening"

    def test_valid_game_phase_early(self, validator):
        """Test valid 'early' alias for opening"""
        phase = validator.validate_game_phase("early")
        assert phase == "opening"

    def test_valid_game_phase_middlegame(self, validator):
        """Test valid 'middlegame' game phase"""
        phase = validator.validate_game_phase("middlegame")
        assert phase == "middlegame"

    def test_valid_game_phase_mid(self, validator):
        """Test valid 'mid' alias for middlegame"""
        phase = validator.validate_game_phase("mid")
        assert phase == "middlegame"

    def test_valid_game_phase_endgame(self, validator):
        """Test valid 'endgame' game phase"""
        phase = validator.validate_game_phase("endgame")
        assert phase == "endgame"

    def test_valid_game_phase_end(self, validator):
        """Test valid 'end' alias for endgame"""
        phase = validator.validate_game_phase("end")
        assert phase == "endgame"

    def test_game_phase_case_insensitive(self, validator):
        """Test game phase is case-insensitive"""
        assert validator.validate_game_phase("OPENING") == "opening"
        assert validator.validate_game_phase("Opening") == "opening"
        assert validator.validate_game_phase("MiDdLeGaMe") == "middlegame"
        assert validator.validate_game_phase("END") == "endgame"

    def test_invalid_game_phase(self, validator):
        """Test invalid game phase"""
        with pytest.raises(InvalidGamePhaseError):
            validator.validate_game_phase("invalid")

    def test_invalid_game_phase_empty(self, validator):
        """Test empty game phase"""
        with pytest.raises(InvalidGamePhaseError):
            validator.validate_game_phase("")

    def test_invalid_game_phase_numeric(self, validator):
        """Test numeric game phase (invalid)"""
        with pytest.raises(InvalidGamePhaseError):
            validator.validate_game_phase("123")

    # ===== Yes/No Validation Tests =====

    def test_yes_no_yes(self, validator):
        """Test 'yes' response"""
        assert validator.validate_yes_no("yes") is True
        assert validator.validate_yes_no("y") is True
        assert validator.validate_yes_no("Y") is True
        assert validator.validate_yes_no("YES") is True

    def test_yes_no_no(self, validator):
        """Test 'no' response"""
        assert validator.validate_yes_no("no") is False
        assert validator.validate_yes_no("n") is False
        assert validator.validate_yes_no("N") is False
        assert validator.validate_yes_no("NO") is False

    def test_yes_no_invalid(self, validator):
        """Test invalid yes/no response"""
        with pytest.raises(ValueError):
            validator.validate_yes_no("maybe")

    def test_yes_no_empty(self, validator):
        """Test empty yes/no response"""
        with pytest.raises(ValueError):
            validator.validate_yes_no("")

    def test_yes_no_numeric(self, validator):
        """Test numeric yes/no response"""
        with pytest.raises(ValueError):
            validator.validate_yes_no("1")

    # ===== Edge Cases and Special Inputs =====

    def test_whitespace_handling_difficulty(self, validator):
        """Test that whitespace is handled for difficulty"""
        difficulty = validator.validate_difficulty("  3  ")
        assert difficulty == 3

    def test_whitespace_handling_game_phase(self, validator):
        """Test that whitespace is handled for game phase"""
        phase = validator.validate_game_phase("  opening  ")
        assert phase == "opening"

    def test_whitespace_handling_yes_no(self, validator):
        """Test that whitespace is handled for yes/no"""
        assert validator.validate_yes_no("  yes  ") is True
        assert validator.validate_yes_no("  no  ") is False

    def test_multiple_validation_calls(self, validator):
        """Test multiple validation calls work correctly"""
        # Should work consistently
        for _ in range(5):
            assert validator.validate_difficulty("3") == 3
            assert validator.validate_game_phase("mid") == "middlegame"
            assert validator.validate_yes_no("y") is True

    # ===== Error Message Tests =====

    def test_difficulty_error_message(self, validator):
        """Test that difficulty error includes helpful message"""
        try:
            validator.validate_difficulty("10")
        except InvalidDifficultyError as e:
            error_msg = str(e)
            # Should mention valid range
            assert "1" in error_msg or "5" in error_msg

    def test_game_phase_error_message(self, validator):
        """Test that game phase error includes helpful message"""
        try:
            validator.validate_game_phase("invalid")
        except InvalidGamePhaseError as e:
            error_msg = str(e)
            # Should mention valid options
            assert "opening" in error_msg or "middlegame" in error_msg or "endgame" in error_msg

    def test_yes_no_error_message(self, validator):
        """Test that yes/no error includes helpful message"""
        try:
            validator.validate_yes_no("maybe")
        except ValueError as e:
            error_msg = str(e)
            # Should mention y/n or yes/no
            assert "y" in error_msg.lower() or "n" in error_msg.lower()

    # ===== Boundary Tests =====

    def test_difficulty_boundary_min(self, validator):
        """Test minimum difficulty boundary (1)"""
        assert validator.validate_difficulty("1") == 1

    def test_difficulty_boundary_max(self, validator):
        """Test maximum difficulty boundary (5)"""
        assert validator.validate_difficulty("5") == 5

    def test_difficulty_just_below_min(self, validator):
        """Test just below minimum difficulty (0)"""
        with pytest.raises(InvalidDifficultyError):
            validator.validate_difficulty("0")

    def test_difficulty_just_above_max(self, validator):
        """Test just above maximum difficulty (6)"""
        with pytest.raises(InvalidDifficultyError):
            validator.validate_difficulty("6")

    # ===== Type Tests =====

    def test_difficulty_returns_int(self, validator):
        """Test that validate_difficulty returns an integer"""
        result = validator.validate_difficulty("3")
        assert isinstance(result, int)

    def test_game_phase_returns_str(self, validator):
        """Test that validate_game_phase returns a string"""
        result = validator.validate_game_phase("opening")
        assert isinstance(result, str)

    def test_yes_no_returns_bool(self, validator):
        """Test that validate_yes_no returns a boolean"""
        result = validator.validate_yes_no("yes")
        assert isinstance(result, bool)

    # ===== Special Characters Tests =====

    def test_game_phase_with_special_chars(self, validator):
        """Test game phase with special characters"""
        with pytest.raises(InvalidGamePhaseError):
            validator.validate_game_phase("opening!")

    def test_difficulty_with_special_chars(self, validator):
        """Test difficulty with special characters"""
        with pytest.raises(InvalidDifficultyError):
            validator.validate_difficulty("3!")

    # ===== Unicode Tests =====

    def test_difficulty_unicode(self, validator):
        """Test difficulty with unicode characters"""
        with pytest.raises(InvalidDifficultyError):
            validator.validate_difficulty("３")  # Fullwidth digit 3

    # ===== None Input Tests =====

    def test_difficulty_none_input(self, validator):
        """Test difficulty with None input"""
        with pytest.raises((InvalidDifficultyError, TypeError, AttributeError)):
            validator.validate_difficulty(None)

    def test_game_phase_none_input(self, validator):
        """Test game phase with None input"""
        with pytest.raises((InvalidGamePhaseError, AttributeError)):
            validator.validate_game_phase(None)

    def test_yes_no_none_input(self, validator):
        """Test yes/no with None input"""
        with pytest.raises((ValueError, AttributeError)):
            validator.validate_yes_no(None)
