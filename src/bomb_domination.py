#!/usr/bin/python3

#          Copyright Rein Halbersma 2018.
# Distributed under the Boost Software License, Version 1.0.
#    (See accompanying file LICENSE_1_0.txt or copy at
#          http://www.boost.org/LICENSE_1_0.txt)

from itertools import product
import numpy as np
from z3 import Bool, If, Optimize, PbGe, Sum, sat

# Stratego setup area
H, W =  4, 10

def rectangle(h, w):
    return product(range(h), range(w))

# Board display
def piece(model, r, c):
    return 'B' if model.evaluate(is_bomb[r][c]) else '.'

def board(model):
    board = np.array([ piece(model, r, c) for (r, c) in rectangle(H, W) ]).reshape(H, W)
    return "%s" % '\n'.join(map(lambda row: ' '.join(map(str, row)), board))

# http://forum.stratego.com/topic/1134-stratego-quizz-and-training-forum/?p=11667
# http://forum.stratego.com/topic/1134-stratego-quizz-and-training-forum/?p=441746
print("The minimum number of bombs on a Stratego setup area such that each 2x3 and 3x2 rectangle has at least one bomb.   ")

# Variables
is_bomb = np.array([ Bool("is_bomb_%s%s" % (r, c)) for (r, c) in rectangle(H, W) ]).reshape(H, W).tolist()

# Bomb placement
def at_least_one_bomb_for_each_rectangle(h, w):
    return [
        PbGe([
            (is_bomb[r + dr][c + dc], 1)
            for (dr, dc) in rectangle(h, w)
        ], 1)
        for (r, c) in rectangle(H - h + 1, W - w + 1)
    ]

# Clauses
s = Optimize()
s.add(at_least_one_bomb_for_each_rectangle(2, 3))
s.add(at_least_one_bomb_for_each_rectangle(3, 2))

# Objective
num_bombs = Sum([ If(is_bomb[r][c], 1, 0) for (r, c) in rectangle(H, W) ])
min_bombs = s.minimize(num_bombs)

if s.check() == sat:
    assert s.lower(min_bombs) == 6
    print("The minimum number of bombs satisfying the constraints == %s.   " % s.lower(min_bombs))
    print(board(s.model()))
else:
    print("Z3 failed to find a solution.")

# http://forum.stratego.com/topic/1134-stratego-quizz-and-training-forum/?p=11661
# http://forum.stratego.com/topic/1146-stratego-quizz-and-training-forum-answers/?p=11813
# http://forum.stratego.com/topic/1134-stratego-quizz-and-training-forum/?p=441745
print("The minimum number of bombs on a Stratego setup area such that each 2x3, 3x2 and 1x6 rectangle has at least one bomb.   ")

# Extra clause
s.add(at_least_one_bomb_for_each_rectangle(1, 6))

if s.check() == sat:
    assert s.lower(min_bombs) == 7
    print("The minimum number of bombs satisfying the constraints == %s.   " % s.lower(min_bombs))
    print(board(s.model()))
else:
    print("Z3 failed to find a solution.")
