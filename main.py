# main.py

import sys
from src.game_logic import Connect6Game
from src.gui import Connect6GUI

def get_board_size():
    """
    Get board size from user with validation (6-19).

    Returns:
        int: Valid board size between 6 and 19
    """
    print("=== Connect 6 Game Setup ===")
    print()

    while True:
        try:
            size_input = input("Enter board size (6-19): ").strip()
            size = int(size_input)
            if size < 6:
                print("Board size must be at least 6. Please try again.")
                continue
            if size > 19:
                print("Board size must be at most 19. Please try again.")
                continue
            return size
        except ValueError:
            print("Invalid input. Please enter a number between 6 and 19.")

def get_ai_algorithm_choice():
    """
    Get AI algorithm choice from user before each AI turn.
    
    Returns:
        tuple: (algorithm, heuristic) where algorithm is 'minimax' or 'alpha_beta'
               and heuristic is 'heuristic_1' or 'heuristic_2'
    """
    print()
    print("Choose AI Algorithm for this turn:")
    print("1 - Minimax with 1st heuristic")
    print("2 - Minimax with 2nd heuristic")
    print("3 - Alpha-Beta with 1st heuristic")
    print("4 - Alpha-Beta with 2nd heuristic")
    print()
    
    while True:
        try:
            choice = input("Enter your choice (1-4): ").strip()
            choice_num = int(choice)
            if choice_num == 1:
                return 'minimax', 'heuristic_1'
            elif choice_num == 2:
                return 'minimax', 'heuristic_2'
            elif choice_num == 3:
                return 'alpha_beta', 'heuristic_1'
            elif choice_num == 4:
                return 'alpha_beta', 'heuristic_2'
            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def main_console():
    """Run the game in console mode (Player vs AI)."""
    board_size = get_board_size()
    game = Connect6Game(size=board_size, human_player='X', ai_player='O', ai_algorithm='minimax', heuristic='heuristic_1')
    print()
    print("=== Connect 6 - Player vs AI ===")
    print(f"Board size: {board_size}x{board_size}")
    print(f"You are Player {game.human_player}, AI is Player {game.ai_player}")
    print()
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
                    if game.is_draw():
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
            # Let user choose AI algorithm before AI's turn
            algorithm, heuristic = get_ai_algorithm_choice()
            game.set_ai_config(algorithm, heuristic)
            print(f"\nAI (Player {game.ai_player}) is thinking using {algorithm} with {heuristic}...")
            
            # Get AI move from the algorithm
            ai_depth = 1 if algorithm == 'minimax' else 2 
            ai_moves = game.get_ai_move(depth=ai_depth)  # depth can be adjusted for AI strength
            
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
                if game.is_draw():
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
    # Get board size from GUI dialog
    board_size = Connect6GUI.get_board_size_dialog()
    if board_size is None:
        print("Game cancelled.")
        return
    app = Connect6GUI(size=board_size)
    app.run()

def main():
    """Main entry point. Launches GUI by default, or console if --console flag is used."""
    if len(sys.argv) > 1 and sys.argv[1] == "--console":
         main_console()
    else:
         main_gui()

if __name__ == "__main__":
    main()