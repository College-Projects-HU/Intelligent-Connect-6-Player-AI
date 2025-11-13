import game_logic as connect6
import constants as c
import math

class AlphaBetaPruning:
    def __init__(self, game):
        self.game = game
        
        
    def alpha_beta(self, game, depth, alpha, beta, maximizing_player):

        if depth == 0 or game.check_draw():
            return 0 # 3ayz evaluation function
    
    
        if maximizing_player:
            max_score = -math.inf
            orig_r, orig_c = game.last_row, game.last_col
            outer_break = False  # For pruning
    
            for (x1, y1) in game.get_all_legal_moves():
                game.board[x1][y1] = game.current_player  # SET FIRST STONE
                game.last_row = x1
                game.last_col = y1
    
                for (x2, y2) in game.get_all_legal_moves():
                    # SET SECOND STONE
                    game.board[x2][y2] = game.current_player
                    game.last_row = x2
                    game.last_col = y2
    
    
                    # What's going to happen from now on?
                    score = self.alpha_beta(game, depth - 1, alpha, beta, False)
    
                    # Reset second stone
                    game.board[x2][y2] = c.EMPTY
                    # Restore state to *after move 1*
                    game.last_row = x1
                    game.last_col = y1
    
                    # MAX score and pruning
                    max_score = max(max_score, score)
                    alpha = max(alpha, score)
                    if beta <= alpha:
                        outer_break = True
                        break
                # Reset first stone
                game.board[x1][y1] = c.EMPTY
    
                if outer_break: break
    
            game.last_row = orig_r
            game.last_col = orig_c
            return max_score
        else:
            min_score = math.inf
            # 1. Save the state *once*
            orig_r, orig_c = game.last_row, game.last_col
    
            outer_break = False
            for (x1, y1) in game.get_all_legal_moves():
                game.board[x1][y1] = connect6.PLAYER_1
                game.last_row = x1
                game.last_col = y1
    
                for (x2, y2) in game.get_all_legal_moves():
                    game.board[x2][y2] = connect6.PLAYER_1
                    game.last_row = x2
                    game.last_col = y2
    
                    score = alpha_beta(game, depth - 1, alpha, beta, True)
    
                    # Undo move 2
                    game.board[x2][y2] = c.EMPTY
                    # Restore state to *after move 1*
                    game.last_row = x1
                    game.last_col = y1
    
                    min_score = min(min_score, score)
                    beta = min(beta, score)
                    if beta <= alpha:
                        outer_break = True
                        break
    
                # Undo move 1
                game.board[x1][y1] = c.EMPTY
                if outer_break:
                    break
    
            # 2. Restore the *original* state
            game.last_row = orig_r
            game.last_col = orig_c
            return min_score
    
    
    def find_best_move(game):
        best_score = -math.inf
        best_move = None
        orig_r, orig_c = game.last_row, game.last_col
        for (x1, y1) in game.get_all_legal_moves():
            game.board[x1][y1] = game.current_player # SET FIRST STONE
            game.last_row = x1
            game.last_col = y1
    
            for (x2, y2) in game.get_all_legal_moves():
                game.board[x2][y2] = game.current_player # SET SECOND STONE
                game.last_row = x2
                game.last_col = y2
    
                # What's going to happen from now on?
                score = alpha_beta(game, game.depth, -math.inf, math.inf, False)
    
                if score >= best_score:
                    best_score = score
                    best_move = [(x1, y1), (x2, y2)]
    
                # Reset second stone
                game.board[x2][y2] = c.EMPTY
                # Restore state to *after move 1*
                game.last_row = x1
                game.last_col = y1
            # Reset first stone
            game.board[x1][y1] = c.EMPTY
            # 2. Restore the *original* state
            game.last_row = orig_r
            game.last_col = orig_c
    
        return best_move