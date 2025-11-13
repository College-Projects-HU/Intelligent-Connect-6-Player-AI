import game_logic as connect6
import constants as c
import math

class AlphaBetaPruning:
    def __init__(self, game, max_depth=c.DEFUALT_DEPTH):
        self.game = game
        self.max_depth = max_depth

    
    def get_opponent(self, player):
        return c.AI if player == c.PLAYER else c.AI 
    
    def evaluate_board(self, game):
        """
            Evaluation function that takes a game and return a number\n
            Returns inf/-inf for max/min winning states\n
            Otherwise, returns heuristic value 
        """
        # Check for wins first
        win = game.check_winner(game.last_x, game.last_y)
        winner = game.get_winner(game.last_x, game.last_y)
        
        if win:
            return math.inf if winner == c.AI else -math.inf
        elif game.check_draw():
            return 0
        else:
            # If no win, return a heuristic score (implement your own logic here)
            # Placeholder - implement proper board evaluation
            return 0 
    
    def alpha_beta(self, game, depth, alpha, beta, maximizing_player):
        win = game.check_winner(game.last_x, game.last_y)
        draw = game.check_draw()
        
        if (not depth) or draw or win:
            return self.evaluate_board(game) 
    
        if maximizing_player:
            return self.max_node(game, depth, alpha, beta)
        else:
            return self.min_node(game, depth, alpha, beta)
    
    
    def max_node(self, game, depth, alpha, beta):
        max_score = -math.inf
        orig_r, orig_c = game.last_row, game.last_col
        outer_break = False  # pruning ya 4bab
        
        moves = game.get_available_moves()
        
        for i in range(len(moves)):
            x1, y1 = moves[i]
            game.board[x1][y1] = game.current_player  # SET FIRST STONE
            game.last_row = x1
            game.last_col = y1

            for j in range(i + 1, len(moves)):
                x2, y2 = moves[j]
                
                game.board[x2][y2] = game.current_player # SET SECOND STONE
                game.last_row = x2
                game.last_col = y2

                # What's going to happen from now on? (this comment for me to remind myself cus I get lost very often)
                score = self.alpha_beta(game, depth - 1, alpha, beta, False)

                # clear 2nd stone
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
        
    def min_node(self, game, depth, alpha, beta):
        min_score = math.inf
        orig_r, orig_c = game.last_row, game.last_col
        outer_break = False  # pruning ya 4bab
        
        moves = game.get_available_moves()
        
        for i in range(len(moves)):
            x1, y1 = moves[i]
            game.board[x1][y1] = game.current_player  # SET FIRST STONE
            game.last_row = x1
            game.last_col = y1
    
            for j in range(i + 1, len(moves)):
                x2, y2 = moves[j]
                
                game.board[x2][y2] = game.current_player  # SET SECOND STONE
                game.last_row = x2
                game.last_col = y2
    
                # What's going to happen from now on?
                score = self.alpha_beta(game, depth - 1, alpha, beta, True)  # True for maximizing next
    
                # clear 2nd stone
                game.board[x2][y2] = c.EMPTY
                
                # Restore state to *after move 1*
                game.last_row = x1
                game.last_col = y1
    
                # MIN score and pruning
                min_score = min(min_score, score)  # Use min instead of max
                beta = min(beta, score)  # Update beta instead of alpha
                if beta <= alpha:  # Same pruning condition
                    outer_break = True
                    break
    
            # Reset first stone
            game.board[x1][y1] = c.EMPTY
    
            if outer_break: break
    
        game.last_row = orig_r
        game.last_col = orig_c
        return min_score  # Return min_score instead of max_score
    
    def find_best_move(self, game):
        best_score = -math.inf
        best_move = None
        orig_r, orig_c = game.last_row, game.last_col
        moves = game.get_available_moves()
        
        for i in range(len(moves)):
            x1, y1 = moves[i]
            game.board[x1][y1] = game.current_player # SET FIRST STONE
            game.last_row = x1
            game.last_col = y1

            for j in range(i + 1, len(moves)):
                x2, y2 = moves[j]
                game.board[x2][y2] = game.current_player # SET SECOND STONE
                game.last_row = x2
                game.last_col = y2
    
                # What's going to happen from now on?
                score = self.alpha_beta(game, game.depth, -math.inf, math.inf, False)
    
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