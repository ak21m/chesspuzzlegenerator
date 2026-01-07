"""
Configuration settings for chess puzzle generator
"""

from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application configuration"""

    # Paths
    BASE_DIR = Path(__file__).parent.parent
    STORAGE_DIR = BASE_DIR / "storage"
    DATABASE_PATH = STORAGE_DIR / "puzzles.db"
    PROGRESS_PATH = STORAGE_DIR / "progress.json"
    IMAGES_DIR = STORAGE_DIR / "images"

    # Lichess Database
    LICHESS_DB_URL = "https://database.lichess.org/lichess_db_puzzle.csv.zst"
    LICHESS_CSV_PATH = STORAGE_DIR / "lichess_db_puzzle.csv.zst"

    # Rendering
    BOARD_SIZE = 512
    BOARD_COORDINATES = True

    # Stockfish (optional - for future)
    STOCKFISH_PATH = os.getenv("STOCKFISH_PATH", None)

    # Database batch size for imports
    IMPORT_BATCH_SIZE = 1000

    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.STORAGE_DIR.mkdir(exist_ok=True)
        cls.IMAGES_DIR.mkdir(exist_ok=True)

    @classmethod
    def get_difficulty_range(cls, difficulty: int) -> tuple[int, int]:
        """Get rating range for difficulty level (1-5)"""
        from config.constants import Difficulty

        difficulty_map = {
            1: Difficulty.LEVEL_1,
            2: Difficulty.LEVEL_2,
            3: Difficulty.LEVEL_3,
            4: Difficulty.LEVEL_4,
            5: Difficulty.LEVEL_5
        }

        if difficulty not in difficulty_map:
            raise ValueError(f"Difficulty must be 1-5, got {difficulty}")

        return difficulty_map[difficulty].value
