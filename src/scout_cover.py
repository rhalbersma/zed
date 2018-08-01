#!/usr/bin/python3

#          Copyright Rein Halbersma 2018.
# Distributed under the Boost Software License, Version 1.0.
#    (See accompanying file LICENSE_1_0.txt or copy at
#          http://www.boost.org/LICENSE_1_0.txt)

from itertools import chain, product, repeat
import numpy as np
from z3 import *

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
print("Placing as many scouts as possible on a %sx%s Stratego board such that they threaten exactly one other scout." % (H, W))

# Variables
is_scout = np.array([ Bool("is_scout_%s%s" % (r, c)) for (r, c) in squares() ]).reshape(H, W).tolist()

# Piece placement
no_scouts_in_lakes = [ Not(is_scout[r][c]) for (r, c) in lakes() ]

# Lines
open_rows = [ zip(repeat(r), range(W)) for r in chain(range(0, 4), range(6, H)) ]
open_cols = [ zip(range(H), repeat(c)) for c in chain(range(0, 2), range(4, 6), range(8, W)) ]
lake_rows = [ zip(repeat(r), range(c, c + 2)) for r in range(4, 6) for c in (0, 4, 8) ]
lake_cols = [ zip(range(r, r + 4), repeat(c)) for r in (0, 6) for c in chain(range(2, 4), range(6, 8)) ]
lines = open_rows + open_cols + lake_rows + lake_cols

max_two_per_line = [ 
    PbLe([ 
        (is_scout[r][c], 1) 
        for (r, c) in line 
    ], 2) 
    for line in lines 
]

# Scout moves
def L_scout_moves_from(r, c):
    if r in chain(range(0, 4), range(6, H)) or c in range(0, 2): 
        return range(0, c)
    elif c in range(4, 6):
        return range(4, c)
    elif c in range(8, W):
        return range(8, c)
    else:
        return range(0)

def R_scout_moves_from(r, c):
    if r in chain(range(0, 4), range(6, H)) or c in range(8, W):
        return range(c + 1, W)
    elif c in range(0, 2):
        return range(c + 1, 2)
    elif c in range(4, 6):
        return range(c + 1, 6)
    else:
        return range(0)

def D_scout_moves_from(r, c):
    if c in chain(range(0, 2), range(4, 6), range(8, W)) or r in range(0, 4): 
        return range(0, r)
    elif r in range(6, H):
        return range(6, r)
    else:
        return range(0)

def U_scout_moves_from(r, c):
    if c in chain(range(0, 2), range(4, 6), range(8, W)) or r in range(6, H):
        return range(r + 1, H)
    elif r in range(0, 4):
        return range(r + 1, 4)
    else:
        return range(0)

scout_moves_from = np.array([
    chain(
        zip(repeat(r), L_scout_moves_from(r, c)),
        zip(repeat(r), R_scout_moves_from(r, c)),    
        zip(D_scout_moves_from(r, c), repeat(c)),
        zip(U_scout_moves_from(r, c), repeat(c))
    )
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

# Clauses
s = Optimize()
#s = Solver()
s.add(no_scouts_in_lakes)
s.add(max_two_per_line)
s.add(scouts_threaten_exactly_one_other_scout)

# Objective
num_scouts = Sum([ If(is_scout[r][c], 1, 0) for (r, c) in squares() ])
num_scout_pairs = Int('K')
s.add(num_scouts == 2 * num_scout_pairs)
max_scouts = s.maximize(num_scout_pairs)
#num_scouts = PbEq([ (is_scout[r][c], 1) for (r, c) in squares() ], 20)
#s.add(num_scouts)

if s.check() == sat:
    #assert s.upper(max_scouts) == 20
    print("Maximum number of scouts satisfying constraints == %s." % s.upper(num_scout_pairs))
    print(board(s.model()))
else:
    print("Z3 failed to find a solution.")

