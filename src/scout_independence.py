#!/usr/bin/env python3

#          Copyright Rein Halbersma 2018-2021.
# Distributed under the Boost Software License, Version 1.0.
#    (See accompanying file LICENSE_1_0.txt or copy at
#          http://www.boost.org/LICENSE_1_0.txt)

from itertools import chain, product, repeat
import numpy as np
from z3 import And, Bool, If, Implies, Not, PbEq, PbLe, Optimize, sat, Sum

# Stratego board
H, W =  10, 10

def board():
    return product(range(H), range(W))

def lakes():
    return product(range(4, 6), chain(range(2, 4), range(6, 8)))

# Board display
def piece(m, r, c):
    return '#' if (r, c) in lakes() else '2' if m.evaluate(is_scout[r][c]) else '.'

def diagram(model):
    b = np.array([ piece(model, r, c) for (r, c) in board() ]).reshape(H, W)
    return "%s" % '\n'.join(map(lambda row: ' '.join(map(str, row)), b))

# https://en.wikipedia.org/wiki/Independent_set_(graph_theory)
# http://forum.stratego.com/topic/1134-stratego-quizz-and-training-forum/?p=11659
# http://forum.stratego.com/topic/1146-stratego-quizz-and-training-forum-answers/?p=11812
# http://forum.stratego.com/topic/1134-stratego-quizz-and-training-forum/?p=441750
print("The maximum number of scouts on a Stratego board such that no scout threatens another scout.")

# Variables
is_scout = np.array([ Bool("is_scout_%s%s" % (r, c)) for (r, c) in board() ]).reshape(H, W).tolist()

# Piece placement
no_scouts_in_lakes = [ Not(is_scout[r][c]) for (r, c) in lakes() ]

# Segments
open_rows = [ list(zip(repeat(r), range(W))) for r in chain(range(0, 4), range(6, H)) ]
open_cols = [ list(zip(range(H), repeat(c))) for c in chain(range(0, 2), range(4, 6), range(8, W)) ]
lake_rows = [ list(zip(repeat(r), range(c, c + 2))) for r in range(4, 6) for c in (0, 4, 8) ]
lake_cols = [ list(zip(range(r, r + 4), repeat(c))) for r in (0, 6) for c in chain(range(2, 4), range(6, 8)) ]
segments = open_rows + open_cols + lake_rows + lake_cols

# TODO: incorporate the fixed issue https://github.com/Z3Prover/z3/issues/1782 as soon as there is a new release available
at_most_one_scout_per_segment = [
    PbEq([
        (is_scout[r][c], 1)
        for (r, c) in s
    ], 1)
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
    for (r, c) in board()
]).reshape(H, W)

no_scout_threatens_another_scout = [
    Implies(
        is_scout[r][c],
        And([
            Not(is_scout[dr][dc])
            for (dr, dc) in scout_moves_from[r, c]
        ])
    )
    for (r, c) in board() if (r, c) not in lakes()
]

# Clauses
s = Optimize()
s.add(no_scouts_in_lakes)
s.add(at_most_one_scout_per_segment)
s.add(no_scout_threatens_another_scout)

# Objective
num_scouts = Sum([ If(is_scout[r][c], 1, 0) for (r, c) in board() ])
max_scouts = s.maximize(num_scouts)

if s.check() == sat:
    #assert s.upper(max_scouts) == 14
    print("The maximum number of scouts satisfying the constraints == %s." % s.upper(max_scouts))
    print(diagram(s.model()))
else:
    print("Z3 failed to find a solution.")
