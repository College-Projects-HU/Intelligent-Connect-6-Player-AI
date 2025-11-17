# src/minimax.py
import time
from itertools import combinations

INF = 10**9
DEFAULT_RADIUS = 2
HUMAN_FOCUS_RADIUS = 3   # prefer searching near last human move when available


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

def minimax(game, depth, maximizing_player, radius=DEFAULT_RADIUS,
            max_candidates=12, max_second_per_first=6, verbose=True):
    """
    Minimal minimax:
      - depth: recursion depth (0 == evaluate_position)
      - maximizing_player: True if root is maximizing (AI)
      - verbose: prints stats to console (time, depth, node count)
    Behavior change: if game.last_human_moves exists, restrict candidates to Chebyshev distance
    HUMAN_FOCUS_RADIUS from the last human stone(s). If that produces no candidates, fall back.
    """
    t0 = time.time()
    required = 1 if game.first_move else 2
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
    # Prefer smaller distance and higher probe score.
    scored = []
    for c in candidates:
        d = _dist_to_orig(c)
        # Use cached probe score on the single-move child as an approximation
        try:
            child = simulate(game, [c], root_player)
            ps = probe_score_cached(child)
        except Exception:
            ps = 0
        scored.append((d, -ps, c))
    scored.sort()
    candidates = [t[2] for t in scored]
    if max_candidates and len(candidates) > max_candidates:
        candidates = candidates[:max_candidates]

    # immediate root win check
    for a in candidates:
        child = simulate(game, [a], root_player)
        if is_win_after_placement(child, a):
            elapsed = time.time() - t0
            stats = {"time": elapsed, "depth": depth, "nodes": 1}
            setattr(game, "_last_minimax_stats", stats)
            if verbose:
                print(f"[minimax] depth={depth} nodes={1} time={elapsed:.4f}s (console)")
            if required == 1:
                return INF, [a]
            for b in candidates:
                if b != a:
                    return INF, [a, b]
            for b in avail:
                if b != a:
                    return INF, [a, b]
            return INF, [a]

    node_count = 0

    def recurse(node_game, depth_left, maximizing):
        nonlocal node_count
        node_count += 1

        if node_game.is_draw():
            return 0, None
        if depth_left == 0:
            return probe_score_cached(node_game), None

        req = 1 if node_game.first_move else 2
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

        # single-move nodes
        if req == 1:
            scored = []
            for a in local_cand:
                child = simulate(node_game, [a], node_game.current_player)
                if is_win_after_placement(child, a):
                    return (INF if maximizing else -INF), [a]
                scored.append((probe_score_cached(child), a, child))
            scored.sort(reverse=maximizing, key=lambda t: t[0])
            for _, a, child in scored:
                sc, _ = recurse(child, depth_left - 1, not maximizing)
                if maximizing:
                    if sc > best_score:
                        best_score = sc
                        best_moves = [a]
                else:
                    if sc < best_score:
                        best_score = sc
                        best_moves = [a]
            return best_score, best_moves

        # two-move nodes: check immediate first-move wins
        for a in local_cand:
            child_a = simulate(node_game, [a], node_game.current_player)
            if is_win_after_placement(child_a, a):
                second = None
                for b in local_cand:
                    if b != a:
                        second = b
                        break
                if not second:
                    for b in local_avail:
                        if b != a:
                            second = b
                            break
                return (INF if maximizing else -INF), [a, second or a]

        # build unordered pairs
        pair_candidates = []
        if len(local_cand) >= 2:
            pair_candidates = list(combinations(local_cand, 2))
        else:
            a = local_cand[0]
            for b in local_avail:
                if b != a:
                    pair_candidates.append((a, b))

        scored_pairs = []
        for a, b in pair_candidates:
            child_ab = simulate(node_game, [a, b], node_game.current_player)
            if is_win_after_placement(child_ab, b) or is_win_after_placement(child_ab, a):
                return (INF if maximizing else -INF), [a, b]
            scored_pairs.append((probe_score_cached(child_ab), (a, b), child_ab))

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

    req_now = 1 if game.first_move else 2
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
