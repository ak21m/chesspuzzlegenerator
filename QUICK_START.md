# Quick Start Guide - New Features! 🎉

All three new features are now fully integrated and working:

## ✅ What's New

### 1. **ASCII Board Display** ♟️
- Board now renders **directly in your terminal** with beautiful Unicode pieces
- No need to open PNG files!
- Colored squares (light/dark)
- Highlights for hints
- Automatic fallback to PNG if terminal doesn't support Unicode

### 2. **Theme Filtering** 🎯
- Practice specific tactics: forks, pins, skewers, etc.
- See top 10 popular themes with puzzle counts
- Type a theme name or select by number
- Press Enter to skip (random theme)

### 3. **Timer Mode** ⏱️
- **Automatic stopwatch** tracks your solve time
- Timer shows elapsed time during puzzle solving
- Times recorded in statistics for tracking improvement

## 🚀 How to Use

### Starting the App:
```bash
./run.sh
```
or
```bash
source venv/bin/activate
export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib
python main.py
```

### Complete Puzzle Flow:

1. **Select "Play Puzzle"** from main menu

2. **Choose Difficulty** (1-5):
   ```
   Enter difficulty (1-5): 3
   ```

3. **Choose Game Phase**:
   ```
   Select game phase:
     1 = Opening positions
     2 = Middlegame positions
     3 = Endgame positions

   Game phase (1-3): 2
   ```

4. **Select Theme** (NEW! 🎯):
   ```
   Select a theme (or press Enter for any theme):
     0 = Any theme (random)
     1 = fork (1247 puzzles)
     2 = pin (892 puzzles)
     3 = mateIn2 (756 puzzles)
     ...

   Theme choice (0 for any): 1
   ```
   This will give you **fork puzzles only**!

5. **Solve the Puzzle** (NEW! ♟️):
   ```
   ╔════════════════════════╗
 8 │ ♜ ♞ ♝ ♛ ♚ ♝ ♞ ♜ │
 7 │ ♟ ♟ ♟ ♟   ♟ ♟ ♟ │
 6 │               ♟     │
 5 │                     │
 4 │           ♙ ♟       │
 3 │                     │
 2 │ ♙ ♙ ♙ ♙   ♙ ♙ ♙ │
 1 │ ♖ ♘ ♗ ♕ ♔ ♗ ♘ ♖ │
   ╚════════════════════════╝
     a  b  c  d  e  f  g  h

   Elapsed: 00:12

   White to move:
   ```
   **Note**: Timer runs automatically in stopwatch mode!

6. **Enter your move**:
   - SAN notation: `Nf3`, `Qxd5`, `O-O`
   - UCI notation: `g1f3`, `d1d5`
   - Type `hint` for progressive hints (highlights shown on board!)
   - Type `quit` or press `ESC` to exit

## 🎨 ASCII Board Features

The board updates automatically:
- After each move
- When you request hints (with highlighted squares!)
- Shows current position with piece colors

**Example with highlights:**
```
Hint (Level 2): Move the knight from g1

╔════════════════════════╗
8 │ ♜ ♞ ♝ ♛ ♚ ♝ ♞ ♜ │
...
1 │ ♖ ♘[♗]♕ ♔ ♗ ♘ ♖ │    ← Highlighted square!
  ╚════════════════════════╝
```

## ⏱️ Timer Display

During puzzle solving:
```
Time remaining: 02:37    ← Countdown mode

Your move: Nf3
```

or

```
Elapsed: 01:23           ← Stopwatch mode

Your move: Nf3
```

After completion:
```
Puzzle solved! Well done!
Completed in 01:45

✓ Attempts: 1
✓ Time: 01:45
✓ Hints used: 0
✓ Theme: fork
```

## 🎯 Popular Themes to Try

**Tactical:**
- `fork` - Attack multiple pieces
- `pin` - Restrict piece movement
- `skewer` - Force valuable piece away
- `discoveredAttack` - Reveal hidden attack
- `sacrifice` - Give material for advantage

**Checkmates:**
- `mateIn2` - Two-move checkmates
- `mateIn3` - Three-move checkmates
- `backRankMate` - Back rank patterns
- `smotheredMate` - Knight mate with blocked king

**Try them out:**
1. Start with `fork` (difficulty 2-3)
2. Move to `pin` and `skewer` (difficulty 3)
3. Practice `mateIn2` (difficulty 2-4)
4. Challenge with `mateIn3` (difficulty 3-5)

## 💡 Pro Tips

1. **Learning Mode**: Use **theme filtering** to focus
   - Focus on one tactic at a time
   - Take your time to understand patterns
   - Timer tracks your progress automatically

2. **Speed Training**: Mix themes and difficulty
   - Track improvement over time with automatic timing
   - Build pattern recognition speed

3. **Progressive Practice**:
   - Week 1: Forks (difficulty 2)
   - Week 2: Pins (difficulty 2-3)
   - Week 3: Mate in 2 (difficulty 3)
   - Week 4: Mix themes (difficulty 3-4)
   - Review your timing stats to see improvement!

## 🐛 Troubleshooting

**Board shows weird characters:**
- Your terminal might not support Unicode
- App will automatically fallback to PNG images
- Try a modern terminal (iTerm2, Windows Terminal, etc.)

**Theme not working:**
- Some themes have fewer puzzles
- App will automatically fallback to broader themes
- Try popular themes like `fork`, `pin`, `mateIn2`

## 📊 View Your Statistics

From the main menu, select option 2 to see:
- Total puzzles solved
- Success rate
- Best/current streak
- Breakdown by difficulty
- **NEW**: Timing statistics (if you used timer mode)

## 🎮 Ready to Play!

Run the app and try it out:
```bash
./run.sh
```

Enjoy the new features! The board looks amazing in the terminal, themes help you focus on specific tactics, and the timer adds a fun challenge! 🚀♟️
