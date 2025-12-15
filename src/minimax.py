# src/minimax.py
import time
from itertools import combinations
from typing import List, Tuple, Set, Optional
from src.constants import MINIMAX_MAX_BRANCH

# Constants
INF = 10**9
DEFAULT_RADIUS = 2
HUMAN_FOCUS_RADIUS = 3

# Caches
_SIM_CACHE = {}
_PROBE_CACHE = {}

def clear_caches():
    """Clear simulation and probe caches."""
    _SIM_CACHE.clear()
    _PROBE_CACHE.clear()

def _chebyshev_distance(p1: Tuple[int, int], p2: Tuple[int, int]) -> int:
    """Calculate Chebyshev distance between two points."""
    return max(abs(p1[0] - p2[0]), abs(p1[1] - p2[1]))

def _board_state_key(game) -> str:
    """Generate a unique key for the current board state."""
    grid = game.board.grid
    return '|'.join([''.join(row) for row in grid]) + f":{game.current_player}"

def simulate(game, moves: List[Tuple[int, int]], player: str):
    """
    Simulate moves on a copy of the game. Uses caching to avoid redundant copies.
    """
    bk = _board_state_key(game)
    key = (bk, tuple(moves), player)
    
    if key in _SIM_CACHE:
        return _SIM_CACHE[key]
    
    child = game.make_move_copy(moves, player)
    _SIM_CACHE[key] = child
    return child

def probe_score(game) -> float:
    """
    Calculate or retrieve the heuristic score for the current game state.
    """
    bk = _board_state_key(game)
    if bk in _PROBE_CACHE:
        return _PROBE_CACHE[bk]
    
    score = game.evaluate_position()
    _PROBE_CACHE[bk] = score
    return score

def _find_immediate_threats(game, opponent: str, length: int) -> Set[Tuple[int, int]]:
    """
    Scan the board for immediate threats (open runs of 'length') for the opponent.
    Returns a set of blocking moves.
    """
    board = game.board.grid
    n = game.board.size
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    blockers = set()

    for i in range(n):
        for j in range(n):
            if board[i][j] != opponent:
                continue
            
            for dx, dy in directions:
                # Count chain length in this direction
                count = 1
                
                # Check forward
                x, y = i + dx, j + dy
                while 0 <= x < n and 0 <= y < n and board[x][y] == opponent:
                    count += 1
                    x += dx; y += dy
                end1 = (x, y)
                
                # Check backward
                x, y = i - dx, j - dy
                while 0 <= x < n and 0 <= y < n and board[x][y] == opponent:
                    count += 1
                    x -= dx; y -= dy
                end2 = (x, y)

                if count == length:
                    # If we found a run of the specified length, check ends for blockers
                    ex, ey = end1
                    if 0 <= ex < n and 0 <= ey < n and board[ex][ey] == '.':
                        blockers.add((ex, ey))
                    
                    ex, ey = end2
                    if 0 <= ex < n and 0 <= ey < n and board[ex][ey] == '.':
                        blockers.add((ex, ey))
                        
    return blockers

def _get_relevant_origins(game) -> Set[Tuple[int, int]]:
    """Get relevant points of interest (last human moves) to focus search around."""
    origins = set()
    if hasattr(game, "last_human_moves") and game.last_human_moves:
        origins.update(game.last_human_moves)
    elif getattr(game, "last_row", None) is not None and getattr(game, "last_col", None) is not None:
        origins.add((game.last_row, game.last_col))
    return origins

def get_ordered_candidates(game, radius=DEFAULT_RADIUS, max_count=12) -> List[Tuple[int, int]]:
    """
    Get a list of candidate moves, prioritized by proximity to recent moves
    and heuristic score.
    """
    avail = list(game.get_available_moves())
    if not avail:
        return []

    origins = _get_relevant_origins(game)
    candidates = set()

    # If we have focus points (human moves), look closely around them
    if origins:
        for c in avail:
            for o in origins:
                if _chebyshev_distance(c, o) <= HUMAN_FOCUS_RADIUS:
                    candidates.add(c)
                    break
    
    # If no focused candidates found (or no origins), fall back to general radius
    if not candidates:
        occupied = {(i, j) for i in range(game.board.size) 
                   for j in range(game.board.size) 
                   if game.board.grid[i][j] != '.'}
        
        if not occupied:
            # Empty board or start of game
            return avail[:max_count]
            
        for c in avail:
            for o in occupied:
                if _chebyshev_distance(c, o) <= radius:
                    candidates.add(c)
                    break

    final_candidates = list(candidates if candidates else avail)

    # Simple heuristic ordering: prioritize moves with higher immediate probe score
    # This helps alpha-beta (if used) or just general search quality
    scored = []
    root_player = game.current_player
    
    for c in final_candidates:
        # Distance score: closer to origins is better (lower dist)
        dist = min([_chebyshev_distance(c, o) for o in origins]) if origins else 0
        
        # Probe score
        try:
            # We must simulate to get a score
            child = simulate(game, [c], root_player)
            ps = probe_score(child)
        except Exception:
            ps = 0
            
        scored.append((dist, -ps, c)) # Minimize dist, maximize (negative minimize) score
        
    scored.sort()
    
    # Return top candidates
    return [x[2] for x in scored[:max_count]]


