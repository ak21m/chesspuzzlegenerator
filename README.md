# Chess Puzzle Generator

A Python console application that provides chess puzzles from the Lichess database (5M+ puzzles). Select difficulty (1-5) and game phase (opening/mid/endgame), solve tactical puzzles, and track your progress.

## Features

- 5.4M+ chess puzzles from Lichess
- Difficulty levels 1-5 (rated 600-3000)
- Game phase filtering (opening/middlegame/endgame)
- Progressive 4-level hint system
- Progress tracking with statistics
- 512x512px PNG board visualization
- Move validation for SAN and UCI notation
- Puzzle themes display

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- ~2GB free disk space for puzzle database

## Installation

### 1. Clone or Download Repository

```bash
cd /path/to/your/projects
# (Repository is already at /Users/aniketshingote/Projects/chesspuzzlegenerator)
```

### 2. Create Virtual Environment

```bash
cd chesspuzzlegenerator
python -m venv venv
```

### 3. Install System Dependencies (macOS only)

On macOS, you need to install the Cairo graphics library:

```bash
brew install cairo
```

### 4. Activate Virtual Environment

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 5. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 6. Setup Database

This step downloads the Lichess puzzle database (~250MB) and imports it into SQLite (~10-15 minutes).

**Full import (recommended):**
```bash
python scripts/setup_database.py
```

**Sample import (for testing, 1000 puzzles only):**
```bash
python scripts/setup_database.py --sample
```

## Usage

### Run the Application

**Easy way (recommended):**
```bash
./run.sh
```

**Manual way:**
```bash
source venv/bin/activate
export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib  # macOS only
python main.py
```

### Main Menu Options

1. **Play Puzzle** - Solve a chess puzzle
2. **View Statistics** - See your progress and stats
3. **Help** - View help information
4. **Exit** - Quit the application

### Playing Puzzles

1. Select difficulty (1-5):
   - Level 1: Beginner (rating 600-1200)
   - Level 2: Intermediate (rating 1200-1600)
   - Level 3: Advanced (rating 1600-2000)
   - Level 4: Expert (rating 2000-2400)
   - Level 5: Master (rating 2400-3000)

2. Select game phase:
   - `opening` (or `early`) - Opening positions
   - `middlegame` (or `mid`) - Middlegame positions
   - `endgame` (or `end`) - Endgame positions

3. Solve the puzzle:
   - View the board image at the displayed path
   - Enter moves in algebraic notation (e.g., `Nf3`, `Qxd5`, `e4`)
   - Type `hint` for progressive hints (4 levels)
   - Type `quit` to exit puzzle

### Move Notation

The application supports two notation formats:

- **Standard Algebraic Notation (SAN)**: `Nf3`, `Qxd5`, `O-O`, `exd5+`
- **UCI notation**: `g1f3`, `d1d5`, `e1g1`, `e4d5`

### Hints

Type `hint` during puzzle solving for progressive assistance:

1. **Level 1**: Piece to move (e.g., "Move your knight")
2. **Level 2**: Source square (e.g., "From g1")
3. **Level 3**: Destination square (e.g., "To f3")
4. **Level 4**: Full move (e.g., "Play Nf3")

## Project Structure

```
chesspuzzlegenerator/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── README.md                  # This file
│
├── config/                    # Configuration
│   ├── settings.py
│   └── constants.py
│
├── data/                      # Database layer
│   ├── database.py
│   ├── models.py
│   └── puzzle_loader.py
│
├── core/                      # Game logic
│   ├── puzzle_manager.py
│   ├── puzzle_selector.py
│   ├── move_validator.py
│   ├── hint_system.py
│   └── progress_tracker.py
│
├── rendering/                 # Board visualization
│   ├── board_renderer.py
│   └── image_utils.py
│
├── ui/                        # User interface
│   ├── cli.py
│   ├── input_handler.py
│   └── display.py
│
├── scripts/                   # Setup scripts
│   ├── download_puzzles.py
│   └── setup_database.py
│
└── storage/                   # Data storage (created during setup)
    ├── puzzles.db            # SQLite database
    ├── progress.json         # Your progress
    └── images/               # Generated board images
```

## Troubleshooting

### Database Not Found

If you see "Error: Puzzle database not found!", run the setup script:

```bash
python scripts/setup_database.py
```

### Import Interrupted

If database import is interrupted, you can resume by running setup again. The script will ask if you want to recreate the database.

### Move Not Recognized

Make sure you're using proper algebraic notation:
- Include piece letter for non-pawn moves: `Nf3` not `f3`
- Pawns don't need piece letter: `e4` not `Pe4`
- Captures use `x`: `Nxf3` or `exd5`
- Castling: `O-O` (kingside) or `O-O-O` (queenside)

### Board Image Not Displaying

The application generates PNG files in `storage/images/`. You need to open these images manually with your system's image viewer. Future versions may include inline display for compatible terminals.

## Statistics

View your progress anytime from the main menu:

- Total puzzles solved
- Success rate
- Current streak (consecutive solved)
- Best streak
- Breakdown by difficulty level

Progress is saved in `storage/progress.json`.

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black .
```

### Type Checking

```bash
mypy .
```

## Data Source

Puzzles are sourced from the [Lichess Puzzle Database](https://database.lichess.org/), which is freely available under Creative Commons licensing.

## Future Enhancements

Planned features for future versions:

- Stockfish integration for custom puzzle generation
- Web interface
- Timed puzzle mode
- Daily challenges
- Puzzle collections
- Performance analytics

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Lichess.org for the amazing puzzle database
- python-chess library for chess logic
- The open source chess community

## Support

For issues or questions:
1. Check this README
2. Review error messages carefully
3. Ensure all dependencies are installed
4. Verify database setup completed successfully

Enjoy solving puzzles!
