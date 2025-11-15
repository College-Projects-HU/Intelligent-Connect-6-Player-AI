import src.game_logic as connect6
import src.constants as c
import math

class AlphaBetaPruning:
    def __init__(self, game, heuristic, max_depth=c.DEFUALT_DEPTH):
        self.game = game
        self.max_depth = max_depth
        self.heuristic = heuristic

    def __evaluate_board(self, game, win, draw):
        """
            Evaluation function that takes a game and returns a number\n
            Returns inf/-inf for max/min winning states\n
            Otherwise, returns heuristic value (for god's sake, get it done by next sunday)
        """
        if win:
            winner = game.board.grid[game.last_x][game.last_y]
            return math.inf if winner == c.AI else -math.inf
        elif draw:
            return 0
        else:
            if self.heuristic == c.EVAL1:
                return 0 # Replaced by heuristic_1
            else:
                return 0 # Replaced by heuristic_2 

    def alpha_beta(self, game, depth, alpha, beta, maximizing_player):
        win = game.check_winner(game.last_x, game.last_y)
        draw = game.check_draw()
        
        if (not depth) or draw or win:
            return self.__evaluate_board(game, win, draw) 
    
        if maximizing_player:
            return self.__max_node(game, depth, alpha, beta)
        else:
            return self.__min_node(game, depth, alpha, beta)
    
    def __max_node(self, game, depth, alpha, beta):
        max_score = -math.inf
        orig_r, orig_c = game.last_row, game.last_col
        outer_break = False  # pruning ya 4bab
        
        moves = game.get_available_moves()
        
        for i in range(len(moves)):
            x1, y1 = moves[i]
            game.board.grid[x1][y1] = c.AI  # SET FIRST STONE
            game.last_row = x1
            game.last_col = y1

            for j in range(i + 1, len(moves)):
                x2, y2 = moves[j]
                
                game.board.grid[x2][y2] = c.AI # SET SECOND STONE
                game.last_row = x2
                game.last_col = y2

                # What's going to happen from now on? (this comment for me to remind myself cus I get lost very often)
                score = self.alpha_beta(game, depth - 1, alpha, beta, False)

                # clear 2nd stone
                game.board.grid[x2][y2] = c.EMPTY
                
                # Restore state to *after move 1*
                game.last_row = x1
                game.last_col = y1

                # MAX score and pruning
                max_score = max(max_score, score)
                alpha = max(alpha, score)
                if beta <= alpha:
                    outer_break = True
                    break

            # clear 1st stone
            game.board[x1][y1] = c.EMPTY
            
            if outer_break: break

        game.last_row = orig_r
        game.last_col = orig_c
        
        return max_score
        
    def __min_node(self, game, depth, alpha, beta):
        min_score = math.inf
        orig_r, orig_c = game.last_row, game.last_col
        outer_break = False  # pruning ya 4bab

        moves = game.get_available_moves()
        
        for i in range(len(moves)):
            x1, y1 = moves[i]
            game.board.grid[x1][y1] = c.PLAYER  # SET FIRST STONE
            game.last_row = x1
            game.last_col = y1

            for j in range(i + 1, len(moves)):
                x2, y2 = moves[j]
                
                game.board.grid[x2][y2] = c.PLAYER  # SET SECOND STONE
                game.last_row = x2
                game.last_col = y2
    
                # What's going to happen from now on?
                score = self.alpha_beta(game, depth - 1, alpha, beta, True)  # True for maximizing next
    
                # clear 2nd stone
                game.board.grid[x2][y2] = c.EMPTY
                
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
            game.board.grid[x1][y1] = c.EMPTY
    
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
            game.board.grid[x1][y1] = c.AI # SET FIRST STONE
            game.last_row = x1
            game.last_col = y1

            for j in range(i + 1, len(moves)):
                x2, y2 = moves[j]
                game.board.grid[x2][y2] = c.AI # SET SECOND STONE
                game.last_row = x2
                game.last_col = y2
    
                # What's going to happen from now on?
                score = self.alpha_beta(game, game.depth, -math.inf, math.inf, False)
    
                if score >= best_score:
                    best_score = score
                    best_move = [(x1, y1), (x2, y2)]
    
                # Reset second stone
                game.board.grid[x2][y2] = c.EMPTY
                # Restore state to *after move 1*
                game.last_row = x1
                game.last_col = y1
            # Reset first stone
            game.board.grid[x1][y1] = c.EMPTY
            # 2. Restore the *original* state
            game.last_row = orig_r
            game.last_col = orig_c
    
        return best_move