def minimax(game, depth: int, maximizing_player: bool, 
            radius=DEFAULT_RADIUS, max_candidates=15, verbose=True) -> Tuple[float, List[Tuple[int, int]]]:
    """
    Minimax algorithm with heuristic optimizations.
    Assumes AI always plays 2 stones 
    """
    t0 = time.time()
    
    # Clear caches at the start of a root search
    # (Optional: keep them if we want persistence across turns, but safer to clear)
    # _SIM_CACHE.clear() # Keeping persistent for now as per original design implication
    
    required_moves = 2 # Forced assumption as per user request
    avail = list(game.get_available_moves())
    
    # Basic validation
    if len(avail) < required_moves:
         return 0, avail # Take whatever is left

    # --- Root Level Threat Detection ---
    # Check if we need to block immediately
    opponent = 'O' if game.current_player == 'X' else 'X'
    
    # Check for open-5 (urgent!)
    blockers = _find_immediate_threats(game, opponent, 5)
    if not blockers:
        # Check for open-4 (urgent)
        blockers = _find_immediate_threats(game, opponent, 4)
        
    if blockers:
        # Filter blockers to ensure they are valid moves
        valid_blockers = [b for b in blockers if b in avail]
        if valid_blockers:
            # If we found imperative blocks, just return them to save time
            chosen = sorted(valid_blockers)[:required_moves]
            
            # If we only have 1 blocker but need 2 moves, fill with best other candidate
            if len(chosen) < required_moves:
                remaining = [m for m in avail if m not in chosen]
                if remaining:
                    # Pick a move near the block if possible
                    best_rem = min(remaining, key=lambda m: _chebyshev_distance(m, chosen[0]))
                    chosen.append(best_rem)
            
            if verbose:
                print(f"[minimax] Immediate threat detected! Blocking with: {chosen}")
            return 0, chosen

    # --- Main Search ---
    node_count = 0

    def recurse(node_game, depth_left, maximizing) -> Tuple[float, List[Tuple[int, int]]]:
        nonlocal node_count
        node_count += 1
        
        # Base cases
        if node_game.is_draw():
            return 0, []
        
        if depth_left == 0:
            return probe_score(node_game), []

        # Generate candidates
        candidates = get_ordered_candidates(node_game, radius, max_candidates)
        if not candidates:
             return probe_score(node_game), []

        # We need to pick PAIRS of moves
        # Generate pairs from the top candidates
        # If we have few candidates, this combination count is small.
        # If candidates=12, 12C2 = 66 pairs. Manageable.
        
        pairs = list(combinations(candidates, 2))
        if not pairs and len(avail) >= 2:
             # Fallback if candidates < 2 (unlikely unless end of game)
             pairs = list(combinations(avail[:5], 2)) 

        best_score = -INF if maximizing else INF
        best_moves = []

        # Sort pairs by a quick heuristic probe to improve alpha-beta pruning efficiency 
        # (even though this is minimax, sorting helps likely-best-first)
        scored_pairs = []
        for p in pairs:
            # Quick probe: simulate the pair
            child = simulate(node_game, list(p), node_game.current_player)
            val = probe_score(child)
            scored_pairs.append((val, p, child))
            
        # Sort: Descending for Max, Ascending for Min
        scored_pairs.sort(key=lambda x: x[0], reverse=maximizing)

        # Explore
        # Limit branching factor for pairs to avoid exponential explosion
        # We only look at the top N pairs
        max_branch = MINIMAX_MAX_BRANCH
        
        for i, (val, moves, child) in enumerate(scored_pairs):
            if i >= max_branch:
                break
                
            score, _ = recurse(child, depth_left - 1, not maximizing)
            
            if maximizing:
                if score > best_score:
                    best_score = score
                    best_moves = list(moves)
            else:
                if score < best_score:
                    best_score = score
                    best_moves = list(moves)
        
        return best_score, best_moves

    # Start recursion
    final_score, final_moves = recurse(game, depth, maximizing_player)
    
    elapsed = time.time() - t0
    if verbose:
        print(f"[minimax] depth={depth} nodes={node_count} time={elapsed:.4f}s")
        
    return final_score, final_moves
