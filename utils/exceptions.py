"""
Custom exceptions for chess puzzle generator
"""


class ChessPuzzleError(Exception):
    """Base exception for application"""
    pass


class DatabaseError(ChessPuzzleError):
    """Database-related errors"""
    pass


class DatabaseNotFoundError(DatabaseError):
    """Database file not found"""
    pass


class PuzzleNotFoundError(ChessPuzzleError):
    """No puzzle matching criteria"""
    pass


class InvalidMoveError(ChessPuzzleError):
    """Invalid move input"""
    pass


class RenderError(ChessPuzzleError):
    """Image rendering failed"""
    pass


class InvalidDifficultyError(ChessPuzzleError):
    """Invalid difficulty level"""
    pass


class InvalidGamePhaseError(ChessPuzzleError):
    """Invalid game phase"""
    pass
