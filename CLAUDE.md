# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start

### Running the Application

```bash
# Easy way (recommended)
./run.sh

# Manual way (macOS)
source venv/bin/activate
export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib
python main.py
```

### Initial Setup (First Time)

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Install Cairo library (macOS)
brew install cairo

# 3. Activate and install dependencies
source venv/bin/activate
pip install -r requirements.txt

# 4. Download and import Lichess puzzle database (~10-15 minutes)
python scripts/setup_database.py

# For quick testing (1000 puzzles only)
python scripts/setup_database.py --sample
```

### Testing and Development

```bash
# Run tests
pytest tests/

# Code formatting
black .

# Type checking
mypy .
```

## Architecture Overview

### Core Data Flow

The application follows a layered architecture with clear separation of concerns:

```
CLI (ui/cli.py)
    ↓
PuzzleManager (core/puzzle_manager.py) ← Orchestrator
    ↓
    ├─ PuzzleSelector (core/puzzle_selector.py) → Database (data/database.py)
    ├─ MoveValidator (core/move_validator.py) → python-chess
    ├─ HintSystem (core/hint_system.py)
    ├─ ProgressTracker (core/progress_tracker.py) → progress.json
    ├─ PuzzleTimer (utils/timer.py)
    └─ BoardRenderer (rendering/board_renderer.py) → PNG images
```

**Key Component: PuzzleManager** (`core/puzzle_manager.py`)
- Acts as the central orchestrator for all puzzle-related operations
- Manages puzzle lifecycle: selection → validation → hints → completion
- Coordinates between selector, validator, hint system, and progress tracker
- Maintains current puzzle state and timer

### Critical Architectural Decisions

1. **State Management**: PuzzleManager holds all active puzzle state. Components are stateless and receive puzzle/board objects as parameters.

2. **Board Representation**: Uses `chess.Board` from python-chess library throughout. The board position advances as:
   - Start from puzzle FEN
   - Apply opponent's first move (puzzle.moves[0])
   - User makes their move (puzzle.moves[1])
   - Apply opponent's response (puzzle.moves[2])
   - Continue until puzzle.moves exhausted

3. **Move Validation Flow**:
   - MoveValidator maintains an internal board that progresses through the solution
   - Compares user input against expected moves in puzzle.solution_moves
   - Supports both SAN (Standard Algebraic Notation) and UCI notation
   - **Important**: SAN parsing is case-sensitive (e.g., "Qa4" not "qa4")

4. **Database Schema**:
   - `puzzles` table: Core puzzle data with piece_count for game phase detection
   - `themes` table: Normalized theme names
   - `puzzle_themes` junction table: Many-to-many relationship
   - Indexes on rating and piece_count for fast filtering

5. **Rendering Pipeline**:
   - `chess.Board` → `chess.svg.board()` → SVG string
   - SVG → `cairosvg.svg2png()` → PNG file (512x512px)
   - For iTerm2: PNG → base64 → inline display via escape codes
   - Images saved to `storage/images/puzzle_<id>.png`

### Game Phase Detection Logic

Located in `core/puzzle_selector.py`:
- **Opening**: `opening_tags IS NOT NULL OR themes LIKE '%opening%'`
- **Middlegame**: `piece_count >= 12 AND themes NOT LIKE '%endgame%'`
- **Endgame**: `piece_count < 12 OR themes LIKE '%endgame%'`

### Progressive Hint System

Located in `core/hint_system.py`:
- Level 1: Piece type to move (e.g., "Move your knight")
- Level 2: Source square (e.g., "From g1") + visual highlight
- Level 3: Destination square (e.g., "To f3") + visual highlight
- Level 4: Full move in SAN (e.g., "Play Nf3")

Each hint level generates a new board image with highlighted squares.

### Progress Tracking

Located in `core/progress_tracker.py`:
- Stores puzzle attempts in `storage/progress.json`
- Tracks: puzzle_id, solved, attempts, time_taken, difficulty, hints_used
- Calculates: success_rate, current_streak, best_streak, solved_by_difficulty
- Used to exclude already-solved puzzles from selection

## Platform-Specific Notes

### macOS Cairo Library Setup

The Cairo library is required for SVG→PNG conversion but isn't in Python's default library path:

```bash
# Install Cairo
brew install cairo

# Set library path before running
export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib

