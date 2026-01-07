"""
Puzzle selection with filtering by difficulty and game phase
"""

from typing import Optional, Set
from data.database import Database
from data.models import Puzzle
from config.settings import Settings
from config.constants import ENDGAME_PIECE_THRESHOLD, ENDGAME_THEMES, OPENING_THEMES
from utils.exceptions import PuzzleNotFoundError


class PuzzleSelector:
    """
    Selects puzzles based on difficulty and game phase
    Ensures variety and avoids repetition
    """

    def __init__(self, database: Database):
        """
        Initialize selector with database

        Args:
            database: Database instance
        """
        self.db = database

    def select_puzzle(
        self,
        difficulty: int,
        game_phase: str,
        solved_puzzle_ids: Set[str] = None,
        theme: Optional[str] = None
    ) -> Optional[Puzzle]:
        """
        Select a puzzle matching criteria with progressive fallback

        Args:
            difficulty: Difficulty level (1-5)
            game_phase: Game phase ('opening', 'middlegame', 'endgame')
            solved_puzzle_ids: Set of already solved puzzle IDs to avoid
            theme: Optional theme to filter by (e.g., 'fork', 'pin', 'mateIn2')

        Returns:
            Puzzle instance or None if not found

        Raises:
            PuzzleNotFoundError: If no puzzles available even after fallbacks
        """
        solved_puzzle_ids = solved_puzzle_ids or set()

        # Try exact match with solved filter
        puzzle = self._query_puzzle(difficulty, game_phase, solved_puzzle_ids, exclude_solved=True, theme=theme)
        if puzzle:
            return puzzle

        # Fallback 1: Include solved puzzles
        if solved_puzzle_ids:
            puzzle = self._query_puzzle(difficulty, game_phase, solved_puzzle_ids, exclude_solved=False, theme=theme)
            if puzzle:
                return puzzle

        # Fallback 2: Try adjacent difficulty levels
        for adj_diff in [difficulty - 1, difficulty + 1]:
            if 1 <= adj_diff <= 5:
                puzzle = self._query_puzzle(adj_diff, game_phase, solved_puzzle_ids, exclude_solved=False, theme=theme)
                if puzzle:
                    return puzzle

        # Fallback 3: Relax game phase constraint
        puzzle = self._query_puzzle(difficulty, None, solved_puzzle_ids, exclude_solved=False, theme=theme)
        if puzzle:
            return puzzle

        # Fallback 4: Relax theme constraint
        if theme:
            puzzle = self._query_puzzle(difficulty, game_phase, solved_puzzle_ids, exclude_solved=False, theme=None)
            if puzzle:
                return puzzle

        # Fallback 5: Any puzzle
        puzzle = self._query_puzzle(None, None, solved_puzzle_ids, exclude_solved=False, theme=None)
        if puzzle:
            return puzzle

        raise PuzzleNotFoundError("No puzzles available in database")

    def _query_puzzle(
        self,
        difficulty: Optional[int],
        game_phase: Optional[str],
        solved_puzzle_ids: Set[str],
        exclude_solved: bool,
        theme: Optional[str] = None
    ) -> Optional[Puzzle]:
        """
        Query database for puzzle with filters

        Args:
            difficulty: Difficulty level (1-5) or None for any
            game_phase: Game phase or None for any
            solved_puzzle_ids: Set of solved puzzle IDs
            exclude_solved: Whether to exclude solved puzzles
            theme: Optional theme to filter by

        Returns:
            Puzzle instance or None
        """
        # Build WHERE clause
        where_clauses = []
        params = []

        # Difficulty filter
        if difficulty is not None:
            min_rating, max_rating = Settings.get_difficulty_range(difficulty)
            where_clauses.append("p.rating BETWEEN ? AND ?")
            params.extend([min_rating, max_rating])

        # Game phase filter
        if game_phase:
            phase_clause, phase_params = self._build_phase_filter(game_phase)
            if phase_clause:
                where_clauses.append(phase_clause)
                params.extend(phase_params)

        # Theme filter
        if theme:
            where_clauses.append("t.theme_name = ?")
            params.append(theme)

        # Exclude solved puzzles
        if exclude_solved and solved_puzzle_ids:
            placeholders = ','.join(['?' for _ in solved_puzzle_ids])
            where_clauses.append(f"p.puzzle_id NOT IN ({placeholders})")
            params.extend(solved_puzzle_ids)

        # Build query
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

        query = f"""
            SELECT DISTINCT p.*
            FROM puzzles p
            LEFT JOIN puzzle_themes pt ON p.puzzle_id = pt.puzzle_id
            LEFT JOIN themes t ON pt.theme_id = t.theme_id
            WHERE {where_sql}
            ORDER BY RANDOM()
            LIMIT 1
        """

        # Execute query
        row = self.db.execute_one(query, tuple(params))

        if not row:
            return None

        # Convert to Puzzle object
        return self._row_to_puzzle(row)

    def _build_phase_filter(self, game_phase: str) -> tuple[str, list]:
        """
        Build SQL filter for game phase

        Args:
            game_phase: 'opening', 'middlegame', or 'endgame'

        Returns:
            Tuple of (SQL clause, parameters)
        """
        if game_phase == 'opening':
            # Opening: Has opening tags OR opening-related themes
            theme_placeholders = ','.join(['?' for _ in OPENING_THEMES])
            clause = f"(p.opening_tags != '' OR t.theme_name IN ({theme_placeholders}))"
            params = list(OPENING_THEMES)
            return clause, params

        elif game_phase == 'endgame':
            # Endgame: Less than threshold pieces OR endgame themes
            theme_placeholders = ','.join(['?' for _ in ENDGAME_THEMES])
            clause = f"(p.piece_count < ? OR t.theme_name IN ({theme_placeholders}))"
            params = [ENDGAME_PIECE_THRESHOLD] + list(ENDGAME_THEMES)
            return clause, params

        else:  # middlegame
            # Middlegame: At least threshold pieces AND not endgame themes
            theme_placeholders = ','.join(['?' for _ in ENDGAME_THEMES])
            clause = f"(p.piece_count >= ? AND (t.theme_name IS NULL OR t.theme_name NOT IN ({theme_placeholders})))"
            params = [ENDGAME_PIECE_THRESHOLD] + list(ENDGAME_THEMES)
            return clause, params

    def _row_to_puzzle(self, row) -> Puzzle:
        """
        Convert database row to Puzzle object

        Args:
            row: SQLite row

        Returns:
            Puzzle instance
        """
        # Get themes for this puzzle
        themes_query = """
            SELECT t.theme_name
            FROM puzzle_themes pt
            JOIN themes t ON pt.theme_id = t.theme_id
            WHERE pt.puzzle_id = ?
        """
        theme_rows = self.db.execute_query(themes_query, (row['puzzle_id'],))
        themes = [r['theme_name'] for r in theme_rows]

        # Parse opening tags
        opening_tags = row['opening_tags'].split(',') if row['opening_tags'] else []

        # Parse moves
        moves = row['moves'].split()

        return Puzzle(
            puzzle_id=row['puzzle_id'],
            fen=row['fen'],
            moves=moves,
            rating=row['rating'],
            rating_deviation=row['rating_deviation'],
            popularity=row['popularity'],
            nb_plays=row['nb_plays'],
            themes=themes,
            game_url=row['game_url'],
            opening_tags=opening_tags,
            piece_count=row['piece_count']
        )

    def get_puzzle_by_id(self, puzzle_id: str) -> Optional[Puzzle]:
        """
        Get specific puzzle by ID

        Args:
            puzzle_id: Puzzle ID

        Returns:
            Puzzle instance or None
        """
        row = self.db.execute_one(
            "SELECT * FROM puzzles WHERE puzzle_id = ?",
            (puzzle_id,)
        )

        if not row:
            return None

        return self._row_to_puzzle(row)

    def get_available_themes(self, limit: int = 50) -> list[tuple[str, int]]:
        """
        Get list of available themes with puzzle counts

        Args:
            limit: Maximum number of themes to return

        Returns:
            List of (theme_name, count) tuples, sorted by popularity
        """
        query = """
            SELECT t.theme_name, COUNT(DISTINCT pt.puzzle_id) as count
            FROM themes t
            JOIN puzzle_themes pt ON t.theme_id = pt.theme_id
            GROUP BY t.theme_name
            HAVING count > 0
            ORDER BY count DESC
            LIMIT ?
        """

        rows = self.db.execute_query(query, (limit,))
        return [(row['theme_name'], row['count']) for row in rows]
