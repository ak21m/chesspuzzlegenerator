"""
Command-line interface for chess puzzle trainer
"""

import chess
from core.puzzle_manager import PuzzleManager
from rendering.board_renderer import BoardRenderer
from rendering.terminal_image import TerminalImageRenderer
from ui.display import Display
from ui.input_handler import InputHandler
from utils.exceptions import PuzzleNotFoundError
from config.settings import Settings


class ChessPuzzleCLI:
    """
    Console interface for puzzle game
    Main game loop and user interaction
    """

    def __init__(self, manager: PuzzleManager):
        """
        Initialize CLI

        Args:
            manager: PuzzleManager instance
        """
        self.manager = manager
        self.renderer = BoardRenderer(str(Settings.IMAGES_DIR))
        self.terminal_image = TerminalImageRenderer()
        self.display = Display()
        self.input_handler = InputHandler()
        self.can_show_inline = self.terminal_image.can_display_images()

    def run(self):
        """Main game loop"""
        self.display.show_welcome()

        while True:
            self.display.show_main_menu()

            choice = self.input_handler.get_menu_choice(1, 4)

            if choice == 1:
                self.play_puzzle()
            elif choice == 2:
                self.show_statistics()
            elif choice == 3:
                self.show_help()
            elif choice == 4:
                print("\nThanks for playing! Goodbye!")
                break
            elif choice is None:
                continue

    def play_puzzle(self):
        """
        Puzzle solving flow
        """
        # Get puzzle parameters
        difficulty = self.input_handler.get_difficulty()
        if difficulty is None:
            return

        game_phase = self.input_handler.get_game_phase()
        if game_phase is None:
            return

        # Get theme (optional)
        available_themes = self.manager.get_available_themes()
        theme = self.input_handler.get_theme_choice(available_themes)

        # Default to stopwatch mode (always enabled, no time limit)
        timer_config = {'enabled': True, 'time_limit': None}

        # Load puzzle
        self.display.show_loading("Loading puzzle...")

        try:
            puzzle = self.manager.start_puzzle(difficulty, game_phase, theme=theme, timer_config=timer_config)
        except PuzzleNotFoundError as e:
            self.display.show_error(str(e))
            self.display.pause()
            return

        # Display puzzle info
        self.display.show_puzzle_header(puzzle, difficulty, game_phase)
        if theme:
            print(f"Theme: {theme}")

        # Render and display initial board
        current_board = self.manager.get_current_board()
        image_path = self.renderer.render_puzzle(current_board, puzzle.puzzle_id)

        # Display board - inline if supported, otherwise show path
        if self.can_show_inline:
            self.terminal_image.display_image(image_path, width=400)
        else:
            turn = "White" if current_board.turn == chess.WHITE else "Black"
            self.display.show_board_info(image_path, turn)

        # Puzzle solving loop
        while not self.manager.is_puzzle_complete():
            # Check if time is up
            if self.manager.is_time_up():
                print("\n⏰ Time's up!")
                self.manager.finish_puzzle()
                self.display.pause()
                return

            # Show timer status if enabled
            timer_status = self.manager.get_timer_status()
            if timer_status:
                print(f"\n{timer_status}")

            self.display.show_move_prompt()
            user_input = self.input_handler.get_move_or_command()

            if not user_input:
                continue

            # Handle commands
            if user_input == 'quit':
                # Quit immediately without confirmation
                self.manager.finish_puzzle(quit_early=True)
                return

            elif user_input == 'hint':
                hint = self.manager.get_hint()
                if hint:
                    self.display.show_hint(hint)

                    # Re-render board with hint visualization
                    current_board = self.manager.get_current_board()
                    image_path = self.renderer.render_puzzle(
                        current_board,
                        puzzle.puzzle_id,
                        hint=hint
                    )

                    # Display updated board
                    if self.can_show_inline:
                        self.terminal_image.display_image(image_path, width=400)
                    else:
                        print(f"Updated board: {image_path}")
                else:
                    self.display.show_error("No hints available")
                continue

            # Validate move
            is_correct, message = self.manager.validate_move(user_input)

            if is_correct:
                self.display.show_success(message)

                # Re-render board after move (if puzzle continues)
                if not self.manager.is_puzzle_complete():
                    current_board = self.manager.get_current_board()
                    image_path = self.renderer.render_puzzle(
                        current_board,
                        puzzle.puzzle_id
                    )

                    # Display updated board
                    if self.can_show_inline:
                        print()  # Add spacing
                        self.terminal_image.display_image(image_path, width=400)
                    else:
                        turn = "White" if current_board.turn == chess.WHITE else "Black"
                        print(f"\n{turn} to move")
                        print(f"Board updated: {image_path}")
            else:
                self.display.show_error(message)

        # Puzzle complete
        results = self.manager.finish_puzzle()

        self.display.show_puzzle_complete(
            puzzle=results['puzzle'],
            attempts=results['attempts'],
            time_taken=results['time_taken'],
            hints_used=results['hints_used']
        )

        self.display.pause()

    def show_statistics(self):
        """Display user statistics"""
        stats = self.manager.get_statistics()
        self.display.show_statistics(stats)
        self.display.pause()

    def show_help(self):
        """Show help information"""
        self.display.show_help()
        self.display.pause()
