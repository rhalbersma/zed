#!/usr/bin/env python3

#          Copyright Rein Halbersma 2018-2026.
# Distributed under the Boost Software License, Version 1.0.
#    (See accompanying file LICENSE_1_0.txt or copy at
#          http://www.boost.org/LICENSE_1_0.txt)

"""Solve every puzzle and check it against the published answer.

    ./solve_all.py            all six
    ./solve_all.py VI         just the ones whose name starts with VI
    ./solve_all.py -q         answers only, no per-query log
"""
import sys

from zed import solve
from zed.problems import CATALOG


def main(argv):
    quiet = "-q" in argv
    prefix = next((a for a in argv[1:] if not a.startswith("-")), None)
    failures = 0
    for problem in CATALOG:
        if prefix and not problem.name.startswith(prefix):
            continue
        print("==", problem.name)
        result = solve.solve(problem, verbose=not quiet)
        ok = result["optimum"] == problem.expected
        failures += not ok
        print("  -> %s   %s   %.2fs" % (
            result["optimum"],
            "OK" if ok else "MISMATCH (expected %s)" % problem.expected,
            result["total"]))
        print(solve.diagram(result))
        print()
    return failures


if __name__ == "__main__":
    sys.exit(main(sys.argv))
