# main.py

import sys
from src.game_logic import Connect6Game
from src.gui import Connect6GUI

def main_console():
    """Run the game in console mode (Player vs AI)."""
    game = Connect6Game(size=19, human_player='X', ai_player='O', ai_algorithm='minimax')
    print("=== Connect 6 - Player vs AI ===")
    print(f"You are Player {game.human_player}, AI is Player {game.ai_player}")
    game.board.display()

    while True:
        # Human player's turn
        if game.is_human_turn():
            print(f"\nYour turn (Player {game.human_player})")
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
                    # Game ended
                    if game.board.is_full():
                        print("It's a draw!")
                    else:
                        winner = game.current_player
                        if winner == game.human_player:
                            print("Congratulations! You win!")
                        else:
                            print(f"AI (Player {game.ai_player}) wins!")
                    break  # Game ended
            # Show board either after successful turn or after invalid attempt (no change on invalid)
            game.board.display()
        
        # AI player's turn
        elif game.is_ai_turn():
            print(f"\nAI (Player {game.ai_player}) is thinking...")
            
            # Get AI move from the algorithm
            # TODO: The get_ai_move() method should call the actual minimax/alpha_beta algorithms
            # Currently it returns a placeholder. Once the algorithms are implemented,
            # this will automatically use them.
            ai_moves = game.get_ai_move(depth=3)  # depth can be adjusted for AI strength
            
            if not ai_moves:
                print("AI Error: No valid moves available!")
                break
            
            # Display AI's moves
            moves_text = ", ".join(f"({x + 1}, {y + 1})" for x, y in ai_moves)
            print(f"AI plays: {moves_text}")
            
            # Play AI's turn
            if game.play_turn(ai_moves):
                # Game ended
                game.board.display()
                if game.board.is_full():
                    print("It's a draw!")
                else:
                    winner = game.current_player
                    if winner == game.human_player:
                        print("Congratulations! You win!")
                    else:
                        print(f"AI (Player {game.ai_player}) wins!")
                break  # Game ended
            
            # Show board after AI's move
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
