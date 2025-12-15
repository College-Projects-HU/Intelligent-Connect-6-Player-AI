# src/minimax.py
import time
from itertools import combinations
from src.constants import MAX_CANDIDATES

INF = 10**9
DEFAULT_RADIUS = 2
HUMAN_FOCUS_RADIUS = 3   # prefer searching near last human move when available

# Normalization/clamping thresholds used when ordering and at leaves.
# These keep heuristic magnitudes from overwhelming distance/ordering.
_ORDER_LIMIT = 500.0
_LEAF_LIMIT = 10000.0


def _chebyshev(a, b):
    (x1, y1), (x2, y2) = a, b
    return max(abs(x1 - x2), abs(y1 - y2))


def get_candidate_moves(game, radius=DEFAULT_RADIUS):
    """Return candidate empty cells for search.

    This implementation reuses `game.get_available_moves()` and the board
    rather than scanning the whole file independently.
    """
    grid = game.board.grid
    n = game.board.size

    # Build occupied cells set from the grid (small cost, still simpler than
    # reimplementing board bookkeeping here). Use available_moves for final
    # filtering so we never return invalid cells.
    occupied = {(i, j) for i in range(n) for j in range(n) if grid[i][j] != '.'}
    avail = set(game.get_available_moves())

    # If no occupied cells, return all available moves (first moves)
    if not occupied:
        return sorted(avail)

    candidates = set()
    for c in avail:
        # include empty cell if it's within chebyshev `radius` of any occupied cell
        for o in occupied:
            if _chebyshev(c, o) <= radius:
                candidates.add(c)
                break

    if not candidates:
        return sorted(avail)
    return sorted(candidates)


def get_candidate_moves_near_last_human(game, radius=HUMAN_FOCUS_RADIUS):
    """Prefer cells near the last human move.

    The game may supply different attributes for last human moves; prefer
    `last_human_moves` if present (set/list), otherwise fall back to
    `last_row`/`last_col`. Returns a set of coords.
    """
    grid = game.board.grid
    n = game.board.size
    avail = set(game.get_available_moves())

    origins = set()
    if hasattr(game, "last_human_moves") and game.last_human_moves:
        origins.update(game.last_human_moves)
    elif getattr(game, "last_row", None) is not None and getattr(game, "last_col", None) is not None:
        origins.add((game.last_row, game.last_col))

    if not origins:
        return set()

    candidates = set()
    for c in avail:
        for o in origins:
            if _chebyshev(c, o) <= radius:
                candidates.add(c)
                break

    return candidates

def board_state_key(game):
    grid = game.board.grid
    rows = [''.join(row) for row in grid]
    return '|'.join(rows) + f":{game.current_player}:{int(game.first_move)}"

def is_win_after_placement(sim_game, coord):
    x, y = coord
    return sim_game.check_winner(x, y)

# small caches to reduce repeated expensive ops
_SIM_CACHE = {}
_PROBE_CACHE = {}

def simulate(game, moves, player):
    """Use the game's `make_move_copy` (already provided in `game_logic`) and cache results."""
    bk = board_state_key(game)
    key = (bk, tuple(moves), player)
    if key in _SIM_CACHE:
        return _SIM_CACHE[key]
    child = game.make_move_copy(moves, player)
    _SIM_CACHE[key] = child
    return child

def probe_score_cached(game):
    bk = board_state_key(game)
    if bk in _PROBE_CACHE:
        return _PROBE_CACHE[bk]
    val = game.evaluate_position()
    _PROBE_CACHE[bk] = val
    return val


def _clamp_for_ordering(v: float) -> float:
    """Clamp probe scores used for ordering to [-_ORDER_LIMIT, _ORDER_LIMIT]."""
    try:
        if v != v:  # NaN guard
            return 0.0
        if v > _ORDER_LIMIT:
            return _ORDER_LIMIT
        if v < -_ORDER_LIMIT:
            return -_ORDER_LIMIT
        return float(v)
    except Exception:
        return 0.0


def _clamp_for_leaf(v: float) -> float:
    """Clamp leaf evaluation values to a bounded range but preserve infinities."""
    try:
        if abs(v) >= INF:
            return v
        if v > _LEAF_LIMIT:
            return _LEAF_LIMIT
        if v < -_LEAF_LIMIT:
            return -_LEAF_LIMIT
        return float(v)
    except Exception:
        return 0.0

