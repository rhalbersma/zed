#!/usr/bin/env python3

#          Copyright Rein Halbersma 2018-2026.
# Distributed under the Boost Software License, Version 1.0.
#    (See accompanying file LICENSE_1_0.txt or copy at
#          http://www.boost.org/LICENSE_1_0.txt)

"""Puzzle VI's question -- how many mutually invisible scouts fit? -- asked of
every board, over a range of bombs per setup area.

    ./sweep.py               all boards, 0..6 bombs
    ./sweep.py classic       just that board
    ./sweep.py -b 5          just that budget

The counting cap in the last column is #segments + bombs: a bomb splits at most
one segment per orientation, so it can buy at most one extra scout.  Where the
answer equals the cap the bound alone settles it and no refutation is needed;
where it falls short, the solver has to prove the gap.
"""
import sys
import time

from zed import solve
from zed.board import counting_cap, with_setup
from zed.problems import Problem, CLASSIC, L_ATTAQUE, QUICK_ARENA, TRAVEL

BOARDS = [("l_attaque", L_ATTAQUE), ("classic", CLASSIC),
          ("quick_arena", QUICK_ARENA), ("travel", TRAVEL)]


def main(argv):
    budgets = range(0, 7)
    if "-b" in argv:
        budgets = [int(argv[argv.index("-b") + 1])]
    prefix = next((a for a in argv[1:] if not a.startswith("-") and not a.isdigit()), None)
    boards = [(n, b) for n, b in BOARDS if not prefix or n.startswith(prefix)]

    print("max independent scouts vs bombs per setup area\n")
    print("board        " + "".join("%5s" % ("b=%d" % b) for b in budgets) + "   cap")
    for name, base in boards:
        row, cap = [], None
        for b in budgets:
            board = with_setup(base, b)
            cap = counting_cap(board)
            t = time.time()
            result = solve.solve(Problem(name, board, "independent", "max"),
                                 verbose=False)
            row.append((result["optimum"], time.time() - t))
        print("%-12s " % name
              + "".join("%5d" % n for n, _ in row)
              + "   %d" % cap
              + "   (%.1fs)" % sum(dt for _, dt in row))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