# Or use run.sh which handles this automatically
```

This is already configured in `run.sh`.

### Terminal Image Display

The app uses iTerm2's inline image protocol (`rendering/terminal_image.py`):
- Detects terminal capabilities via `TERM_PROGRAM` and `TERM` environment variables
- Falls back to showing file path if inline display not supported
- Base64 encodes PNG and sends via `\033]1337;File=...` escape sequence

## Database Import Process

Located in `scripts/setup_database.py`:

1. Downloads `lichess_db_puzzle.csv.zst` (~250MB compressed)
2. Decompresses using zstandard library
3. Parses CSV with fields: PuzzleId, FEN, Moves, Rating, Themes, etc.
4. Calculates piece_count from FEN for game phase detection
5. Normalizes themes into separate tables
6. Batch inserts (1000 puzzles per transaction)
7. Creates indexes for fast queries

**Important**: Keep file handle open throughout decompression. The zstandard stream must stay alive while reading. See `puzzle_loader.py:_decompress_zstd()` for proper implementation.

## UI/UX Features

### Recent UI Changes (2026-01)

- **Game Phase**: Numbered selection (1=opening, 2=middlegame, 3=endgame) instead of text input
- **Timer**: Always enabled in stopwatch mode (no user selection)
- **Quit**: Types "quit" or ESC to exit immediately (no confirmation)
- **Colors**: ANSI color codes for better visual hierarchy
  - Cyan: Menu numbers and selections
  - Yellow: Descriptions and hints
  - Green: Success messages and theme names
  - Red: Errors

### Input Handling Quirks

Located in `ui/input_handler.py`:
- Commands (hint, quit, esc) are lowercased for matching
- Moves are kept case-sensitive for SAN notation
- ESC detection via `\x1b` character check
- All menus support Ctrl+C / Ctrl+D for graceful exit

## Common Pitfalls

1. **Move Case Sensitivity**: Never lowercase user move input before passing to python-chess. SAN requires proper casing (Qa4, not qa4).

2. **Board Rendering None Values**: `chess.svg.board()` requires lists, not None:
   ```python
   # Wrong
   chess.svg.board(board, squares=None)

   # Correct
   chess.svg.board(board, squares=squares if squares else [])
   ```

3. **Zstandard File Handles**: Don't close compressed file before finishing decompression:
   ```python
   # Wrong
   with open(file, 'rb') as f:
       dctx = zstd.ZstdDecompressor()
       reader = dctx.stream_reader(f)
       return reader  # f is now closed!

   # Correct
   f = open(file, 'rb')
   dctx = zstd.ZstdDecompressor()
   reader = dctx.stream_reader(f)
   # Keep f open, close in finally block
   ```

4. **Puzzle Selection Fallback**: When no puzzles match criteria (difficulty + phase + theme + unsolved), use progressive fallback:
   - Remove unsolved filter
   - Try adjacent difficulties (±1)
   - Relax game phase
   - Relax theme
   See `puzzle_selector.py:select_puzzle()` for implementation.

## File References

### Entry Point
- `main.py:24-84` - Application initialization and main loop

### Core Orchestration
- `core/puzzle_manager.py:48-95` - Puzzle lifecycle management
- `core/puzzle_manager.py:97-120` - Move validation coordination
- `core/puzzle_manager.py:159-215` - Puzzle completion and scoring

### Critical Algorithms
- `core/puzzle_selector.py:32-102` - Puzzle selection with fallback
- `core/move_validator.py:26-75` - Move validation logic
- `core/hint_system.py:24-81` - Progressive hint generation

### Database Layer
- `data/puzzle_loader.py:82-175` - CSV import with zstandard decompression
- `data/database.py:54-113` - Puzzle query methods

### UI Components
- `ui/cli.py:56-200` - Main puzzle solving loop
- `ui/input_handler.py:44-111` - Colored menu selections
- `rendering/terminal_image.py:44-95` - iTerm2 inline image display

## Configuration

All paths and constants defined in `config/settings.py`:
- Database: `storage/puzzles.db`
- Progress: `storage/progress.json`
- Images: `storage/images/`
- Board size: 512x512px

Difficulty ratings in `config/constants.py`:
- Level 1: 600-1200 (Beginner)
- Level 2: 1200-1600 (Intermediate)
- Level 3: 1600-2000 (Advanced)
- Level 4: 2000-2400 (Expert)
- Level 5: 2400-3000 (Master)

40+ puzzle themes defined in `config/constants.py` (TACTICAL_THEMES, MATE_THEMES, etc.)
