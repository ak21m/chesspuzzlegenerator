"""
Constants for chess puzzle generator
"""

from enum import Enum


class Difficulty(Enum):
    """Difficulty levels with rating ranges"""
    LEVEL_1 = (600, 1200)    # Beginner
    LEVEL_2 = (1200, 1600)   # Intermediate
    LEVEL_3 = (1600, 2000)   # Advanced
    LEVEL_4 = (2000, 2400)   # Expert
    LEVEL_5 = (2400, 3000)   # Master


class GamePhase(Enum):
    """Game phases"""
    OPENING = "opening"
    MIDDLEGAME = "middlegame"
    ENDGAME = "endgame"


# Game phase thresholds
ENDGAME_PIECE_THRESHOLD = 12

# Endgame theme keywords for filtering
ENDGAME_THEMES = [
    'endgame', 'mateIn1', 'mateIn2', 'mateIn3', 'mateIn4', 'mateIn5',
    'promotion', 'queenEndgame', 'rookEndgame', 'bishopEndgame',
    'knightEndgame', 'pawnEndgame'
]

# Opening theme keywords
OPENING_THEMES = [
    'opening', 'openingVariation', 'trap'
]

# Hint costs (for potential scoring system)
HINT_PENALTIES = {
    1: 10,   # -10 points for piece hint
    2: 20,   # -20 points for source square
    3: 30,   # -30 points for dest square
    4: 50    # -50 points for full move
}

# Common puzzle themes for filtering
TACTICAL_THEMES = {
    'fork': 'Attack two or more pieces simultaneously',
    'pin': 'Piece cannot move without exposing a more valuable piece',
    'skewer': 'Force a valuable piece to move, exposing a less valuable piece',
    'discoveredAttack': 'Moving a piece reveals an attack from another piece',
    'doubleCheck': 'Check from two pieces simultaneously',
    'attraction': 'Force enemy piece to a bad square',
    'deflection': 'Force piece away from defending something',
    'interference': 'Block line between two enemy pieces',
    'removeDefender': 'Eliminate or distract a defending piece',
    'sacrifice': 'Give up material for tactical advantage',
    'zugzwang': 'Any move worsens your position',
    'clearance': 'Clear a square or line for own piece',
    'xRayAttack': 'Attack through an enemy piece',
}

# Checkmate patterns
MATE_THEMES = {
    'mateIn1': 'Checkmate in one move',
    'mateIn2': 'Checkmate in two moves',
    'mateIn3': 'Checkmate in three moves',
    'mateIn4': 'Checkmate in four moves',
    'mateIn5': 'Checkmate in five or more moves',
    'backRankMate': 'Checkmate on the back rank',
    'anastasiasMate': 'Knight and Rook checkmate pattern',
    'arabianMate': 'Knight and Rook checkmate in corner',
    'doubleBishopMate': 'Two bishops deliver mate',
    'dovetailMate': 'Queen delivers mate, king can\'t move',
    'smotheredMate': 'Knight delivers mate, king blocked by own pieces',
    'hookMate': 'Rook and Knight checkmate pattern',
}

# Strategic themes
STRATEGIC_THEMES = {
    'advantage': 'Gain significant advantage',
    'crushing': 'Overwhelming advantage',
    'quietMove': 'Subtle but strong move',
    'defensiveMove': 'Strong defensive resource',
    'equality': 'Reach equal position from worse',
    'attackingF2F7': 'Attack on f2 or f7 square',
    'capturingDefender': 'Capture piece that was defending',
}

# Special move themes
SPECIAL_MOVE_THEMES = {
    'castling': 'Castling is the key move',
    'enPassant': 'En passant capture',
    'promotion': 'Pawn promotion',
    'underPromotion': 'Promote to piece other than queen',
}

# Popular theme categories for UI
THEME_CATEGORIES = {
    'Tactical Patterns': list(TACTICAL_THEMES.keys()),
    'Checkmate Patterns': list(MATE_THEMES.keys()),
    'Strategic': list(STRATEGIC_THEMES.keys()),
    'Special Moves': list(SPECIAL_MOVE_THEMES.keys()),
}

# All available themes combined
ALL_THEME_DESCRIPTIONS = {
    **TACTICAL_THEMES,
    **MATE_THEMES,
    **STRATEGIC_THEMES,
    **SPECIAL_MOVE_THEMES
}
