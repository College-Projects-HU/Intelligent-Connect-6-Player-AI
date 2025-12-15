# Minimax with Beam Search - Refactored Pseudocode

## Helper Functions

### `_chebyshev_distance(p1, p2)`
Calculates the maximum coordinate difference between two points. Used to measure "closeness" on the board.
```python
return max(abs(x1-x2), abs(y1-y2))
```

### `_board_state_key(game)`
Generates a unique string representing the current board and player. Used as a key for caching.

### `simulate(game, moves, player)`
Creates a future game state.
1. Checks `_SIM_CACHE` for existing state.
2. If not found, creates a copy of `game`.
3. Applies the `moves`.
4. Saves to cache and returns the new game object.

### `probe_score(game)`
Returns the heuristic evaluation of a game state.
1. Checks `_PROBE_CACHE`.
2. If not found, runs `game.evaluate_position()`.
3. Saves to cache and returns the score.

### `_find_immediate_threats`
*Removed in refactoring.* Replaced by a direct simulation loop in the root of `minimax` that checks if any opponent move results in a win.

### `get_candidate_moves(game, radius)`
Generates valid moves to consider.
1. **Optimization**: If there are stones on the board, it only returns empty cells within `radius` (Chebyshev distance) of existing stones.
2. **Fallback**: If board is empty, returns all moves (e.g. center).

### `get_candidate_moves_near_last_human(game, radius)`
A more focused version of candidate generation.
1. **Focus**: strict filter to only return cells near the *last human move*.
2. **Purpose**: Used to narrow the search beam significantly, assuming response must be local.

---

## Main Algorithm: `minimax`

```python
function minimax(game, depth, is_maximizing_player):
    # 1. Candidate Selection
    #    - Try "focused" candidates (near last human move)
    #    - If none, fall back to general candidates (near any stone)

    # 2. Threat Detection (Root Level)
    #    - Loop through available moves
    #    - Simulate opponent placing a stone
    #    - If opponent wins immediately, this is a THREAT.
    #    - Return these blocking moves immediately (pruning the distinct branch).

    # 3. Recursive Search (Beam Search)
    function recurse(node_game, depth_left, maximizing):
        if draw: return 0
        if depth_left == 0: return probe_score(node_game)

        # Candidate Generation
        candidates = get_candidate_moves_near_last_human(node_game) OR get_candidate_moves(node_game)

        # Pair Generation (Unified)
        if count(candidates) >= 2:
            pairs = combinations(candidates, 2)
        else:
            pairs = (candidates[0] + any_other_move)

        # Scoring & Sorting (Beam)
        scored_pairs = []
        for pair in pairs:
            # Check immediate win
            child = simulate(node_game, pair)
            if child.is_win():
                return WIN_SCORE, pair
            
            # Heuristic score
            score = probe_score(child)
            scored_pairs.add((score, pair, child))
        
        sort scored_pairs

        # Iterate Top Pairs
        best = -INF
        for pair in scored_pairs[:MAX_BRANCH]:
             val = recurse(child, depth-1, !maximizing)
             best = max(best, val)
        
        return best
```
