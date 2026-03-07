# Chess Trainer

An educational chess application built with Python and Pygame, featuring a modern dark UI, real-time position evaluation powered by Stockfish, move-quality feedback, interactive move history, and professional game lookup.

---

## Table of Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the App](#running-the-app)
- [How to Play](#how-to-play)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Panel Buttons](#panel-buttons)
- [Move Quality Labels](#move-quality-labels)
- [Building a Standalone Executable](#building-a-standalone-executable)
- [Project Structure](#project-structure)
- [License](#license)

---

## Features

- **Full chess game** – legal move validation, check/checkmate/stalemate detection, promotion.
- **Stockfish integration** – background engine analysis after every move with centipawn evaluation.
- **Win-percentage bars** – top (Black) and bottom (White) bars showing real-time advantage.
- **Horizontal eval bar** – shows engine score (+/- pawns, or mate) in the side panel.
- **Move-quality feedback** – every move is automatically classified as Best, Excellent, Good, Inaccuracy, Mistake, or Blunder based on centipawn loss.
- **Move history panel** – scrollable numbered move list with colour-coded quality badges.
- **Best-move suggestion** – on demand, a blue arrow points to the engine's top choice.
- **Custom arrows** – draw your own analysis arrows on the board.
- **Board flip** – view the position from Black's perspective.
- **Pro-game lookup** – searches games by Magnus Carlsen, Hikaru Nakamura, and Fabiano Caruana (via Chess.com API) for the current board position.
- **Fullscreen / windowed** – toggle at any time; the UI scales to any resolution.
- **Undo** – take back the last move instantly.

---

## Screenshots

> *(Add screenshots here once the app is running.)*

---

## Requirements

| Dependency | Version |
|---|---|
| Python | 3.10 or later |
| pygame | 2.6.1 |
| chess | 1.11.1 |
| requests | 2.32.3 |
| pyinstaller | ≥ 6.0 (build only) |

The full list is in [my_chess_game/requirements.txt](my_chess_game/requirements.txt).

### Stockfish engine

The app ships the Stockfish source code under `stockfish/`. You need the **compiled Windows binary** placed at:

```
my_chess_game/stockfish/stockfish/stockfish-windows-x86-64-avx2.exe
```

Download the latest release from the [official Stockfish website](https://stockfishchess.org/download/) and copy the `.exe` into that folder.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/chess.git
cd chess
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

**Windows (PowerShell)**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt)**
```cmd
.venv\Scripts\activate.bat
```

### 4. Install dependencies

```bash
pip install -r my_chess_game/requirements.txt
```

### 5. Add the Stockfish binary

Download the pre-compiled `stockfish-windows-x86-64-avx2.exe` from [stockfishchess.org](https://stockfishchess.org/download/) and place it at:

```
my_chess_game/stockfish/stockfish/stockfish-windows-x86-64-avx2.exe
```

---

## Running the App

With the virtual environment activated, run:

```bash
cd my_chess_game
python main.py
```

The application opens in **fullscreen** mode by default. Press **F11** or **Escape** to switch to a resizable window.

---

## How to Play

1. **Select a piece** – left-click any piece belonging to the side whose turn it is.  
   Legal destination squares are highlighted with dots (empty squares) or a coloured overlay (capture squares).

2. **Move the piece** – left-click a highlighted destination square to execute the move.

3. **Deselect** – click the same piece again, click an empty non-target square, or press **Escape**.

4. **Pawn promotion** – when a pawn reaches the last rank it is automatically promoted to a Queen.

5. **Draw arrows** – enable **Draw mode** (side panel button), then click-and-drag on the board to draw analysis arrows. Disable Draw mode to play normally again.

6. **Engine evaluation** – click **Evaluate** to toggle the real-time Stockfish bar. It re-analyses after every moved.

7. **Get the best move** – click **Suggest** to show a blue arrow indicating the engine's recommended move.

8. **Pro-game lookup** – click **Pro Games** after reaching any position to see whether Magnus Carlsen, Hikaru Nakamura, or Fabiano Caruana played through that exact position in January 2024.

---

## Keyboard Shortcuts

| Key | Action |
|---|---|
| `←` (Left Arrow) | Undo the last move |
| `F` | Flip the board (swap White / Black perspective) |
| `F11` | Toggle fullscreen / windowed |
| `Escape` | Close overlays → deselect piece → exit fullscreen |

---

## Panel Buttons

All buttons are in the right-side panel.

| Button | Description |
|---|---|
| **New Game** | Reset the board and move history to the starting position. |
| **Pro Games** | Fetch professional games matching the current board position from Chess.com. |
| **Suggest** | Ask Stockfish for its best move and display it as a blue arrow. |
| **Draw / Stop** | Toggle arrow-drawing mode on/off (clears existing arrows when toggled off). |
| **Evaluate** | Toggle the engine evaluation bar and win-percentage display. |
| **Undo** | Take back the last half-move. |
| **Flip** | Mirror the board to view from the opposite side. |

---

## Move Quality Labels

After each move, Stockfish calculates the **centipawn loss** compared to the best available move. The result is labelled and colour-coded in the move history:

| Label | Centipawn Loss | Colour |
|---|---|---|
| **Best** | 0 | Green |
| **Excellent** | 1 – 10 | Light green |
| **Good** | 11 – 25 | Yellow-green |
| **Inaccuracy** | 26 – 50 | Yellow |
| **Mistake** | 51 – 100 | Orange |
| **Blunder** | > 100 | Red |

---

## Building a Standalone Executable

A build script and PyInstaller spec file are included to produce a Windows `.exe` installer.

### Prerequisites

- [Inno Setup 6](https://jrsoftware.org/isinfo.php) installed at `C:\Program Files (x86)\Inno Setup 6\ISCC.exe`
- Virtual environment created and dependencies installed (see [Installation](#installation))

### Steps

```cmd
cd my_chess_game
build.bat
```

The script performs four steps:

1. Upgrades PyInstaller inside the venv.
2. Runs PyInstaller using `chess_trainer.spec` → output in `dist\chess_trainer\`.
3. Runs Inno Setup using `setup.iss` → produces `installer\Setup_ChessTrainer.exe`.
4. Reports success.

Distribute the generated `Setup_ChessTrainer.exe` to end-users. No Python installation is required on their machines.

---

## Project Structure

```
chess/
├── README.md
├── LICENSE
└── my_chess_game/
    ├── main.py               # Application entry point & main game loop
    ├── metrics.py            # Colour palette, Layout, HistoryOfMoves classes
    ├── history_of_games.py   # Chess.com API integration for pro-game lookup
    ├── requirements.txt      # Python dependencies
    ├── chess_trainer.spec    # PyInstaller build specification
    ├── build.bat             # Windows build script (PyInstaller + Inno Setup)
    ├── setup.iss             # Inno Setup installer script
    ├── pieces/               # SVG chess piece images + app logo
    └── stockfish/            # Stockfish source code
        └── stockfish/
            └── stockfish-windows-x86-64-avx2.exe   # ← place binary here
```

---

## License

This project is licensed under the terms found in [LICENSE](LICENSE).  
Stockfish is distributed under the [GNU General Public License v3](stockfish/stockfish/Copying.txt).
