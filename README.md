# Chess Puzzle Generator

A feature-rich Python console application for solving chess puzzles from the Lichess database. Practice tactics with 5.4M+ puzzles, filter by difficulty and themes, get progressive hints, and track your improvement over time.

## ✨ Features

- **5.4M+ Chess Puzzles** from the Lichess database
- **Difficulty Levels 1-5** (rated 600-3000) for all skill levels
- **Theme Filtering** - Practice specific tactics (40+ themes: forks, pins, checkmates, etc.)
- **Game Phase Selection** - Focus on opening, middlegame, or endgame positions
- **Progressive Hint System** - 4 levels of hints with visual board highlights
- **Inline Board Display** - PNG images render directly in iTerm2/Kitty terminals
- **Automatic Timer** - Stopwatch tracks your solve times
- **Progress Tracking** - View statistics, streaks, and improvement over time
- **Colorful UI** - ANSI colors for better visual experience
- **Flexible Move Input** - Supports both SAN (Nf3) and UCI (g1f3) notation

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

1. **Select difficulty** (1-5):
   - Level 1: Beginner (600-1200)
   - Level 2: Intermediate (1200-1600)
   - Level 3: Advanced (1600-2000)
   - Level 4: Expert (2000-2400)
   - Level 5: Master (2400-3000)

2. **Select game phase** (1-3):
   - 1 = Opening positions
   - 2 = Middlegame positions
   - 3 = Endgame positions

3. **Choose a theme** (optional):
   - Select from top 10 popular themes (fork, pin, mate in 2, etc.)
   - Type a specific theme name
   - Press Enter to skip (random theme)

4. **Solve the puzzle**:
   - Board displays inline (iTerm2/Kitty) or as PNG file path
   - Enter moves in algebraic notation (e.g., `Nf3`, `Qxd5`, `e4`)
   - Type `hint` for progressive hints (4 levels with visual highlights)
   - Type `quit` or press `ESC` to exit puzzle
   - Timer automatically tracks your solve time

### Move Notation

The application supports two notation formats:

- **Standard Algebraic Notation (SAN)**: `Nf3`, `Qxd5`, `O-O`, `exd5+`
- **UCI notation**: `g1f3`, `d1d5`, `e1g1`, `e4d5`

### Hints

Type `hint` during puzzle solving for progressive assistance with visual highlights:

1. **Level 1**: Piece to move (e.g., "Move your knight")
2. **Level 2**: Source square (e.g., "From g1") + highlighted square
3. **Level 3**: Destination square (e.g., "To f3") + highlighted square
4. **Level 4**: Full move (e.g., "Play Nf3")

Each hint generates a new board image with highlighted squares to guide you.

### Popular Themes

Practice specific tactical patterns:

**Tactical Themes:**
- `fork` - Attack multiple pieces simultaneously
- `pin` - Restrict piece movement
- `skewer` - Force valuable piece away
- `discoveredAttack` - Reveal hidden attack
- `sacrifice` - Give material for advantage
- `deflection` - Remove defender
- `doubleCheck` - Check with two pieces

**Checkmate Patterns:**
- `mateIn2` - Two-move checkmates
- `mateIn3` - Three-move checkmates
- `backRankMate` - Back rank patterns
- `smotheredMate` - Knight mate with blocked king
- `anastasia` - Knight and rook mate

See `config/constants.py` for the complete list of 40+ themes.

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

### Board Image Not Displaying Inline

If you're not seeing the board inline in your terminal:

1. **Check terminal compatibility**: iTerm2, Kitty, and WezTerm support inline images
2. **Fallback mode**: The app will show the PNG file path instead
3. **Open manually**: Board images are saved in `storage/images/puzzle_<id>.png`
4. **Try iTerm2**: Download from https://iterm2.com for the best experience

## Statistics & Progress Tracking

View your progress anytime from the main menu:

- **Total puzzles solved** and attempts
- **Success rate** percentage
- **Current streak** (consecutive solved)
- **Best streak** (personal record)
- **Breakdown by difficulty** level with visual bars
- **Solve times** tracked automatically

Progress is saved in `storage/progress.json` and persists across sessions.

## Terminal Compatibility

### Inline Board Display

The application supports inline PNG rendering for compatible terminals:

- ✅ **iTerm2** (macOS) - Full support
- ✅ **Kitty** - Full support
- ✅ **WezTerm** - Full support
- ⚠️ **Other terminals** - Falls back to PNG file paths

For the best experience, use iTerm2 or Kitty to see the chess board rendered directly in your terminal!

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

## Screenshots

The application features a colorful, modern terminal UI:

- **Cyan** numbers for menu selections
- **Yellow** for hints and descriptions
- **Green** for success messages and theme names
- **Red** for errors
- **Bold** text for headers

Board images render inline in compatible terminals (iTerm2, Kitty) with pieces and highlighted squares.

## What Makes This Different?

- **Massive Database**: 5.4M+ curated puzzles from Lichess
- **Smart Filtering**: Combine difficulty + game phase + theme for targeted practice
- **Progressive Learning**: Hint system teaches without giving away answers
- **Visual Feedback**: Inline board rendering with highlighted squares
- **Track Progress**: See your improvement with statistics and streaks
- **Fast & Offline**: SQLite database runs locally, no API calls needed
- **Modern Terminal UI**: Colorful ANSI interface feels responsive and polished

## Future Enhancements

Potential features for future versions:

- Stockfish integration for position evaluation
- Spaced repetition system for optimal learning
- Custom puzzle collections and playlists
- Daily challenges and leaderboards
- Opening repertoire training
- Performance analytics and weakness detection

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
