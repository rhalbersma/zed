#          Copyright Rein Halbersma 2018-2026.
# Distributed under the Boost Software License, Version 1.0.
#    (See accompanying file LICENSE_1_0.txt or copy at
#          http://www.boost.org/LICENSE_1_0.txt)

"""One driver for every puzzle.  The search shape follows from the rule's
monotonicity, not from the puzzle.

Optimize()/maximize() is deliberately not used.  It cannot be pinned to QF_FD,
its objective must be arithmetic (it rejects a Pb* term outright), and it fails
to finish on puzzles V and VI even given ten minutes.
"""
import time

from z3 import *

from . import rules
from .board import counting_cap, matching_number, segments


def solve(problem, verbose=True, seed_heuristic=True):
    board = problem.board
    s, obj, sc, bo, aux, _ = rules.encode(problem)
    log, t0 = [], time.time()

    def query(k, extra):
        # push/pop rather than accumulating: the subsumed bounds and the lemmas
        # learned on easy rungs cost more than the base clauses they keep.
        s.push()
        for e in extra:
            s.add(e)
        t = time.time()
        res = s.check()
        dt = time.time() - t
        model = s.model() if res == sat else None
        s.pop()
        log.append((k, str(res), dt))
        if verbose:
            print("    N=%-3d %-6s %6.2fs" % (k, res, dt))
        return res, model

    best, best_model = None, None

    if problem.sense == "min":
        # feasibility grows with k, so the first sat is the minimum
        for k in range(0, len(board.playable()) + 1):
            res, m = query(k, [PbLe(obj, k)])
            if res == sat:
                best, best_model = k, m
                break

    elif problem.rule == "independent":
        # independence is downward closed, so the first unsat proves the maximum
        cap = counting_cap(board)
        lo = 0
        if seed_heuristic:
            t = time.time()
            lo = _heuristic(board)
            if verbose:
                print("    heuristic lower bound = %d  (%.2fs)" % (lo, time.time() - t))
        used_rank, used_file = aux["segment_used"]
        k = max(1, lo)
        while k <= cap:
            res, m = query(k, [PbGe(obj, k),
                               PbEq([(x, 1) for x in used_rank], k),
                               PbEq([(x, 1) for x in used_file], k)])
            if res != sat:
                break
            best, best_model = k, m
            k += 1

    else:
        # "exactly one" is NOT downward closed: sat at k says nothing about k-2,
        # so we scan down from the cap and take the first sat.  N is even because
        # the threat relation is a perfect matching on the scouts.
        ranks, files = segments(board)
        for k in range(2 * min(len(ranks), len(files)), 0, -1):
            if k % 2:
                continue
            res, m = query(k, [PbEq(obj, k)])
            if res == sat:
                best, best_model = k, m
                break

    return dict(problem=problem, optimum=best, model=best_model, sc=sc, bo=bo,
                log=log, total=time.time() - t0)


def _heuristic(board, restarts=20, seed=0):
    """Local search over bomb layouts scored by matching number.

    For the independence rule this is a polynomial lower bound, so the solver
    usually only has to run the single refutation that proves maximality.
    """
    import random
    rng = random.Random(seed)
    pools = [[q for q in sq if q not in board.lakes] for sq, _ in board.setup]
    budgets = [b for _, b in board.setup]
    if not pools:
        return matching_number(board)
    best = 0
    for _ in range(restarts):
        bombs = set()
        for pool, budget in zip(pools, budgets):
            bombs |= set(rng.sample(pool, min(budget, len(pool))))
        cur, improved = matching_number(board, bombs), True
        while improved:
            improved = False
            for old in list(bombs):
                pool = next(p for p in pools if old in p)
                for new in pool:
                    if new in bombs:
                        continue
                    candidate = (bombs - {old}) | {new}
                    value = matching_number(board, candidate)
                    if value > cur:
                        bombs, cur, improved = candidate, value, True
                        break
                if improved:
                    break
        best = max(best, cur)
    return best


def diagram(result, labels=True):
    """Chess layout: rank H at the top, rank 1 at the bottom, files a.. below."""
    board, model = result["problem"].board, result["model"]
    if model is None:
        return "(no model)"
    out = []
    width = len(str(board.H))
    for r in range(board.H - 1, -1, -1):
        row = []
        for f in range(board.W):
            q = (f, r)
            if q in board.lakes:
                row.append("#")
            elif is_true(model.eval(result["sc"][q], True)):
                row.append("2")
            elif is_true(model.eval(result["bo"][q], True)):
                row.append("B")
            else:
                row.append(".")
        out.append(("%*d " % (width, r + 1) if labels else "") + " ".join(row))
    if labels:
        out.append(" " * (width + 1) + " ".join(chr(ord("a") + f) for f in range(board.W)))
    return "\n".join(out)
