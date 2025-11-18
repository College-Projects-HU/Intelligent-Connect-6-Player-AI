import src.game_logic as connect6
import src.constants as c
import src.heuristics as eval
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
        # print(game.last_row)
        if win:
            winner = game.board.grid[game.last_row][game.last_col]
            return math.inf if winner == c.AI else -math.inf
        elif draw:
            return 0
        else:
            if self.heuristic == c.EVAL1:
                return eval.heuristic_1(game)
            else:
                return eval.heuristic_2(game)

    def alpha_beta(self, game, depth, alpha, beta, maximizing_player):
        win = game.check_winner(game.last_row, game.last_col)
        draw = game.is_draw()
        
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
        
        moves = self.get_prioritized_moves(game, limit= 15)
        
        for i in range(len(moves)):
            x1, y1 = moves[i]
            self.set_stone(x1, y1, c.AI)
            
            for j in range(i + 1, len(moves)):
                x2, y2 = moves[j]
                self.set_stone(x2, y2, c.AI)
                
                # What's going to happen from now on? (this comment for me to remind myself cus I get lost very often)
                score = self.alpha_beta(game, depth - 1, alpha, beta, False)

                # clear 2nd stone
                self.remove_stone(x2, y2)
                
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
            self.remove_stone(x1, y1)
            
            if outer_break: break

        game.last_row = orig_r
        game.last_col = orig_c
        
        return max_score
        
    def __min_node(self, game, depth, alpha, beta):
        min_score = math.inf
        orig_r, orig_c = game.last_row, game.last_col
        outer_break = False  # pruning ya 4bab

        moves = self.get_prioritized_moves(game, limit= 15)
        
        for i in range(len(moves)):
            x1, y1 = moves[i]
            self.set_stone(x1, y1, c.PLAYER)
            
            for j in range(i + 1, len(moves)):
                x2, y2 = moves[j]
                self.set_stone(x2, y2, c.PLAYER)
                
                # What's going to happen from now on?
                score = self.alpha_beta(game, depth - 1, alpha, beta, True)  # True for maximizing next
    
                # clear 2nd stone
                self.remove_stone(x2, y2)
                
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
            self.remove_stone(x1, y1)
            if outer_break: break
    
        game.last_row = orig_r
        game.last_col = orig_c
        return min_score  # Return min_score instead of max_score
    
    def get_prioritized_moves(self, game, limit=None):
        """
        Get moves prioritized by proximity to existing stones.
        This DRASTICALLY reduces the branching factor.
        """
        all_moves = game.get_available_moves()  # ✅ FIXED
        
        # If board is empty or nearly empty, return center area moves
        if len(all_moves) >= (game.board.size * game.board.size - 5):
            center = game.board.size // 2
            center_moves = [
                (x, y) for x, y in all_moves 
                if abs(x - center) <= 3 and abs(y - center) <= 3
            ]
            return center_moves[:limit] if limit else center_moves
        
        # Otherwise, only consider moves near existing stones (within 2 cells)
        relevant_moves = set()
        for x in range(game.board.size):
            for y in range(game.board.size):
                if game.board.grid[x][y] != c.EMPTY:
                    # Add all empty cells within radius 2
                    for dx in range(-2, 3):
                        for dy in range(-2, 3):
                            nx, ny = x + dx, y + dy
                            if (0 <= nx < game.board.size and 
                                0 <= ny < game.board.size and 
                                game.board.grid[nx][ny] == c.EMPTY):
                                relevant_moves.add((nx, ny))
        
        result = list(relevant_moves)
        # Further limit if needed
        if limit and len(result) > limit:
            # Prioritize center moves
            center = game.board.size // 2
            result.sort(key=lambda m: abs(m[0] - center) + abs(m[1] - center))
            result = result[:limit]
        
        return result if result else all_moves[:limit] if limit else all_moves
        
    def find_best_move(self, game):
        """
        Find the best move(s) for the current player.
        Returns a list of move tuples: [(x1, y1)] for first move, [(x1, y1), (x2, y2)] otherwise.
        """
        best_score = -math.inf
        best_moves = None
        
        # Use prioritized moves to reduce search space
        moves = self.get_prioritized_moves(game, limit=15)  # Limit to top 15 moves
        
        if game.first_move:
            # First move: only place one stone in the center area
            center = game.board.size // 2
            best_moves = [(center, center)]
            return best_moves
        
        # Regular move: place two stones
        alpha = -math.inf
        beta = math.inf
        
        for i in range(len(moves)):
            x1, y1 = moves[i]
            self.set_stone(x1, y1, c.AI)
            
            for j in range(i + 1, len(moves)):
                x2, y2 = moves[j]
                self.set_stone(x2, y2, c.AI)
                
                # Evaluate this move combination
                score = self.alpha_beta(game, self.max_depth - 1, alpha, beta, False)
                
                # Restore board state
                self.remove_stone(x2, y2)
                game.last_row = x1
                game.last_col = y1
                
                # Update best move
                if score > best_score:
                    best_score = score
                    best_moves = [(x1, y1), (x2, y2)]
                
                alpha = max(alpha, score)
            
            # Remove first stone
            self.remove_stone(x1, y1)
        
        return best_moves if best_moves else [moves[0], moves[1]] if len(moves) >= 2 else []


    def set_stone(self, x, y, stone):
        self.game.board.grid[x][y] = stone
        self.game.last_row = x
        self.game.last_col = y
        self.game._remove_move(x, y)
    
    def remove_stone(self, x, y):
        self.game.board.grid[x][y] = c.EMPTY
        self.game._add_move(x, y)