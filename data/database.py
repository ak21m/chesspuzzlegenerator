"""
Database wrapper for SQLite operations
"""

import sqlite3
from pathlib import Path
from typing import List, Optional, Tuple
from utils.exceptions import DatabaseError, DatabaseNotFoundError


class Database:
    """SQLite database wrapper with error handling"""

    def __init__(self, db_path: str):
        """
        Initialize database connection

        Args:
            db_path: Path to SQLite database file

        Raises:
            DatabaseError: If connection fails
        """
        self.db_path = Path(db_path)
        self.conn = None
        self._connect()

    def _connect(self):
        """Establish database connection"""
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to connect to database: {e}")

    def create_schema(self):
        """Create database schema (tables and indexes)"""
        cursor = self.conn.cursor()

        try:
            # Main puzzles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS puzzles (
                    puzzle_id TEXT PRIMARY KEY,
                    fen TEXT NOT NULL,
                    moves TEXT NOT NULL,
                    rating INTEGER NOT NULL,
                    rating_deviation INTEGER,
                    popularity INTEGER,
                    nb_plays INTEGER,
                    game_url TEXT,
                    opening_tags TEXT,
                    piece_count INTEGER
                )
            ''')

            # Themes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS themes (
                    theme_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    theme_name TEXT UNIQUE NOT NULL
                )
            ''')

            # Puzzle-themes junction table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS puzzle_themes (
                    puzzle_id TEXT,
                    theme_id INTEGER,
                    PRIMARY KEY (puzzle_id, theme_id),
                    FOREIGN KEY (puzzle_id) REFERENCES puzzles(puzzle_id),
                    FOREIGN KEY (theme_id) REFERENCES themes(theme_id)
                )
            ''')

            self.conn.commit()
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to create schema: {e}")

    def create_indexes(self):
        """Create indexes for fast queries"""
        cursor = self.conn.cursor()

        try:
            cursor.execute(
                'CREATE INDEX IF NOT EXISTS idx_rating ON puzzles(rating)'
            )
            cursor.execute(
                'CREATE INDEX IF NOT EXISTS idx_piece_count ON puzzles(piece_count)'
            )
            cursor.execute(
                'CREATE INDEX IF NOT EXISTS idx_theme_name ON themes(theme_name)'
            )
            self.conn.commit()
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to create indexes: {e}")

    def execute_query(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        """
        Execute a SELECT query and return results

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of result rows

        Raises:
            DatabaseError: If query fails
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            raise DatabaseError(f"Query failed: {e}")

    def execute_one(self, query: str, params: Tuple = ()) -> Optional[sqlite3.Row]:
        """
        Execute a SELECT query and return first result

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            First result row or None

        Raises:
            DatabaseError: If query fails
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
        except sqlite3.Error as e:
            raise DatabaseError(f"Query failed: {e}")

    def execute_write(self, query: str, params: Tuple = ()):
        """
        Execute an INSERT/UPDATE/DELETE query

        Args:
            query: SQL query string
            params: Query parameters

        Raises:
            DatabaseError: If query fails
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise DatabaseError(f"Write query failed: {e}")

    def execute_many(self, query: str, params_list: List[Tuple]):
        """
        Execute multiple INSERT queries (batch)

        Args:
            query: SQL query string
            params_list: List of parameter tuples

        Raises:
            DatabaseError: If batch insert fails
        """
        try:
            cursor = self.conn.cursor()
            cursor.executemany(query, params_list)
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise DatabaseError(f"Batch insert failed: {e}")

    def get_puzzle_count(self) -> int:
        """Get total number of puzzles in database"""
        result = self.execute_one("SELECT COUNT(*) as count FROM puzzles")
        return result['count'] if result else 0

    def get_theme_id(self, theme_name: str) -> Optional[int]:
        """Get theme ID by name, or None if not found"""
        result = self.execute_one(
            "SELECT theme_id FROM themes WHERE theme_name = ?",
            (theme_name,)
        )
        return result['theme_id'] if result else None

    def insert_theme(self, theme_name: str) -> int:
        """
        Insert theme and return its ID

        Args:
            theme_name: Name of the theme

        Returns:
            Theme ID (existing or newly created)
        """
        # Try to get existing
        theme_id = self.get_theme_id(theme_name)
        if theme_id:
            return theme_id

        # Insert new
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO themes (theme_name) VALUES (?)",
                (theme_name,)
            )
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Another process inserted it, fetch again
            return self.get_theme_id(theme_name)

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Context manager support"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        self.close()
