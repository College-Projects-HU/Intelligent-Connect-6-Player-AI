from importlib import import_module

m_game = import_module('src.game_logic')

# Simulate a short human vs AI game on a small board to observe AI behavior
BOARD = 9
DEPTH = 2


def print_board(game):
    game.board.display()


def human_move_simple(game):
    """Simple human strategy: place near last human moves or center.
    Picks one or two moves depending on `first_move`."""
    size = game.board.size
    avail = game.get_available_moves()
    # prefer cells near center
    center = (size // 2, size // 2)
    sorted_avail = sorted(avail, key=lambda c: (abs(c[0]-center[0]) + abs(c[1]-center[1])))
    required = 1 if game.first_move else 2
    # pick first `required` available
    return sorted_avail[:required]


def play():
    game = m_game.Connect6Game(size=BOARD, human_player='X', ai_player='O', ai_algorithm='minimax')
    turn = 0
    print('Starting playthrough: human vs AI (minimax)')
    print_board(game)

    while turn < 40:
        # Human turn
        if game.is_human_turn():
            moves = human_move_simple(game)
            print(f'Human plays: {moves}')
            ended = game.play_turn(moves)
            print_board(game)
            if ended:
                print('Game ended after human move')
                break

        # AI turn
        if game.is_ai_turn():
            game.set_ai_config('minimax', 'heuristic_2')
            print('AI thinking...')
            ai_moves = game.get_ai_move(depth=DEPTH)
            print(f'AI plays: {ai_moves}')
            ended = game.play_turn(ai_moves)
            print_board(game)
            if ended:
                print('Game ended after AI move')
                break

        turn += 1

    print('Playthrough finished')


if __name__ == '__main__':
    play()
