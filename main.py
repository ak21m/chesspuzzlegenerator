"""
Chess Puzzle Generator - Main Entry Point
"""

import sys
from pathlib import Path

from config.settings import Settings
from core.puzzle_manager import PuzzleManager
from ui.cli import ChessPuzzleCLI
from utils.exceptions import DatabaseNotFoundError


def check_database() -> bool:
    """
    Check if database exists

    Returns:
        True if database exists, False otherwise
    """
    return Settings.DATABASE_PATH.exists()


def main():
    """
    Main entry point

    Flow:
    1. Check database exists
    2. Initialize components
    3. Start CLI loop
    4. Handle cleanup
    """
    print("Chess Puzzle Generator")
    print("=" * 60)

    # Ensure directories exist
    Settings.ensure_directories()

    # Check database
    if not check_database():
        print("\n✗ Error: Puzzle database not found!")
        print(f"\nExpected location: {Settings.DATABASE_PATH}")
        print("\nPlease run the setup script first:")
        print("  python scripts/setup_database.py")
        print("\nFor quick testing (1000 puzzles):")
        print("  python scripts/setup_database.py --sample")
        sys.exit(1)

    # Display database info
    db_size_mb = Settings.DATABASE_PATH.stat().st_size / (1024 * 1024)
    print(f"\n✓ Database found: {Settings.DATABASE_PATH}")
    print(f"  Size: {db_size_mb:.1f} MB")

    try:
        # Initialize puzzle manager
        manager = PuzzleManager(
            db_path=str(Settings.DATABASE_PATH),
            progress_path=str(Settings.PROGRESS_PATH),
            images_dir=str(Settings.IMAGES_DIR)
        )

        # Start CLI
        cli = ChessPuzzleCLI(manager)
        cli.run()

    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
        sys.exit(0)

    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        # Cleanup
        if 'manager' in locals():
            manager.close()


if __name__ == "__main__":
    main()
