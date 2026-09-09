#          Copyright Rein Halbersma 2018-2026.
# Distributed under the Boost Software License, Version 1.0.
#    (See accompanying file LICENSE_1_0.txt or copy at
#          http://www.boost.org/LICENSE_1_0.txt)

"""z3 encoders for the four rules used by puzzles I-VI.

Two things here are load-bearing for performance and are not cosmetic:

  * SolverFor("QF_FD") rather than Solver().  QF_FD dispatches to the SAT core,
    which handles cardinality/pseudo-Boolean constraints natively.  The default
    Solver() sends Pb* to the SMT core's pseudo-Boolean theory instead, where
    puzzle VI's refutation does not finish at all.

  * Board.squares_rank_major() for variable declaration and constraint
    assertion.  Enumerating file-major costs ~74x on that same query, and unlike
    most timings here this one survives re-measurement: over five SAT random
    seeds with a 120s cap, rank-major solved 5/5 with a median of 1.24s,
    file-major 4/5 with a median of 91.27s.
"""
from itertools import product
from z3 import *

from .board import segments


def encode(problem, ctx=None):
    """Returns (solver, objective terms, scout vars, bomb vars, aux, context).

    Each problem gets its own z3 Context, so that problems cannot interfere and
    can be built in any order.  This is hygiene, not speed: sharing one context
    across all six measures the same (median 1.17s vs 1.13s on puzzle VI's
    refutation over five SAT random seeds).  It looked like a ~330x win when the
    driver still asserted the segment-saturation lemmas -- see _segment_used.
    """
    ctx = ctx or Context()
    board, rule = problem.board, problem.rule
    decl = list(board.squares_rank_major())
    sc = {q: Bool("s_%d_%d" % q, ctx) for q in decl}
    bo = {q: Bool("b_%d_%d" % q, ctx) for q in decl}
    s = SolverFor("QF_FD", ctx=ctx)
    _placement(board, s, sc, bo)
    blocked = lambda q: BoolVal(True, ctx) if q in board.lakes else bo[q]
    aux = {}

    if rule == "bomb_rect_cover":
        for q in board.squares_rank_major():        # this puzzle has no scouts
            s.add(Not(sc[q]))
        for (w, h) in problem.params["rectangles"]:
            for f in range(board.W - w + 1):
                for r in range(board.H - h + 1):
                    cells = [(f + df, r + dr) for df, dr in product(range(w), range(h))]
                    cells = [q for q in cells if q not in board.lakes]
                    if cells:
                        s.add(PbGe([(bo[q], 1) for q in cells], 1))
        obj = [(bo[q], 1) for q in board.playable()]

    elif rule == "domination":
        for q in board.playable():
            s.add(Or([sc[q]] + [sc[p] for p in reachable(board, q)]))
        obj = [(sc[q], 1) for q in board.playable()]

    elif rule == "independent":
        seen = {}
        for tag, line in _lines(board):
            prev = BoolVal(False, ctx)
            for q in line:
                cur = Bool("seen_%s_%d_%d" % (tag, q[0], q[1]), ctx)
                # a scout lies in the unbroken run ending at q
                s.add(cur == And(Not(blocked(q)), Or(sc[q], prev)))
                s.add(Not(And(sc[q], prev)))
                seen[(tag, q)] = cur
                prev = cur
        aux["segment_used"] = _segment_used(board, seen, blocked, ctx)
        obj = [(sc[q], 1) for q in board.playable()]

    elif rule == "exactly_one":
        # provable and local: three scouts in one segment make the middle one
        # threaten two, so every segment holds at most two.  Worth ~20%.
        ranks, files = segments(board)
        for seg in ranks + files:
            if len(seg) > 2:
                s.add(PbLe([(sc[q], 1) for q in seg], 2))
        for q in board.playable():
            s.add(Implies(sc[q], PbEq([(sc[p], 1) for p in reachable(board, q)], 1)))
        obj = [(sc[q], 1) for q in board.playable()]

    else:
        raise ValueError("unknown rule %r" % rule)

    return s, obj, sc, bo, aux, ctx


def reachable(board, q):
    """Squares a scout at q reaches in a straight line, stopping at lakes.

    Note that scouts do not block each other here; this follows the original
    scripts, and with at most one scout per segment the two readings agree.
    """
    f0, r0 = q
    out = []
    for df, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        f, r = f0 + df, r0 + dr
        while 0 <= f < board.W and 0 <= r < board.H and (f, r) not in board.lakes:
            out.append((f, r))
            f += df
            r += dr
    return out


def _placement(board, s, sc, bo):
    """Rules shared by every puzzle: lakes empty, no two pieces on a square,
    bombs only inside a setup area, and the per-area bomb budget."""
    allowed = board.bomb_squares()
    for q in board.squares_rank_major():
        if q in board.lakes:
            s.add(Not(sc[q]))
            s.add(Not(bo[q]))
        else:
            s.add(Not(And(sc[q], bo[q])))
        if q not in allowed:
            s.add(Not(bo[q]))
        if q in board.scouts_forbidden:
            s.add(Not(sc[q]))
    for sq, budget in board.setup:
        live = [q for q in sq if q not in board.lakes]
        if budget < len(live):
            s.add(PbLe([(bo[q], 1) for q in live], budget))


def _lines(board):
    ranks = [("rank", [(f, r) for f in range(board.W)]) for r in range(board.H)]
    files = [("file", [(f, r) for r in range(board.H)]) for f in range(board.W)]
    return ranks + files


def _segment_used(board, seen, blocked, ctx):
    """A segment is *used* iff a scout lies in it, i.e. seen[] holds at its last
    square.  Summing these counts the matched vertices of the bipartite graph,
    which for an independent set equals the number of scouts.

    Returned for exploration, but deliberately NOT asserted by solve.py.  Pinning
    both sides to N is redundant (it follows from the scout count) and it makes
    the search wildly unstable.  Puzzle VI's N=25 refutation under five SAT
    random seeds, 60s cap each:

        PbEq(scouts, 25)                        5/5 solved, median  1.11s
        PbGe(scouts, 25)                        5/5 solved, median  2.03s
        PbGe + saturation                       2/5 solved, median  4.89s
        PbEq + saturation                       2/5 solved, median 41.45s
        saturation alone                        1/5 solved, median  0.57s

    Saturation buys the best single runs (0.22s) and the worst (timeout), which
    is how it came to look like a 5x win on one lucky measurement."""
    used_rank = [And(seen[("rank", (f, r))],
                     BoolVal(True, ctx) if f == board.W - 1 else blocked((f + 1, r)))
                 for r in range(board.H) for f in range(board.W)]
    used_file = [And(seen[("file", (f, r))],
                     BoolVal(True, ctx) if r == board.H - 1 else blocked((f, r + 1)))
                 for f in range(board.W) for r in range(board.H)]
    return used_rank, used_file
