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

### `_find_immediate_threats(game, opponent, length)`
Scans the board for `length` consecutive opponent stones (e.g., 4 or 5) that have open ends.
Returns a set of blocking moves if found.

### `get_ordered_candidates(game, radius, max_count)`
Generates and sorts the most promising moves.
1. **Focus**: Looks for empty cells near recent moves (Chebyshev distance).
2. **Fallback**: If no recent moves, looks near *any* stone.
3. **Scoring**: Ranks candidates by heuristic score (simulating each single move).
4. **Beam**: Returns only the top `max_count` candidates.

---

## Main Algorithm: `minimax`

```python
function minimax(game, depth, is_maximizing_player):
    # 1. Threat Detection (Root Level Only)
    # Check for immediate 5-in-a-row or 4-in-a-row threats
    blockers = _find_immediate_threats(game, opponent)
    if blockers found:
        return 0, [blockers] # Return immediately, do not search

    # 2. Main Recursion
    function recurse(node_game, depth_left, maximizing):
        # Base Cases
        if game is draw: return 0
        if depth_left == 0: return probe_score(node_game)

        # Candidate Generation
        candidates = get_ordered_candidates(node_game)

        # Pair Generation (Assuming 2 stones per turn)
        pairs = combinations(candidates, 2)
        
        # Sort Pairs (Beam Search Prep)
        # Simulate each pair to get a rough score
        scored_pairs = []
        for pair in pairs:
            child = simulate(node_game, pair)
            score = probe_score(child)
            scored_pairs.add(score, pair, child)
        
        sort scored_pairs (descending if maximizing, ascending if minimizing)

        # Search Loop (Beam Width Limited)
        best_score = -INF / +INF
        
        for pair in scored_pairs[:MINIMAX_MAX_BRANCH]:
            # Recursive Call
            score = recurse(child, depth_left - 1, not maximizing)
            
            # Update Best
            if maximizing and score > best_score:
                best_score = score
                best_moves = pair
            elif minimizing and score < best_score:
                best_score = score
                best_moves = pair
                
        return best_score, best_moves

    return recurse(game, depth, maximizing_player)
```
