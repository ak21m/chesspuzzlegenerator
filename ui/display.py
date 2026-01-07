"""
Console display and formatting
"""

from data.models import Puzzle, UserProgress, Hint
from utils.helpers import format_time


class Display:
    """Console output formatting"""

    # Color codes for terminal (if supported)
    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'green': '\033[92m',
        'red': '\033[91m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'cyan': '\033[96m',
    }

    def __init__(self, use_colors: bool = True):
        """
        Initialize display

        Args:
            use_colors: Whether to use terminal colors
        """
        self.use_colors = use_colors

    def _color(self, text: str, color: str) -> str:
        """Apply color to text if colors enabled"""
        if not self.use_colors:
            return text
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}"

    def show_welcome(self):
        """Display welcome message"""
        print("\n" + "=" * 60)
        print(self._color("  CHESS PUZZLE TRAINER", 'bold'))
        print("=" * 60)
        print("\nWelcome! Solve chess puzzles and improve your tactical skills.")
        print("Puzzles are sourced from Lichess.org database.\n")

    def show_main_menu(self):
        """Display main menu"""
        print("\n" + "-" * 60)
        print(self._color("MAIN MENU", 'bold'))
        print("-" * 60)
        print(f"\n{self._color('1.', 'cyan')} Play Puzzle")
        print(f"{self._color('2.', 'cyan')} View Statistics")
        print(f"{self._color('3.', 'cyan')} Help")
        print(f"{self._color('4.', 'cyan')} Exit")
        print()

    def show_puzzle_header(self, puzzle: Puzzle, difficulty: int, game_phase: str):
        """
        Display puzzle information header

        Args:
            puzzle: Puzzle instance
            difficulty: Difficulty level (1-5)
            game_phase: Game phase
        """
        print("\n" + "=" * 60)
        print(self._color(f"PUZZLE #{puzzle.puzzle_id}", 'bold'))
        print("=" * 60)
        print(f"Difficulty: {self._color(f'Level {difficulty}', 'cyan')} (Rating: {puzzle.rating})")
        print(f"Phase: {self._color(game_phase.capitalize(), 'cyan')}")
        print(f"Themes: {self._color(puzzle.themes_str, 'yellow')}")
        print(f"Popularity: {puzzle.popularity} | Plays: {puzzle.nb_plays}")
        print("=" * 60)

    def show_board_info(self, image_path: str, turn: str):
        """
        Display board image information

        Args:
            image_path: Path to board image
            turn: Whose turn (White/Black)
        """
        print(f"\n{self._color(f'{turn} to move', 'bold')}")
        print(f"Board image: {self._color(image_path, 'blue')}")
        print("\nFind the best move!")

    def show_move_prompt(self):
        """Display move input prompt"""
        print(f"\nYour move (or 'hint', 'quit'): ", end='')

    def show_success(self, message: str):
        """Display success message"""
        print(self._color(f"✓ {message}", 'green'))

    def show_error(self, message: str):
        """Display error message"""
        print(self._color(f"✗ {message}", 'red'))

    def show_warning(self, message: str):
        """Display warning message"""
        print(self._color(f"⚠ {message}", 'yellow'))

    def show_info(self, message: str):
        """Display info message"""
        print(self._color(message, 'cyan'))

    def show_hint(self, hint: Hint):
        """
        Display hint

        Args:
            hint: Hint object
        """
        print(f"\n{self._color(f'💡 Hint (Level {hint.level}/4):', 'yellow')} {hint.message}")

    def show_puzzle_complete(self, puzzle: Puzzle, attempts: int, time_taken: float, hints_used: int):
        """
        Display puzzle completion summary

        Args:
            puzzle: Puzzle instance
            attempts: Number of move attempts
            time_taken: Time in seconds
            hints_used: Number of hints used
        """
        print("\n" + "=" * 60)
        print(self._color("🎉 PUZZLE SOLVED!", 'green'))
        print("=" * 60)
        print(f"Attempts: {attempts}")
        print(f"Time: {format_time(time_taken)}")
        print(f"Hints used: {hints_used}")
        print(f"Themes: {puzzle.themes_str}")

        if puzzle.game_url:
            print(f"\nView original game: {puzzle.game_url}")

        print("=" * 60)

    def show_statistics(self, stats: UserProgress):
        """
        Display user statistics

        Args:
            stats: UserProgress object
        """
        print("\n" + "=" * 60)
        print(self._color("YOUR STATISTICS", 'bold'))
        print("=" * 60)
        print(f"\nTotal Puzzles Solved: {self._color(str(stats.total_solved), 'green')}")
        print(f"Total Attempts: {stats.total_attempts}")
        print(f"Success Rate: {self._color(f'{stats.success_rate:.1f}%', 'cyan')}")
        print(f"Current Streak: {self._color(str(stats.current_streak), 'yellow')}")
        print(f"Best Streak: {self._color(str(stats.best_streak), 'yellow')}")

        print("\n" + self._color("Solved by Difficulty:", 'bold'))
        for diff in range(1, 6):
            count = stats.solved_by_difficulty.get(diff, 0)
            bar = "█" * min(count, 20)
            print(f"  Level {diff}: {bar} {count}")

        print("=" * 60)

    def show_help(self):
        """Display help information"""
        print("\n" + "=" * 60)
        print(self._color("HELP - HOW TO PLAY", 'bold'))
        print("=" * 60)

        print("\n" + self._color("Difficulty Levels:", 'bold'))
        print("  1 = Beginner (600-1200)")
        print("  2 = Intermediate (1200-1600)")
        print("  3 = Advanced (1600-2000)")
        print("  4 = Expert (2000-2400)")
        print("  5 = Master (2400-3000)")

        print("\n" + self._color("Game Phases:", 'bold'))
        print("  1 = Opening positions")
        print("  2 = Middlegame positions")
        print("  3 = Endgame positions")

        print("\n" + self._color("Move Notation:", 'bold'))
        print("  Standard Algebraic: Nf3, e4, Qxd5, O-O")
        print("  UCI format: g1f3, e2e4, d1d5, e1g1")

        print("\n" + self._color("Commands During Puzzle:", 'bold'))
        print("  hint - Get progressive hints (4 levels)")
        print("  quit or ESC - Exit current puzzle")

        print("\n" + self._color("Timer:", 'bold'))
        print("  Stopwatch mode automatically tracks your solve time")

        print("\n" + self._color("Hints:", 'bold'))
        print("  Level 1: Piece to move")
        print("  Level 2: Source square")
        print("  Level 3: Destination square")
        print("  Level 4: Full move")

        print("=" * 60)

    def show_loading(self, message: str = "Loading..."):
        """Display loading message"""
        print(f"\n{message}")

    def show_separator(self):
        """Display separator line"""
        print("-" * 60)

    def clear_line(self):
        """Clear current line"""
        print("\r" + " " * 80 + "\r", end='')

    def prompt_input(self, message: str) -> str:
        """
        Prompt for user input

        Args:
            message: Prompt message

        Returns:
            User input string
        """
        return input(f"{message}: ").strip()

    def confirm(self, message: str) -> bool:
        """
        Ask for yes/no confirmation

        Args:
            message: Confirmation message

        Returns:
            True if yes, False if no
        """
        while True:
            response = input(f"{message} (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' or 'n'")

    def pause(self, message: str = "Press Enter to continue..."):
        """Pause and wait for user"""
        input(f"\n{message}")
