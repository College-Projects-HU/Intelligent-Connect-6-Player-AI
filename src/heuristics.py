# src/heuristics.py

"""
Heuristic functions for evaluating Connect 6 game positions.

These functions analyze the board and return a score representing
the position's value from the AI's perspective.
"""

def heuristic_1(game_state):
    """
    First heuristic: Count sequences of stones in a row.
    
    This heuristic evaluates the board by:
    - Counting sequences of AI stones (2, 3, 4, 5 in a row) with positive weights
    - Counting sequences of human stones with negative weights
    - Giving higher weights to longer sequences
    
    Args:
        game_state: A Connect6Game instance
        
    Returns:
        A numerical score (positive = good for AI, negative = good for human)
    """
    score = 0
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # horizontal, vertical, diagonal, anti-diagonal
    size = game_state.board.size
    
    # Weights for different sequence lengths
    weights = {2: 1, 3: 10, 4: 100, 5: 1000}
    
    # Check all positions on the board
    for i in range(size):
        for j in range(size):
            if game_state.board.grid[i][j] == '.':
                continue
            
            player = game_state.board.grid[i][j]
            is_ai = (player == game_state.ai_player)
            
            # Check each direction
            for dx, dy in directions:
                count = 1
                # Count in positive direction
                x, y = i + dx, j + dy
                while 0 <= x < size and 0 <= y < size and game_state.board.grid[x][y] == player:
                    count += 1
                    x += dx
                    y += dy
                
                # Count in negative direction
                x, y = i - dx, j - dy
                while 0 <= x < size and 0 <= y < size and game_state.board.grid[x][y] == player:
                    count += 1
                    x -= dx
                    y -= dy
                
                # Only count sequences of 2-5 (6+ means game is over)
                if 2 <= count <= 5:
                    weight = weights.get(count, 0)
                    if is_ai:
                        score += weight
                    else:
                        score -= weight
    
    return score


def heuristic_2(game_state):
    """
    Second heuristic: Advanced evaluation with threats and center control.
    
    This heuristic evaluates the board by:
    - Counting sequences of stones (like heuristic_1)
    - Detecting threats (5 in a row that can be completed)
    - Considering center control (positions closer to center are more valuable)
    - Blocking opponent's threats
    
    Args:
        game_state: A Connect6Game instance
        
    Returns:
        A numerical score (positive = good for AI, negative = good for human)
    """
    score = 0
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    size = game_state.board.size
    center = size // 2
    
    # Weights for different sequence lengths
    weights = {2: 1, 3: 10, 4: 100, 5: 1000}
    threat_weight = 5000  # Very high weight for threats
    
    # Check all positions on the board
    for i in range(size):
        for j in range(size):
            if game_state.board.grid[i][j] == '.':
                continue
            
            player = game_state.board.grid[i][j]
            is_ai = (player == game_state.ai_player)
            
            # Center control bonus (positions closer to center are better)
            distance_from_center = abs(i - center) + abs(j - center)
            center_bonus = (size - distance_from_center) * 0.1
            if is_ai:
                score += center_bonus
            else:
                score -= center_bonus
            
            # Check each direction
            for dx, dy in directions:
                count = 1
                # Count in positive direction
                x, y = i + dx, j + dy
                while 0 <= x < size and 0 <= y < size and game_state.board.grid[x][y] == player:
                    count += 1
                    x += dx
                    y += dy
                
                # Count in negative direction
                x, y = i - dx, j - dy
                while 0 <= x < size and 0 <= y < size and game_state.board.grid[x][y] == player:
                    count += 1
                    x -= dx
                    y -= dy
                
                # Count sequences
                if 2 <= count <= 5:
                    weight = weights.get(count, 0)
                    if is_ai:
                        score += weight
                    else:
                        score -= weight
                
                # Check for threats (5 in a row with an open end)
                if count == 5:
                    # Check if there's an open space at either end
                    end1_x, end1_y = i + dx * count, j + dy * count
                    end2_x, end2_y = i - dx * count, j - dy * count
                    
                    threat_detected = False
                    if (0 <= end1_x < size and 0 <= end1_y < size and 
                        game_state.board.grid[end1_x][end1_y] == '.'):
                        threat_detected = True
                    if (0 <= end2_x < size and 0 <= end2_y < size and 
                        game_state.board.grid[end2_x][end2_y] == '.'):
                        threat_detected = True
                    
                    if threat_detected:
                        if is_ai:
                            score += threat_weight
                        else:
                            score -= threat_weight
    
    return score

