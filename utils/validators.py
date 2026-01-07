"""
Input validation utilities
"""

from utils.exceptions import InvalidDifficultyError, InvalidGamePhaseError


class InputValidator:
    """Validates user inputs"""

    @staticmethod
    def validate_difficulty(value: str) -> int:
        """
        Validate difficulty input

        Args:
            value: User input string

        Returns:
            Validated difficulty (1-5)

        Raises:
            InvalidDifficultyError: If invalid
        """
        try:
            diff = int(value)
            if 1 <= diff <= 5:
                return diff
            raise InvalidDifficultyError("Difficulty must be between 1 and 5")
        except ValueError:
            raise InvalidDifficultyError(f"Invalid difficulty format: '{value}'. Must be a number 1-5")

    @staticmethod
    def validate_game_phase(value: str) -> str:
        """
        Validate and normalize game phase input

        Args:
            value: User input string

        Returns:
            Normalized game phase ('opening', 'middlegame', or 'endgame')

        Raises:
            InvalidGamePhaseError: If invalid
        """
        normalized = value.lower().strip()

        # Map aliases to canonical names
        phase_map = {
            'opening': 'opening',
            'early': 'opening',
            'open': 'opening',
            'middlegame': 'middlegame',
            'middle': 'middlegame',
            'mid': 'middlegame',
            'endgame': 'endgame',
            'end': 'endgame',
            'ending': 'endgame'
        }

        if normalized in phase_map:
            return phase_map[normalized]
        else:
            raise InvalidGamePhaseError(
                f"Invalid game phase: '{value}'. "
                "Must be 'opening' (or 'early'), 'middlegame' (or 'mid'), or 'endgame' (or 'end')"
            )

    @staticmethod
    def validate_yes_no(value: str) -> bool:
        """
        Validate yes/no input

        Args:
            value: User input string

        Returns:
            True for yes, False for no

        Raises:
            ValueError: If invalid
        """
        normalized = value.lower().strip()

        if normalized in ['y', 'yes', 'yeah', 'yep']:
            return True
        elif normalized in ['n', 'no', 'nope']:
            return False
        else:
            raise ValueError(f"Please enter 'y' or 'n'")
