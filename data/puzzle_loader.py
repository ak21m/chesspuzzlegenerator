"""
Lichess puzzle database loader
Imports CSV data into SQLite database
"""

import csv
import io
from pathlib import Path
from typing import Iterator
import zstandard as zstd
import chess
from tqdm import tqdm

from data.database import Database
from config.settings import Settings
from utils.exceptions import DatabaseError


class PuzzleLoader:
    """
    Loads Lichess puzzle database into SQLite
    Handles decompression and data transformation
    """

    def __init__(self, db_path: str):
        """
        Initialize loader with database path

        Args:
            db_path: Path to SQLite database file
        """
        self.db = Database(db_path)

    def import_from_lichess(self, csv_path: str, compressed: bool = True, limit: int = None):
        """
        Import puzzles from Lichess CSV file

        Args:
            csv_path: Path to Lichess CSV file (can be .zst compressed)
            compressed: Whether file is zstandard compressed
            limit: Optional limit on number of puzzles to import (for testing)

        Steps:
        1. Decompress if needed (zstd)
        2. Parse CSV
        3. Calculate piece counts
        4. Insert into database with themes
        """
        print("Setting up database schema...")
        self.db.create_schema()

        print(f"Importing puzzles from {csv_path}...")
        if compressed:
            print("Decompressing .zst file (this may take a moment)...")

        # Open file (decompress if needed)
        # Keep compressed file handle open throughout
        if compressed:
            compressed_file = open(csv_path, 'rb')
            dctx = zstd.ZstdDecompressor()
            reader = dctx.stream_reader(compressed_file)
            file_handle = io.TextIOWrapper(reader, encoding='utf-8')
        else:
            compressed_file = None
            file_handle = open(csv_path, 'r', encoding='utf-8')

        try:
            # Parse CSV
            csv_reader = csv.DictReader(file_handle)

            # Count lines for progress bar (if possible)
            # For compressed files, we'll use unknown total
            total = limit if limit else None

            # Batch insert for performance
            batch_size = Settings.IMPORT_BATCH_SIZE
            batch = []
            imported_count = 0

            with tqdm(total=total, unit=' puzzles') as pbar:
                for row in csv_reader:
                    try:
                        puzzle_data = self._transform_row(row)
                        batch.append(puzzle_data)

                        if len(batch) >= batch_size:
                            self._insert_batch(batch)
                            imported_count += len(batch)
                            pbar.update(len(batch))
                            batch = []

                        # Check limit
                        if limit and imported_count >= limit:
                            break

                    except Exception as e:
                        # Skip invalid puzzles
                        print(f"\nWarning: Skipping puzzle {row.get('PuzzleId', 'unknown')}: {e}")
                        continue

                # Insert remaining
                if batch:
                    self._insert_batch(batch)
                    imported_count += len(batch)
                    pbar.update(len(batch))

        finally:
            file_handle.close()
            if compressed_file:
                compressed_file.close()

        # Create indexes
        print("\nCreating database indexes...")
        self.db.create_indexes()

        print(f"\nImport complete! Imported {imported_count} puzzles.")
        print(f"Total puzzles in database: {self.db.get_puzzle_count()}")

    def _transform_row(self, row: dict) -> dict:
        """
        Transform CSV row to database format

        Args:
            row: CSV row as dictionary

        Returns:
            Dictionary with transformed data

        Processing:
        - Parse FEN to count pieces
        - Split comma/space-separated themes
        - Convert types
        """
        # Count pieces from FEN
        try:
            board = chess.Board(row['FEN'])
            piece_count = len(board.piece_map())
        except Exception as e:
            raise ValueError(f"Invalid FEN: {row['FEN']} - {e}")

        # Split moves (space-separated in Lichess format)
        moves = row['Moves'].split()
        if not moves:
            raise ValueError("No moves found")

        # Split themes (space-separated in Lichess format)
        themes = row['Themes'].split() if row.get('Themes') else []

        # Split opening tags (space-separated)
        opening_tags = row.get('OpeningTags', '').split() if row.get('OpeningTags') else []

        return {
            'puzzle_id': row['PuzzleId'],
            'fen': row['FEN'],
            'moves': ' '.join(moves),
            'rating': int(row['Rating']),
            'rating_deviation': int(row['RatingDeviation']),
            'popularity': int(row['Popularity']),
            'nb_plays': int(row['NbPlays']),
            'themes': themes,
            'game_url': row['GameUrl'],
            'opening_tags': ','.join(opening_tags),
            'piece_count': piece_count
        }

    def _insert_batch(self, batch: list):
        """
        Insert batch of puzzles with themes

        Args:
            batch: List of puzzle dictionaries
        """
        for puzzle in batch:
            try:
                # Insert puzzle
                self.db.execute_write('''
                    INSERT OR IGNORE INTO puzzles
                    (puzzle_id, fen, moves, rating, rating_deviation,
                     popularity, nb_plays, game_url, opening_tags, piece_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    puzzle['puzzle_id'],
                    puzzle['fen'],
                    puzzle['moves'],
                    puzzle['rating'],
                    puzzle['rating_deviation'],
                    puzzle['popularity'],
                    puzzle['nb_plays'],
                    puzzle['game_url'],
                    puzzle['opening_tags'],
                    puzzle['piece_count']
                ))

                # Insert themes
                for theme in puzzle['themes']:
                    # Get or create theme ID
                    theme_id = self.db.insert_theme(theme)

                    # Link puzzle to theme
                    self.db.execute_write('''
                        INSERT OR IGNORE INTO puzzle_themes (puzzle_id, theme_id)
                        VALUES (?, ?)
                    ''', (puzzle['puzzle_id'], theme_id))

            except DatabaseError as e:
                # Log error but continue with other puzzles
                print(f"\nWarning: Failed to insert puzzle {puzzle['puzzle_id']}: {e}")
                continue

    def close(self):
        """Close database connection"""
        self.db.close()
