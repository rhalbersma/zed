#!/usr/bin/python3

#          Copyright Rein Halbersma 2018.
# Distributed under the Boost Software License, Version 1.0.
#    (See accompanying file LICENSE_1_0.txt or copy at
#          http://www.boost.org/LICENSE_1_0.txt)

from itertools import chain, product
import numpy as np
from z3 import *

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
    return '#' if (r, c) in lakes() else '2' if m.evaluate(is_scout[r][c]) else 'B' if m.evaluate(is_lake[r][c]) else '.'

def board(model):
    b = np.array([ piece(model, r, c) for (r, c) in squares() ]).reshape(H, W)
    return "%s" % '\n'.join(map(lambda row: ' '.join(map(str, row)), b))

# http://forum.stratego.com/topic/1134-stratego-quizz-and-training-forum/?p=11671
# http://forum.stratego.com/topic/1134-stratego-quizz-and-training-forum/?p=458177
print("Placing as many scouts as possible on a %sx%s Stratego board with at most 6 bombs in each setup area such that the scouts don't threaten each other." % (H, W))

# Variables
is_scout = np.array([ Bool("is_scout_%s%s" % (r, c)) for (r, c) in squares() ]).reshape(H, W).tolist()
is_lake  = np.array([ Bool("is_lake_%s%s"  % (r, c)) for (r, c) in squares() ]).reshape(H, W).tolist()

# Piece placement
lakes_in_lakes = [ is_lake[r][c] for (r, c) in lakes() ] 
disjoint_scouts_and_lakes = [ Not(And(is_scout[r][c], is_lake[r][c])) for (r, c) in squares() ]
no_dmz_bombs = [ Not(is_lake[r][c]) for (r, c) in dmz() ]

# Scout moves
def right_scout_moves_from(c):
    return range(c + 1, W)

def up_scout_moves_from(r):
    return range(r + 1, H) 

def squares_in_between(b, e):
    return range(b + 1, e)

no_mutual_scout_threats = [ 
    Implies(
        is_scout[r][c], 
        And(
            [
                Implies(
                    is_scout[r][cR],
                    Or([
                        is_lake[r][cb]
                        for cb in squares_in_between(c, cR)
                    ])
                )
                for cR in right_scout_moves_from(c)            
            ] +
            [
                Implies(
                    is_scout[rU][c],
                    Or([
                        is_lake[rb][c]
                        for rb in squares_in_between(r, rU)
                    ])
                )
                for rU in up_scout_moves_from(r)
            ]
        )
    ) 
    for (r, c) in squares() 
]

num_red_bombs = PbLe([ (is_lake[r][c], 1) for (r, c) in red_setup() ], 6)
num_blu_bombs = PbLe([ (is_lake[r][c], 1) for (r, c) in blu_setup() ], 6)
num_scouts = PbEq([ (is_scout[r][c], 1) for (r, c) in squares() ], 24)

# Clauses
#s = Optimize()
s = Solver()
s.add(lakes_in_lakes)
s.add(disjoint_scouts_and_lakes)
s.add(no_mutual_scout_threats)
s.add(no_dmz_bombs)
s.add(num_red_bombs)
s.add(num_blu_bombs)
s.add(num_scouts)
#num_scouts = Sum([ If(is_scout[r][c], 1, 0) for (r, c) in squares() ])
#max_scouts = s.maximize(num_scouts)

if s.check() == sat:
    #print("Maximum number of scouts satisfying constraints == %s." % s.upper(max_scouts)) # 14
    print(board(s.model()))
else:
    print("Z3 failed to find a solution.")

