#!/usr/bin/python3

#          Copyright Rein Halbersma 2018.
# Distributed under the Boost Software License, Version 1.0.
#    (See accompanying file LICENSE_1_0.txt or copy at
#          http://www.boost.org/LICENSE_1_0.txt)

from itertools import chain, product, repeat
import numpy as np
from z3 import Bool, Implies, Not, PbEq, PbLe, sat, Solver

# Stratego board
H, W =  10, 10

def squares():
    return product(range(H), range(W))

def lakes():
    return product(range(4, 6), chain(range(2, 4), range(6, 8)))

# Board display
def piece(m, r, c):
    return '#' if (r, c) in lakes() else '2' if m.evaluate(is_scout[r][c]) else '.'

def board(model):
    b = np.array([ piece(model, r, c) for (r, c) in squares() ]).reshape(H, W)
    return "%s" % '\n'.join(map(lambda row: ' '.join(map(str, row)), b))

# http://forum.stratego.com/topic/1134-stratego-quizz-and-training-forum/?p=11670
# http://forum.stratego.com/topic/1134-stratego-quizz-and-training-forum/?p=457225
print("The maximum number of scouts on a Stratego board such that each scout threatens exactly one other scout.")

# Variables
is_scout = np.array([ Bool("is_scout_%s%s" % (r, c)) for (r, c) in squares() ]).reshape(H, W).tolist()

# Piece placement
no_scouts_in_lakes = [ Not(is_scout[r][c]) for (r, c) in lakes() ]

# Segments
open_rows = [ list(zip(repeat(r), range(W))) for r in chain(range(0, 4), range(6, H)) ]
open_cols = [ list(zip(range(H), repeat(c))) for c in chain(range(0, 2), range(4, 6), range(8, W)) ]
lake_rows = [ list(zip(repeat(r), range(c, c + 2))) for r in range(4, 6) for c in (0, 4, 8) ]
lake_cols = [ list(zip(range(r, r + 4), repeat(c))) for r in (0, 6) for c in chain(range(2, 4), range(6, 8)) ]
segments = open_rows + open_cols + lake_rows + lake_cols

assert len(open_rows) == 8
assert len(open_cols) == 6
assert len(lake_rows) == 6
assert len(lake_cols) == 8
assert len(segments) == 28

at_most_two_scouts_per_segment = [
    PbLe([
        (is_scout[r][c], 1)
        for (r, c) in s
    ], 2)
    for s in segments
]

# Scout moves in the left (L), right (R), downward (D) and upward (U) directions
def L_scout_moves_from(r, c):
    if r in chain(range(0, 4), range(6, H)):
        return range(0, c)
    elif c in range(0, 2):
        return range(0, c)
    elif c in range(4, 6):
        return range(4, c)
    elif c in range(8, W):
        return range(8, c)
    else:
        return range(0)

def R_scout_moves_from(r, c):
    if r in chain(range(0, 4), range(6, H)):
        return range(c + 1, W)
    elif c in range(0, 2):
        return range(c + 1, 2)
    elif c in range(4, 6):
        return range(c + 1, 6)
    elif c in range(8, W):
        return range(c + 1, W)
    else:
        return range(0)

def D_scout_moves_from(r, c):
    if c in chain(range(0, 2), range(4, 6), range(8, W)):
        return range(0, r)
    elif r in range(0, 4):
        return range(0, r)
    elif r in range(6, H):
        return range(6, r)
    else:
        return range(0)

def U_scout_moves_from(r, c):
    if c in chain(range(0, 2), range(4, 6), range(8, W)):
        return range(r + 1, H)
    elif r in range(0, 4):
        return range(r + 1, 4)
    elif r in range(6, H):
        return range(r + 1, H)
    else:
        return range(0)

scout_moves_from = np.array([
    list(chain(
        zip(repeat(r), L_scout_moves_from(r, c)),
        zip(repeat(r), R_scout_moves_from(r, c)),
        zip(D_scout_moves_from(r, c), repeat(c)),
        zip(U_scout_moves_from(r, c), repeat(c))
    ))
    for (r, c) in squares()
]).reshape(H, W)

scouts_threaten_exactly_one_other_scout = [
    Implies(
        is_scout[r][c],
        PbEq([
            (is_scout[dr][dc], 1)
            for (dr, dc) in scout_moves_from[r, c]
        ], 1)
    )
    for (r, c) in squares() if (r, c) not in lakes()
]

# Clauses (Optimize() takes too long on this problem, Solver() will proof max_scouts = 18 instantly, and disproof max_scouts = 20 within a minute)
s = Solver()
s.add(no_scouts_in_lakes)
s.add(at_most_two_scouts_per_segment)
s.add(scouts_threaten_exactly_one_other_scout)

# Objective
max_scouts = 18
num_scouts = PbEq([ (is_scout[r][c], 1) for (r, c) in squares() ], max_scouts)
s.add(num_scouts)

if s.check() == sat:
    print("The maximum number of scouts satisfying the constraints == %s." % max_scouts)
    print(board(s.model()))
else:
    print("Z3 failed to find a solution.")
