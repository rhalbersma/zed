#          Copyright Rein Halbersma 2018-2026.
# Distributed under the Boost Software License, Version 1.0.
#    (See accompanying file LICENSE_1_0.txt or copy at
#          http://www.boost.org/LICENSE_1_0.txt)

"""Board geometry, shared by every puzzle.

Coordinates follow tabula (https://github.com/rhalbersma/tabula): a square is a
(file, rank) pair, file 0..W-1 shown as a..z, rank 0..H-1 shown as 1..H with
rank 1 at the bottom.  A *rank segment* is a horizontal run of squares, a *file
segment* a vertical one.
"""
from dataclasses import dataclass
from itertools import product


@dataclass(frozen=True)
class Board:
    W: int                                  # width  (files)
    H: int                                  # height (ranks)
    lakes: frozenset = frozenset()          # impassable, never occupied
    setup: tuple = ()                       # ((squares, bomb budget), ...) per setup area
    scouts_forbidden: frozenset = frozenset()

    def squares(self):
        return product(range(self.W), range(self.H))     # (file, rank)

    def squares_rank_major(self):
        """The same squares, rank by rank.

        Used to fix the order in which z3 variables are declared and constraints
        asserted.  This is not cosmetic: declaring them file-major costs a factor
        ~50 on the hardest query (35.5s vs 0.2s on puzzle VI, z3 4.13/5.1).
        """
        return ((f, r) for r in range(self.H) for f in range(self.W))

    def playable(self):
        return [q for q in self.squares_rank_major() if q not in self.lakes]

    def bomb_squares(self):
        out = set()
        for sq, _ in self.setup:
            out |= set(sq)
        return out - set(self.lakes)

    def bomb_budget(self):
        return sum(b for _, b in self.setup)


def rect_from_bounds(f0, r0, w, h):
    """Lower-left corner plus extent: the w x h block anchored at (f0, r0).

    Same convention as matplotlib's Rectangle((x, y), width, height) and
    Bbox.from_bounds(x0, y0, width, height), and as Scan's bit::rect(x, y, w, h)
    except that Scan anchors at the top-left corner.
    """
    return frozenset((f0 + df, r0 + dr) for df, dr in product(range(w), range(h)))


def span(f0, r0, f1, r1):
    """Two corners, INCLUSIVE: every square from (f0, r0) to (f1, r1).

    Like Bbox.from_extents(left, bottom, right, top) or shapely's
    box(minx, miny, maxx, maxy), except inclusive at the far corner because
    squares are discrete: span(0, 0, 9, 3) is a1-j4, i.e. rect_from_bounds(0, 0, 10, 4).
    """
    return frozenset(product(range(f0, f1 + 1), range(r0, r1 + 1)))


def square_name(q):
    """(2, 4) -> 'c5', matching tabula's algebraic() and Scan's "c5"_sq."""
    f, r = q
    return "%s%d" % (chr(ord("a") + f), r + 1)


def segments(board, bombs=frozenset()):
    """Maximal runs free of lakes and bombs.  Returns (rank segments, file segments)."""
    blocked = set(board.lakes) | set(bombs)
    ranks, files = [], []
    for r in range(board.H):
        run = []
        for f in range(board.W):
            if (f, r) in blocked:
                if run: ranks.append(run); run = []
            else: run.append((f, r))
        if run: ranks.append(run)
    for f in range(board.W):
        run = []
        for r in range(board.H):
            if (f, r) in blocked:
                if run: files.append(run); run = []
            else: run.append((f, r))
        if run: files.append(run)
    return ranks, files


def matching_number(board, bombs=frozenset()):
    """Maximum independent scouts for a FIXED bomb layout.

    Independence means at most one scout per segment, and every square lies in
    exactly one rank segment and one file segment.  So a scout set is a matching
    in the bipartite graph (rank segments x file segments) whose edges are the
    free squares, and the maximum is that graph's matching number -- polynomial,
    no solver needed.
    """
    ranks, files = segments(board, bombs)
    rid = {q: i for i, seg in enumerate(ranks) for q in seg}
    fid = {q: j for j, seg in enumerate(files) for q in seg}
    adj = [set() for _ in ranks]
    for q in rid:
        if q not in board.scouts_forbidden and q not in bombs:
            adj[rid[q]].add(fid[q])
    match = [None] * len(files)

    def augment(u, seen):
        for v in adj[u]:
            if v in seen:
                continue
            seen.add(v)
            if match[v] is None or augment(match[v], seen):
                match[v] = u
                return True
        return False

    return sum(augment(u, set()) for u in range(len(ranks)))


def counting_cap(board):
    """N <= min(#rank segments, #file segments), and each bomb splits at most one
    segment per orientation, so the ceiling is base + bomb budget."""
    ranks, files = segments(board)
    return min(len(ranks), len(files)) + board.bomb_budget()


def setup_areas(board):
    """The two setup areas: full width, below and above the lake ranks."""
    lake_ranks = {r for _, r in board.lakes}
    if not lake_ranks:
        return frozenset(), frozenset()
    lo, hi = min(lake_ranks), max(lake_ranks)
    near = frozenset((f, r) for f in range(board.W) for r in range(lo))
    far = frozenset((f, r) for f in range(board.W) for r in range(hi + 1, board.H))
    return near, far


def with_setup(board, budget):
    """The same board, with its derived setup areas each given a bomb budget."""
    near, far = setup_areas(board)
    return Board(board.W, board.H, board.lakes, ((near, budget), (far, budget)),
                 board.scouts_forbidden)
