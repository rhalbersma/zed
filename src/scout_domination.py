#!/usr/bin/env python3

#          Copyright Rein Halbersma 2018-2021.
# Distributed under the Boost Software License, Version 1.0.
#    (See accompanying file LICENSE_1_0.txt or copy at
#          http://www.boost.org/LICENSE_1_0.txt)

from itertools import chain, product, repeat
import numpy as np
from z3 import Bool, If, Not, Or, Optimize, sat, Sum

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

# https://en.wikipedia.org/wiki/Dominating_set
# http://forum.stratego.com/topic/1134-stratego-quizz-and-training-forum/?p=441845
print("The minimum number of scouts on a Stratego board such that each square is occupied or threatened by a scout.")

# Variables
is_scout = np.array([ Bool("is_scout_%s%s" % (r, c)) for (r, c) in board() ]).reshape(H, W).tolist()

# Piece placement
no_scouts_in_lakes = [ Not(is_scout[r][c]) for (r, c) in lakes() ]

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

each_square_occupied_or_threatened_by_scout = [
    Or(
        is_scout[r][c],
        Or([
            is_scout[dr][dc]
            for (dr, dc) in scout_moves_from[r, c]
        ])
    )
    for (r, c) in board() if (r, c) not in lakes()
]

# Clauses
s = Optimize()
s.add(no_scouts_in_lakes)
s.add(each_square_occupied_or_threatened_by_scout)

# Objective
num_scouts = Sum([ If(is_scout[r][c], 1, 0) for (r, c) in board() ])
min_scouts = s.minimize(num_scouts)

if s.check() == sat:
    assert s.lower(min_scouts) == 8
    print("The minimum number of scouts satisfying the constraints == %s." % s.lower(min_scouts))
    print(diagram(s.model()))
else:
    print("Z3 failed to find a solution.")