def minimax(game, depth, maximizing_player, radius=DEFAULT_RADIUS,
            max_candidates=MAX_CANDIDATES, max_second_per_first=6, verbose=True):
    """
    Minimal minimax:
      - depth: recursion depth (0 == evaluate_position)
      - maximizing_player: True if root is maximizing (AI)
      - verbose: prints stats to console (time, depth, node count)
    Behavior change: if game.last_human_moves exists, restrict candidates to Chebyshev distance
    HUMAN_FOCUS_RADIUS from the last human stone(s). If that produces no candidates, fall back.
    """
    t0 = time.time()
    required = 2
    root_player = game.current_player

    avail = list(game.get_available_moves())
    if len(avail) <= required:
        elapsed = time.time() - t0
        stats = {"time": elapsed, "depth": depth, "nodes": 0}
        setattr(game, "_last_minimax_stats", stats)
        if verbose:
            print(f"[minimax] depth={depth} nodes={0} time={elapsed:.4f}s (console)")
        return 0, avail[:required]

    # First, try to constrain candidates to near last human moves (distance HUMAN_FOCUS_RADIUS)
    focused_candidates = get_candidate_moves_near_last_human(game, HUMAN_FOCUS_RADIUS)

    # ROOT: scan the board for any opponent open-5 (or open-4) sequences that
    # already exist and would allow an immediate win next turn. If found,
    # compute blocking cells and prioritize them. This detects "you already
    # have 5 in a row" cases where we must block immediately.


    # ROOT: Detect immediate opponent threats by simulation (simpler than scanning runs)
    opponent = 'O' if root_player == 'X' else 'X'
    immediate_blockers = set()
    
    # Check if opponent can win in 1 move (requires immediate block)
    # We only check this on available moves to be safe and simple.
    for m in avail:
        try:
            # Simulate opponent move
            sim = simulate(game, [m], opponent)
            if is_win_after_placement(sim, m):
                immediate_blockers.add(m)
        except Exception:
            pass
            
    if immediate_blockers:
        if verbose:
            print(f"[minimax] Found immediate threats (blocking required): {sorted(immediate_blockers)}")
        # If immediate threats exist, we MUST play them. 
        # Since we play 2 stones, we can block up to 2 distinct threats.
        chosen_blockers = sorted(immediate_blockers)[:required]
        # Return immediately if we found forced blocks
        elapsed = time.time() - t0
        setattr(game, "_last_minimax_stats", {"time": elapsed, "depth": depth, "nodes": 0})
        if verbose:
             print(f"[minimax] Returning blockers: {chosen_blockers}")
        return 0, chosen_blockers
    if focused_candidates:
        # keep order deterministic and only consider those actually available
        candidates = [c for c in sorted(focused_candidates) if c in avail]
    else:
        # fallback to general candidate selection
        candidates = get_candidate_moves(game, radius)
        candidates = [c for c in candidates if c in avail]

    if not candidates:
        candidates = avail

    # Bias candidate ordering toward proximity to the last human move(s)
    origins = set()
    if hasattr(game, "last_human_moves") and game.last_human_moves:
        origins.update(game.last_human_moves)
    elif getattr(game, "last_row", None) is not None and getattr(game, "last_col", None) is not None:
        origins.add((game.last_row, game.last_col))

    def _dist_to_orig(c):
        if not origins:
            return float('inf')
        return min(_chebyshev(c, o) for o in origins)

    # Pre-score candidates by a combination of proximity and cached probe score.
    # Prefer smaller distance and higher probe score. Clamp probe scores so
    # extremely large evaluations don't completely dominate ordering.
    scored = []
    for c in candidates:
        d = _dist_to_orig(c)
        # Use cached probe score on the single-move child as an approximation
        try:
            child = simulate(game, [c], root_player)
            ps = probe_score_cached(child)
        except Exception:
            ps = 0
        ps_order = _clamp_for_ordering(ps)
        scored.append((d, -ps_order, ps, c))
    scored.sort()
    candidates = [t[3] for t in scored]
    if max_candidates and len(candidates) > max_candidates:
        candidates = candidates[:max_candidates]
    opponent = 'O' if root_player == 'X' else 'X'
    req_opp = 2

    blocking_moves = set()

    # Check single-move opponent wins across all available moves (cheap)
    try:
        for b in avail:
            child_b = simulate(game, [b], opponent)
            if is_win_after_placement(child_b, b):
                blocking_moves.add(b)
    except Exception:
        pass

    # If opponent requires 2 moves, check candidate pairs for immediate wins
    if req_opp == 2 and not blocking_moves:
        try:
            # limit pair checking to the (pre-scored) candidates to reduce cost
            from itertools import combinations as _comb
            for a, b in _comb([c for c in candidates], 2):
                child_ab = simulate(game, [a, b], opponent)
                if is_win_after_placement(child_ab, a) or is_win_after_placement(child_ab, b):
                    blocking_moves.add(a)
                    blocking_moves.add(b)
        except Exception:
            pass

    # More thorough two-move opponent win detection (targeted):
    # For each possible first opponent move `a`, simulate it and then check
    # second moves `b` among nearby available cells (using chebyshev
    # locality) to detect a forced two-move win. This reduces the
    # full O(n^2) pair scan while catching many practical threats.
    if req_opp == 2 and not blocking_moves:
        try:
            for a in avail:
                # simulate opponent placing `a`
                child_a = simulate(game, [a], opponent)
                # quickly skip if placing `a` already loses (shouldn't)
                if is_win_after_placement(child_a, a):
                    blocking_moves.add(a)
                    continue

                # Consider b's that are within HUMAN_FOCUS_RADIUS of `a` or
                # within HUMAN_FOCUS_RADIUS of any last human move (if present).
                local_avail2 = list(child_a.get_available_moves())
                origins2 = set()
                if hasattr(game, "last_human_moves") and game.last_human_moves:
                    origins2.update(game.last_human_moves)
                elif getattr(game, "last_row", None) is not None and getattr(game, "last_col", None) is not None:
                    origins2.add((game.last_row, game.last_col))

                # build candidate b-list: nearby to `a` or to known origins
                b_candidates = []
                for b in local_avail2:
                    if _chebyshev(b, a) <= HUMAN_FOCUS_RADIUS:
                        b_candidates.append(b)
                        continue
                    for o in origins2:
                        if _chebyshev(b, o) <= HUMAN_FOCUS_RADIUS:
                            b_candidates.append(b)
                            break

                # check second moves
                for b in b_candidates:
                    child_ab = simulate(child_a, [b], opponent)
                    if is_win_after_placement(child_ab, b) or is_win_after_placement(child_ab, a):
                        blocking_moves.add(a)
                        blocking_moves.add(b)
                        break
                if blocking_moves:
                    break
        except Exception:
            pass

        # If we still found nothing, and the board is not too large, fall back
        # to a full pair scan among all available moves (more expensive but
        # catches threats our locality heuristic missed). Limit to moderate
        # boards to avoid pathological slowdowns.
        if req_opp == 2 and not blocking_moves and len(avail) <= 120:
            try:
                for a in avail:
                    for b in avail:
                        if b == a:
                            continue
                        child_ab = simulate(game, [a, b], opponent)
                        if is_win_after_placement(child_ab, a) or is_win_after_placement(child_ab, b):
                            blocking_moves.add(a)
                            blocking_moves.add(b)
                            break
                    if blocking_moves:
                        break
            except Exception:
                pass

    if blocking_moves and verbose:
        print(f"[minimax] Detected opponent immediate/two-move threat. Blocking moves: {sorted(blocking_moves)}")

    if blocking_moves:
        # If we detected explicit blocking moves (single or two-move threats),
        # return them immediately as the AI's chosen move(s) so the AI will
        # block reliably rather than depending on ordering/probing.
        chosen_blockers = sorted(blocking_moves)[:required]
        if chosen_blockers:
            if verbose:
                print(f"[minimax] Returning detected blocking moves as best moves: {chosen_blockers}")
            elapsed = time.time() - t0
            setattr(game, "_last_minimax_stats", {"time": elapsed, "depth": depth, "nodes": 0})
            return 0, chosen_blockers

        # Reorder candidates so blocking moves come first (dedup while preserving order)
        new_candidates = []
        for m in candidates:
            if m in blocking_moves and m not in new_candidates:
                new_candidates.append(m)
        for m in candidates:
            if m not in new_candidates:
                new_candidates.append(m)
        candidates = new_candidates

    # Step 3: Check for immediate AI win (1 move)
    for a in candidates:
        child = simulate(game, [a], root_player)
        if is_win_after_placement(child, a):
             # Found a winning move. Return it (pair it with any other move)
            elapsed = time.time() - t0
            setattr(game, "_last_minimax_stats", {"time": elapsed, "depth": depth, "nodes": 1})
            if verbose:
                print(f"[minimax] Found immediate win: {a}")
            
            # Find a second valid move to complete the pair
            second = None
            for b in candidates:
                if b != a: second = b; break
            if not second:
                for b in avail:
                     if b != a: second = b; break
            
            return INF, [a, second] if second else [a]

    node_count = 0

    def recurse(node_game, depth_left, maximizing):
        nonlocal node_count
        node_count += 1

        if node_game.is_draw():
            return 0, None
        if depth_left == 0:
            v = probe_score_cached(node_game)
            # Preserve exact infinities (winning positions) but clamp ordinary evals
            return _clamp_for_leaf(v), None

        req = 2
        local_avail = list(node_game.get_available_moves())

        # same focused behavior recursively: prefer to keep search local to last human moves
        focused = get_candidate_moves_near_last_human(node_game, HUMAN_FOCUS_RADIUS)
        if focused:
            local_cand = [c for c in sorted(focused) if c in local_avail]
        else:
            local_cand = get_candidate_moves(node_game, radius)
            local_cand = [c for c in local_cand if c in local_avail]

        if not local_cand:
            local_cand = local_avail
        if max_candidates and len(local_cand) > max_candidates:
            local_cand = local_cand[:max_candidates]

        if not local_cand:
            return probe_score_cached(node_game), None

        best_score = -INF if maximizing else INF
        best_moves = None

        # Pair generation and scoring (Simpler, unified approach)
        pair_candidates = []
        if len(local_cand) >= 2:
            pair_candidates = list(combinations(local_cand, 2))
        else:
            # Handle edge case where we have < 2 candidates but need 2 moves
            if local_cand:
                a = local_cand[0]
                for b in local_avail:
                    if b != a:
                        pair_candidates.append((a, b))
        
        # Score pairs for sorting (Beam search preparation)
        scored_pairs = []
        for a, b in pair_candidates:
            # Check for immediate wins first (optimization)
            child_ab = simulate(node_game, [a, b], node_game.current_player)
            if is_win_after_placement(child_ab, b) or is_win_after_placement(child_ab, a):
                return (INF if maximizing else -INF), [a, b]
            
            ps = probe_score_cached(child_ab)
            scored_pairs.append((_clamp_for_ordering(ps), (a, b), child_ab))
        
        scored_pairs.sort(reverse=maximizing, key=lambda t: t[0])

        max_pairs = max_second_per_first * max(1, len(local_cand))
        for i, (_, (a, b), child_ab) in enumerate(scored_pairs):
            if i >= max_pairs:
                break
            sc, _ = recurse(child_ab, depth_left - 1, not maximizing)
            if maximizing:
                if sc > best_score:
                    best_score = sc
                    best_moves = [a, b]
            else:
                if sc < best_score:
                    best_score = sc
                    best_moves = [a, b]

        return best_score, best_moves

    best_score, best_moves = recurse(game, depth, maximizing_player)

    elapsed = time.time() - t0
    stats = {"time": elapsed, "depth": depth, "nodes": node_count}
    setattr(game, "_last_minimax_stats", stats)

    # PRINT STATS TO CONSOLE (explicit)
    if verbose:
        # console-only line (no GUI dialogs)
        print(f"[minimax] depth={depth} nodes={node_count} time={elapsed:.4f}s (console)")

    req_now = 2
    avail_now = list(game.get_available_moves())
    if not best_moves or len(best_moves) != req_now or any(m not in avail_now for m in best_moves):
        chosen = []
        for c in avail_now:
            if c not in chosen:
                chosen.append(c)
            if len(chosen) == req_now:
                break
        return best_score, chosen

    return best_score, best_moves
