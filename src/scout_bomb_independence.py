#!/usr/bin/python3

#          Copyright Rein Halbersma 2018.
# Distributed under the Boost Software License, Version 1.0.
#    (See accompanying file LICENSE_1_0.txt or copy at
#          http://www.boost.org/LICENSE_1_0.txt)

from itertools import chain, product, repeat
import numpy as np
from z3 import And, Bool, If, Implies, Not, Or, PbEq, PbLe, sat, Solver, Sum

# Stratego board
H, W =  10, 10

def squares():
    return product(range(H), range(W))

def lakes():
    return product(range(4, 6), chain(range(2, 4), range(6, 8)))

def dmz():
    return product(range(4, 6), chain(range(0, 2), range(4, 6), range(8, W)))

def red_setup():
    return product(range(0, 4), range(W))

def blu_setup():
    return product(range(6, H), range(W))

# Board display
def piece(m, r, c):
    return '#' if (r, c) in lakes() else '2' if m.evaluate(is_scout[r][c]) else 'B' if m.evaluate(is_bomb[r][c]) else '.'

def board(model):
    b = np.array([ piece(model, r, c) for (r, c) in squares() ]).reshape(H, W)
    return "%s" % '\n'.join(map(lambda row: ' '.join(map(str, row)), b))

# http://forum.stratego.com/topic/1134-stratego-quizz-and-training-forum/?p=11671
# http://forum.stratego.com/topic/1134-stratego-quizz-and-training-forum/?p=458177
print("The maximum number of scouts on a Stratego board with at most 6 bombs in each setup area such that no scout threatens another scout.")

# Variables
is_scout = np.array([ Bool("is_scout_%s%s" % (r, c)) for (r, c) in squares() ]).reshape(H, W).tolist()
is_bomb  = np.array([ Bool("is_bomb_%s%s"  % (r, c)) for (r, c) in squares() ]).reshape(H, W).tolist()

# Piece placement
no_scouts_and_bombs_on_same_square = [ Not(And(is_scout[r][c], is_bomb[r][c])) for (r, c) in squares() ]
no_scouts_or_bombs_in_lakes = [ Not(Or(is_scout[r][c], is_bomb[r][c])) for (r, c) in lakes() ] 
no_bombs_in_dmz = [ Not(is_bomb[r][c]) for (r, c) in dmz() ]
at_most_six_bombs_in_red_setup = PbLe([ (is_bomb[r][c], 1) for (r, c) in red_setup() ], 6)
at_most_six_bombs_in_blu_setup = PbLe([ (is_bomb[r][c], 1) for (r, c) in blu_setup() ], 6)

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

scout_sum_segment = [ Sum([ If(is_scout[r][c], 1, 0) for (r, c) in s ]) for s in segments  ]
bomb_sum_segment = [ Sum([ If(is_bomb[r][c], 1, 0) for (r, c) in s ]) for s in segments  ]

at_most_one_more_scout_than_bombs_per_segment = [
    scout_sum_segment[i] <= bomb_sum_segment[i] + 1
    for i, _ in enumerate(segments)
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

L_scout_moves_cols = np.array([
    L_scout_moves_from(r, c)
    for (r, c) in squares()
]).reshape(H, W)

R_scout_moves_cols = np.array([
    R_scout_moves_from(r, c)
    for (r, c) in squares()
]).reshape(H, W)

D_scout_moves_rows = np.array([
    D_scout_moves_from(r, c)
    for (r, c) in squares()
]).reshape(H, W)

U_scout_moves_rows = np.array([
    U_scout_moves_from(r, c)
    for (r, c) in squares()
]).reshape(H, W)

def squares_in_between(b, e):
    return range(b + 1, e)

no_scout_threatens_another_scout = [ 
    Implies(
        is_scout[r][c], 
        And(
            [
                Implies(
                    is_scout[r][cL],
                    Or([
                        is_bomb[r][cb]
                        for cb in squares_in_between(cL, c)
                    ])
                )
                for cL in L_scout_moves_cols[r, c]
            ] +
            [
                Implies(
                    is_scout[r][cR],
                    Or([
                        is_bomb[r][cb]
                        for cb in squares_in_between(c, cR)
                    ])
                )
                for cR in R_scout_moves_cols[r, c]
            ] +
            [
                Implies(
                    is_scout[rD][c],
                    Or([
                        is_bomb[rb][c]
                        for rb in squares_in_between(rD, r)
                    ])
                )
                for rD in D_scout_moves_rows[r, c]
            ] +
            [
                Implies(
                    is_scout[rU][c],
                    Or([
                        is_bomb[rb][c]
                        for rb in squares_in_between(r, rU)
                    ])
                )
                for rU in U_scout_moves_rows[r, c]
            ]
        )
    ) 
    for (r, c) in squares() if (r, c) not in lakes()
]

# Clauses
s = Solver()
s.add(no_scouts_and_bombs_on_same_square)
s.add(no_scouts_or_bombs_in_lakes)
s.add(no_bombs_in_dmz)
s.add(at_most_one_more_scout_than_bombs_per_segment)
s.add(no_scout_threatens_another_scout)
s.add(at_most_six_bombs_in_red_setup)
s.add(at_most_six_bombs_in_blu_setup)

# Objective
max_scouts = 24
num_scouts = PbEq([ (is_scout[r][c], 1) for (r, c) in squares() ], max_scouts)
s.add(num_scouts)

if s.check() == sat:
    print("Maximum number of scouts satisfying constraints == %s." % max_scouts)
    print(board(s.model()))
else:
    print("Z3 failed to find a solution.")
