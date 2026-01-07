"""
User input handling and processing
"""

from typing import Optional, Tuple
from utils.validators import InputValidator
from utils.exceptions import InvalidDifficultyError, InvalidGamePhaseError


class InputHandler:
    """Handles user input with validation"""

    def __init__(self):
        """Initialize input handler"""
        self.validator = InputValidator()

    def get_menu_choice(self, min_choice: int = 1, max_choice: int = 4) -> Optional[int]:
        """
        Get menu choice from user

        Args:
            min_choice: Minimum valid choice
            max_choice: Maximum valid choice

        Returns:
            Choice number or None if invalid
        """
        try:
            choice_str = input("Enter your choice: ").strip()
            choice = int(choice_str)

            if min_choice <= choice <= max_choice:
                return choice
            else:
                print(f"Please enter a number between {min_choice} and {max_choice}")
                return None

        except ValueError:
            print("Please enter a valid number")
            return None
        except (KeyboardInterrupt, EOFError):
            return None

    def get_difficulty(self) -> Optional[int]:
        """
        Get difficulty level from user

        Returns:
            Difficulty (1-5) or None if cancelled
        """
        # Color codes
        CYAN = '\033[96m'
        YELLOW = '\033[93m'
        RESET = '\033[0m'

        print("\nSelect difficulty level:")
        print(f"  {CYAN}1{RESET} = Beginner {YELLOW}(600-1200){RESET}")
        print(f"  {CYAN}2{RESET} = Intermediate {YELLOW}(1200-1600){RESET}")
        print(f"  {CYAN}3{RESET} = Advanced {YELLOW}(1600-2000){RESET}")
        print(f"  {CYAN}4{RESET} = Expert {YELLOW}(2000-2400){RESET}")
        print(f"  {CYAN}5{RESET} = Master {YELLOW}(2400-3000){RESET}")

        while True:
            try:
                difficulty_str = input("\nEnter difficulty (1-5): ").strip()

                if not difficulty_str:
                    return None

                difficulty = self.validator.validate_difficulty(difficulty_str)
                return difficulty

            except InvalidDifficultyError as e:
                print(f"Error: {e}")
                continue
            except (KeyboardInterrupt, EOFError):
                print()
                return None

    def get_game_phase(self) -> Optional[str]:
        """
        Get game phase from user

        Returns:
            Game phase ('opening', 'middlegame', 'endgame') or None if cancelled
        """
        # Color codes
        CYAN = '\033[96m'
        RESET = '\033[0m'

        print("\nSelect game phase:")
        print(f"  {CYAN}1{RESET} = Opening positions")
        print(f"  {CYAN}2{RESET} = Middlegame positions")
        print(f"  {CYAN}3{RESET} = Endgame positions")

        while True:
            try:
                choice_str = input("\nGame phase (1-3): ").strip()

                if not choice_str:
                    return None

                choice = int(choice_str)

                if choice == 1:
                    return 'opening'
                elif choice == 2:
                    return 'middlegame'
                elif choice == 3:
                    return 'endgame'
                else:
                    print("Please enter a number between 1 and 3")
                    continue

            except ValueError:
                print("Please enter a valid number")
                continue
            except (KeyboardInterrupt, EOFError):
                print()
                return None

    def get_move_or_command(self) -> Optional[str]:
        """
        Get move or command from user during puzzle

        Returns:
            Move string, command ('hint', 'quit'), or None if cancelled
        """
        try:
            import sys
            import termios
            import tty

            # Check for ESC key (non-blocking)
            user_input = input().strip()

            if not user_input:
                return None

            # Check for ESC character (ASCII 27)
            if user_input == '\x1b' or user_input == chr(27):
                return 'quit'

            # Only lowercase if it's a command (hint, quit)
            # Keep moves case-sensitive for SAN notation
            if user_input.lower() in ['hint', 'quit', 'exit', 'help', 'esc']:
                return user_input.lower()

            # Return move as-is (case-sensitive)
            return user_input

        except (KeyboardInterrupt, EOFError):
            print()
            return 'quit'

    def get_yes_no(self, prompt: str) -> bool:
        """
        Get yes/no answer from user

        Args:
            prompt: Question to ask

        Returns:
            True for yes, False for no
        """
        while True:
            try:
                response = input(f"{prompt} (y/n): ").strip()
                return self.validator.validate_yes_no(response)

            except ValueError as e:
                print(str(e))
                continue
            except (KeyboardInterrupt, EOFError):
                print()
                return False

    def get_text_input(self, prompt: str, allow_empty: bool = False) -> Optional[str]:
        """
        Get text input from user

        Args:
            prompt: Input prompt
            allow_empty: Whether to allow empty input

        Returns:
            User input or None if cancelled
        """
        try:
            text = input(f"{prompt}: ").strip()

            if not text and not allow_empty:
                print("Input cannot be empty")
                return None

            return text

        except (KeyboardInterrupt, EOFError):
            print()
            return None

    def get_theme_choice(self, available_themes: list[tuple[str, int]]) -> Optional[str]:
        """
        Get theme choice from user

        Args:
            available_themes: List of (theme_name, count) tuples

        Returns:
            Theme name or None for any theme, or None if cancelled
        """
        # Color codes
        CYAN = '\033[96m'
        YELLOW = '\033[93m'
        GREEN = '\033[92m'
        RESET = '\033[0m'

        print(f"\nSelect a theme {YELLOW}(or press Enter for any theme){RESET}:")
        print(f"  {CYAN}0{RESET} = Any theme (random)")

        # Show top 10 most popular themes
        display_themes = available_themes[:10]

        for idx, (theme_name, count) in enumerate(display_themes, 1):
            print(f"  {CYAN}{idx}{RESET} = {GREEN}{theme_name}{RESET} {YELLOW}({count} puzzles){RESET}")

        print(f"\n  {YELLOW}Or type a specific theme name{RESET}")

        while True:
            try:
                choice_str = input("\nTheme choice (0 for any): ").strip()

                # Empty = any theme
                if not choice_str or choice_str == "0":
                    return None

                # Try numeric choice
                try:
                    choice = int(choice_str)
                    if 1 <= choice <= len(display_themes):
                        return display_themes[choice - 1][0]
                    else:
                        print(f"Please enter a number between 0 and {len(display_themes)}")
                        continue
                except ValueError:
                    # Not a number, treat as theme name
                    return choice_str

            except (KeyboardInterrupt, EOFError):
                print()
                return None

    def get_timer_mode(self) -> Optional[dict]:
        """
        Get timer configuration from user

        Returns:
            Dict with 'enabled' and 'time_limit' (seconds) or None if cancelled
        """
        print("\nTimer mode:")
        print("  1 = No timer (practice mode)")
        print("  2 = Stopwatch (track time)")
        print("  3 = Countdown (5 minutes)")
        print("  4 = Countdown (3 minutes)")
        print("  5 = Countdown (1 minute)")

        while True:
            try:
                choice_str = input("\nTimer mode (1-5): ").strip()

                if not choice_str:
                    return {'enabled': False, 'time_limit': None}

                choice = int(choice_str)

                if choice == 1:
                    return {'enabled': False, 'time_limit': None}
                elif choice == 2:
                    return {'enabled': True, 'time_limit': None}
                elif choice == 3:
                    return {'enabled': True, 'time_limit': 300}  # 5 minutes
                elif choice == 4:
                    return {'enabled': True, 'time_limit': 180}  # 3 minutes
                elif choice == 5:
                    return {'enabled': True, 'time_limit': 60}   # 1 minute
                else:
                    print("Please enter a number between 1 and 5")
                    continue

            except ValueError:
                print("Please enter a valid number")
                continue
            except (KeyboardInterrupt, EOFError):
                print()
                return None
