# Intelligent Connect 6 Player AI

A Python-based implementation of the strategic board game **Connect 6**, featuring an intelligent AI opponent capable of playing against humans using Minimax and Alpha-Beta pruning algorithms.

## 🎮 About the Game

**Connect 6** is a two-player strategy game similar to Gomoku (Five in a Row), but with a unique twist that makes it fairer and more dynamic.

**Rules:**
1.  **Black** (Player 1) plays the **first move** by placing **one** stone.
2.  **White** (Player 2) plays the next turn by placing **two** stones.
3.  All subsequent turns consist of placing **two** stones.
4.  The goal is to be the first to get **six** or more stones in a row (horizontally, vertically, or diagonally).

## ✨ Features

-   **Two Game Modes**:
    -   **GUI Mode**: A user-friendly graphical interface built with `tkinter`.
    -   **Console Mode**: A command-line interface for terminal-based play.
-   **Intelligent AI**:
    -   **Algorithms**: Choose between **Minimax** and **Alpha-Beta Pruning**.
    -   **Heuristics**:
        -   *Heuristic 1*: Basic pattern matching (counting sequences).
        -   *Heuristic 2*: Advanced evaluation considering threats and center control.
    -   **Dynamic Difficulty**: AI depth and algorithm can be adjusted.
-   **Customizable**: Supports customizable board sizes (from 6x6 to 19x19).
-   **Undo Functionality**: Easily undo moves in GUI mode if you make a mistake or want to change your AI settings.

## 🚀 Getting Started

### Prerequisites

-   **Python 3.6+**
-   Standard libraries only (uses `tkinter` for GUI).

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/College-Projects-HU/Intelligent-Connect-6-Player-AI.git
    cd Intelligent-Connect-6-Player-AI
    ```

## 🕹️ Usage

### Graphical Interface (Recommended)

Run the game with the default GUI:

```bash
python main.py
```

1.  Enter the desired board size (default is 19).
2.  Play your turn by clicking on the board.
3.  Confirm your move.
4.  Watch the AI calculate and respond!

### Console Mode

Play directly in your terminal:

```bash
python main.py --console
```

Follow the prompts to enter coordinates for your moves.

### AI Simulation

Watch a short simulated game between a simple strategy and the AI:

```bash
python run_playthrough.py
```

## 🧠 AI Implementation Details

The AI evaluates the board state using a scoring system:

-   **Positive Logic**: It rewards sequences of its own stones (2, 3, 4, 5 in a row).
-   **Negative Logic**: It penalizes opponent sequences to prioritize blocking.
-   **Search Algorithms**:
    -   **Minimax**: Explores the game tree to a fixed depth to find the optimal move.
    -   **Alpha-Beta Pruning**: Optimizes Minimax by ignoring branches that won't affect the final decision, allowing for deeper searches.

## 📂 Project Structure

```
Intelligent-Connect-6-Player-AI/
├── main.py                 # Main entry point (GUI/Console)
├── run_playthrough.py      # Script for AI vs AI simulation
├── requirements.txt        # Project dependencies
├── src/
│   ├── board.py            # Board representation and logic
│   ├── game_logic.py       # Game rules and state management
│   ├── gui.py              # Tkinter GUI implementation
│   ├── minimax.py          # Minimax algorithm implementation
│   ├── alpha_beta.py       # Alpha-Beta pruning implementation
│   ├── heuristics.py       # Evaluation functions
│   └── constants.py        # Configuration constants
└── tests/                  # Unit tests
```