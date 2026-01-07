"""
Setup database for chess puzzle generator
Downloads Lichess database and imports into SQLite
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.puzzle_loader import PuzzleLoader
from config.settings import Settings
from scripts.download_puzzles import download_lichess_database


def setup_database(sample_only: bool = False):
    """
    Complete database setup:
    1. Download CSV if not exists
    2. Import into SQLite
    3. Create indexes

    Args:
        sample_only: If True, only import first 1000 puzzles for testing
    """
    print("=" * 60)
    print("Chess Puzzle Generator - Database Setup")
    print("=" * 60)

    Settings.ensure_directories()

    # Check if database already exists
    if Settings.DATABASE_PATH.exists():
        print(f"\n⚠  Database already exists at: {Settings.DATABASE_PATH}")
        response = input("Recreate database? This will delete existing data (y/n): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
        Settings.DATABASE_PATH.unlink()
        print("Existing database deleted.")

    # Step 1: Download CSV if needed
    print("\n" + "=" * 60)
    print("Step 1: Download Puzzle Database")
    print("=" * 60)

    if not Settings.LICHESS_CSV_PATH.exists():
        print("\nLichess database not found. Downloading...")
        download_lichess_database()
    else:
        print(f"\n✓ Lichess database found at: {Settings.LICHESS_CSV_PATH}")
        print(f"  File size: {Settings.LICHESS_CSV_PATH.stat().st_size / (1024*1024):.1f} MB")

    # Step 2: Import into SQLite
    print("\n" + "=" * 60)
    print("Step 2: Import Puzzles into Database")
    print("=" * 60)

    if sample_only:
        print("\n⚠  SAMPLE MODE: Importing first 1000 puzzles only")
        print("  For testing purposes. Run without --sample for full import.\n")
        limit = 1000
    else:
        print("\nImporting full database (~5M+ puzzles)")
        print("This will take 10-15 minutes depending on your system.")
        print("You can interrupt anytime with Ctrl+C\n")
        limit = None

    try:
        loader = PuzzleLoader(str(Settings.DATABASE_PATH))
        loader.import_from_lichess(
            str(Settings.LICHESS_CSV_PATH),
            compressed=True,
            limit=limit
        )
        loader.close()

    except KeyboardInterrupt:
        print("\n\n⚠  Import interrupted by user")
        print("Database may be partially populated.")
        print("Run setup again to complete import.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Import failed: {e}")
        sys.exit(1)

    # Done
    print("\n" + "=" * 60)
    print("✓ Setup Complete!")
    print("=" * 60)
    print(f"\nDatabase location: {Settings.DATABASE_PATH}")
    print(f"Database size: {Settings.DATABASE_PATH.stat().st_size / (1024*1024):.1f} MB")
    print("\nYou can now run the application:")
    print("  python main.py")


def main():
    """Main entry point"""
    sample_only = '--sample' in sys.argv or '-s' in sys.argv

    try:
        setup_database(sample_only=sample_only)
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(1)


if __name__ == "__main__":
    main()
