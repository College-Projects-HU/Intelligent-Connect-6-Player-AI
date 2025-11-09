# main.py

import sys
from src.game_logic import Connect6Game
from src.gui import Connect6GUI

def main_console():
    """Run the game in console mode."""
    game = Connect6Game(size=19)
    print("=== Connect 6 ===")
    game.board.display()

    while True:
        print(f"Player {game.current_player}'s turn")
        required_moves = 1 if game.first_move else 2
        print(f"Place {required_moves} stone(s). Enter coordinates as 'x y' (0-indexed).")

        moves = []
        for i in range(required_moves):
            try:
                raw = input(f"Move {i+1}: ").strip()
                x, y = map(int, raw.split())
            except ValueError:
                print("Invalid input. You must enter two integers separated by space.")
                break  # break out to re-prompt the whole turn
            moves.append((x, y))
        else:
            # Attempt to play the atomic turn
            if game.play_turn(moves):
                break  # Game ended
        # Show board either after successful turn or after invalid attempt (no change on invalid)
        game.board.display()

def main_gui():
    """Run the game in GUI mode."""
    app = Connect6GUI(size=19)
    app.run()

def main():
    """Main entry point. Launches GUI by default, or console if --console flag is used."""
    if len(sys.argv) > 1 and sys.argv[1] == "--console":
        main_console()
    else:
        main_gui()

if __name__ == "__main__":
    main()
