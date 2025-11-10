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
        size = game.board.size
        print(f"Place {required_moves} stone(s). Enter coordinates as 'x y' (1-{size}).")

        moves = []
        for i in range(required_moves):
            try:
                raw = input(f"Move {i+1}: ").strip()
                x_input, y_input = map(int, raw.split())
            except ValueError:
                print("Invalid input. You must enter two integers between 1 and "
                      f"{size}, separated by space.")
                break  # break out to re-prompt the whole turn
            moves.append((x_input - 1, y_input - 1))
        else:
            confirmation_moves = ", ".join(
                f"({x + 1}, {y + 1})" for x, y in moves
            )
            confirmation_prompt = (
                f"Confirm moves {confirmation_moves}? (y/n): "
            )
            if input(confirmation_prompt).strip().lower() not in ("y", "yes"):
                print("Move cancelled. Please re-enter your coordinates.")
                continue
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
