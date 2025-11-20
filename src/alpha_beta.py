import src.game_logic as connect6
import src.constants as c
import src.heuristics as eval
import math
import time  # ✅ ADD: Import time

class AlphaBetaPruning:
    def __init__(self, game, heuristic, max_depth=c.ALPHA_BETA_DETPH):
        self.game = game
        self.max_depth = max_depth
        self.heuristic = heuristic
        self.limit = 20
        self.nodes_explored = 0
        self.nodes_pruned = 0
        self.start_time = None

    def __evaluate_board(self, game, win, draw):
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

    def check_threat_at_position(self, game, x, y, player, min_count=5):
        """
        Check if placing a stone at (x,y) creates a threat of min_count or more
        DEFAULT: min_count=5 (detects 5-in-a-row threats that need blocking)
        """
        original = game.board.grid[x][y]
        game.board.grid[x][y] = player
        
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        max_consecutive = 0
        
        for dx, dy in directions:
            count = 1
            # Count in positive direction
            i, j = x + dx, y + dy
            while (0 <= i < game.board.size and 0 <= j < game.board.size and 
                   game.board.grid[i][j] == player):
                count += 1
                i += dx
                j += dy
            # Count in negative direction
            i, j = x - dx, y - dy
            while (0 <= i < game.board.size and 0 <= j < game.board.size and 
                   game.board.grid[i][j] == player):
                count += 1
                i -= dx
                j -= dy
            
            max_consecutive = max(max_consecutive, count)
            
            if max_consecutive >= 6:  # Already winning
                game.board.grid[x][y] = original
                return max_consecutive
        
        game.board.grid[x][y] = original
        return max_consecutive

    def alpha_beta(self, game, depth, alpha, beta, maximizing_player):
        self.nodes_explored += 1
        
        if game.last_row is not None and game.last_col is not None:
            win = game.check_winner(game.last_row, game.last_col)
        else:
            win = False
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
        
        moves = self.get_prioritized_moves(game, self.limit)
        
        for i in range(len(moves)):
            x1, y1 = moves[i]
            self.set_stone(x1, y1, c.AI)
            
            for j in range(i + 1, len(moves)):
                x2, y2 = moves[j]
                self.set_stone(x2, y2, c.AI)
                
                score = self.alpha_beta(game, depth - 1, alpha, beta, False)

                self.remove_stone(x2, y2)
                game.last_row = x1
                game.last_col = y1

                max_score = max(max_score, score)
                alpha = max(alpha, score)
                
                if beta <= alpha:
                    self.nodes_pruned += 1
                    self.remove_stone(x1, y1)
                    game.last_row = orig_r
                    game.last_col = orig_c
                    return max_score

            self.remove_stone(x1, y1)

        game.last_row = orig_r
        game.last_col = orig_c
        return max_score
        
    def __min_node(self, game, depth, alpha, beta):
        min_score = math.inf
        orig_r, orig_c = game.last_row, game.last_col

        moves = self.get_prioritized_moves(game, self.limit)
        
        for i in range(len(moves)):
            x1, y1 = moves[i]
            self.set_stone(x1, y1, c.PLAYER)
            
            for j in range(i + 1, len(moves)):
                x2, y2 = moves[j]
                self.set_stone(x2, y2, c.PLAYER)
                
                score = self.alpha_beta(game, depth - 1, alpha, beta, True)
    
                self.remove_stone(x2, y2)
                game.last_row = x1
                game.last_col = y1
    
                min_score = min(min_score, score)
                beta = min(beta, score)
                
                if beta <= alpha:
                    self.nodes_pruned += 1
                    self.remove_stone(x1, y1)
                    game.last_row = orig_r
                    game.last_col = orig_c
                    return min_score
    
            self.remove_stone(x1, y1)
    
        game.last_row = orig_r
        game.last_col = orig_c
        return min_score
    
    def get_prioritized_moves(self, game, limit=None):
        """
        Priority: Win > Block > Strong threats > Building
        """
        all_moves = game.get_available_moves()
        
        if not all_moves:
            return []
        
        # Early game: center focus
        if len(all_moves) >= (game.board.size * game.board.size - 5):
            center = game.board.size // 2
            return [(x, y) for x, y in all_moves 
                    if abs(x - center) <= 4 and abs(y - center) <= 4][:limit]
        
        current_player = c.AI if game.current_player == c.AI else c.PLAYER
        opponent = c.PLAYER if current_player == c.AI else c.AI
        
        # Categorize moves
        winning_moves = []
        critical_blocks = []  # Block 5-in-a-row
        important_blocks = []  # Block 4-in-a-row
        strong_attacks = []   # Create 5-in-a-row
        good_attacks = []     # Create 4-in-a-row
        decent_moves = []
        
        # Get relevant area
        relevant = set()
        for x in range(game.board.size):
            for y in range(game.board.size):
                if game.board.grid[x][y] != c.EMPTY:
                    for dx in range(-3, 4):
                        for dy in range(-3, 4):
                            nx, ny = x + dx, y + dy
                            if (0 <= nx < game.board.size and 
                                0 <= ny < game.board.size and 
                                game.board.grid[nx][ny] == c.EMPTY):
                                relevant.add((nx, ny))
        
        moves_to_check = list(relevant) if relevant else all_moves
        
        for move in moves_to_check:
            x, y = move
            
            my_threat = self.check_threat_at_position(game, x, y, current_player)
            opp_threat = self.check_threat_at_position(game, x, y, opponent)
            
            # Winning move
            if my_threat >= 6:
                winning_moves.append(move)
            # CRITICAL: Block opponent's 5-in-a-row (they can win next turn!)
            elif opp_threat >= 5:
                critical_blocks.append((move, opp_threat))
            # Block opponent's 4-in-a-row
            elif opp_threat >= 4:
                important_blocks.append((move, opp_threat))
            # Create our 5-in-a-row
            elif my_threat >= 5:
                strong_attacks.append((move, my_threat))
            # Create our 4-in-a-row
            elif my_threat >= 4:
                good_attacks.append((move, my_threat))
            else:
                score = my_threat * 10 + opp_threat * 5
                decent_moves.append((move, score))
        
        # Sort by priority
        critical_blocks.sort(key=lambda x: x[1], reverse=True)
        important_blocks.sort(key=lambda x: x[1], reverse=True)
        strong_attacks.sort(key=lambda x: x[1], reverse=True)
        good_attacks.sort(key=lambda x: x[1], reverse=True)
        decent_moves.sort(key=lambda x: x[1], reverse=True)
        
        # Combine in priority order
        result = (
            winning_moves +
            [m for m, _ in critical_blocks] +
            [m for m, _ in important_blocks] +
            [m for m, _ in strong_attacks] +
            [m for m, _ in good_attacks] +
            [m for m, _ in decent_moves]
        )
        
        # Remove duplicates
        seen = set()
        unique = []
        for m in result:
            if m not in seen:
                seen.add(m)
                unique.append(m)
        
        return unique[:limit] if limit else unique
        
    def find_best_move(self, game):
        # Reset and start timing
        self.nodes_explored = 0
        self.nodes_pruned = 0
        self.start_time = time.time()
        
        if game.first_move:
            center = game.board.size // 2
            return [(center, center)]
        
        moves = self.get_prioritized_moves(game, self.limit)
        current_player = c.AI
        opponent = c.PLAYER
        
        # IMMEDIATE WIN CHECK
        for i in range(len(moves)):
            x1, y1 = moves[i]
            if self.check_threat_at_position(game, x1, y1, current_player) >= 6:
                return [(x1, y1), moves[0] if moves[0] != (x1, y1) else moves[1]]
            
            self.set_stone(x1, y1, current_player)
            for j in range(i + 1, len(moves)):
                x2, y2 = moves[j]
                if self.check_threat_at_position(game, x2, y2, current_player) >= 6:
                    self.remove_stone(x1, y1)
                    return [(x1, y1), (x2, y2)]
            self.remove_stone(x1, y1)
        
        # CRITICAL BLOCK CHECK - if opponent has 5-in-a-row threat, MUST block!
        critical_threats = []
        for move in moves[:15]:  # Check top moves
            x, y = move
            threat_level = self.check_threat_at_position(game, x, y, opponent)
            if threat_level >= 5:
                critical_threats.append((move, threat_level))
        
        # If opponent has critical threat, use both stones to block/counter
        if critical_threats:
            critical_threats.sort(key=lambda x: x[1], reverse=True)
            block1 = critical_threats[0][0]
            # Second stone: another block or attack
            if len(critical_threats) > 1:
                block2 = critical_threats[1][0]
            else:
                # Use second stone to create our own threat
                block2 = moves[1] if moves[1] != block1 else moves[2]
            return [block1, block2]
        
        # Normal alpha-beta search
        best_score = -math.inf
        best_moves = None
        alpha = -math.inf
        beta = math.inf
        
        for i in range(min(len(moves), 20)):
            x1, y1 = moves[i]
            self.set_stone(x1, y1, c.AI)
            
            for j in range(i + 1, min(len(moves), 20)):
                x2, y2 = moves[j]
                self.set_stone(x2, y2, c.AI)
                
                score = self.alpha_beta(game, self.max_depth - 1, alpha, beta, False)
                
                self.remove_stone(x2, y2)
                game.last_row = x1
                game.last_col = y1
                
                if score > best_score:
                    best_score = score
                    best_moves = [(x1, y1), (x2, y2)]
                
                alpha = max(alpha, score)
            
            self.remove_stone(x1, y1)
        
        # Print Console Details :)) (ya rb fok el dy2a)
        elapsed_time = time.time() - self.start_time
        
        print(f"==== Alpha Beta at depth {self.max_depth} ====")
        print(f"Nodes Explored: {self.nodes_explored:,}")
        print(f"Pruned {self.nodes_pruned:} times")
        print(f"Time Taken: {elapsed_time:.2f} seconds")
        print(f"Best Move Returned From AlphaBetaPurning Class: {best_moves}")
        print(f"Best Score: {best_score}")
        return best_moves if best_moves else [moves[0], moves[1]]

    def set_stone(self, x, y, stone):
        self.game.board.grid[x][y] = stone
        self.game.last_row = x
        self.game.last_col = y
        self.game._remove_move(x, y)
    
    def remove_stone(self, x, y):
        self.game.board.grid[x][y] = c.EMPTY
        self.game._add_move(x, y)