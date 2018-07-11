#!/usr/bin/python3

#          Copyright Rein Halbersma 2018.
# Distributed under the Boost Software License, Version 1.0.
#    (See accompanying file LICENSE_1_0.txt or copy at
#          http://www.boost.org/LICENSE_1_0.txt)

import numpy as np
from operator import ge
from z3 import *

# Stratego setup area dimensions
H, W =  4, 10
bomb = [ [ Int("bomb_%s%s" % (r, c)) for c in range(W) ] for r in range(H) ]
num_bombs = Sum([ bomb[r][c] for r in range(H) for c in range(W) ])
squares_are_allowed = [ Or(0 == bomb[r][c], bomb[r][c] == 1) for r in range(H) for c in range(W) ]

# http://forum.stratego.com/topic/1134-stratego-quizz-and-training-forum/?p=11661
# http://forum.stratego.com/topic/1134-stratego-quizz-and-training-forum/?p=441745

def num_bombs_in_box(h, w, fn, b):
    return [
        fn(Sum([
            bomb[r + dr][c + dc]
            for dr in range(h)
            for dc in range(w)
        ]), b)
        for r in range(H - h + 1)
        for c in range(W - w + 1)
    ]

problem = Optimize()
problem.add(squares_are_allowed)
problem.add(num_bombs_in_box(1, 6, ge, 1))
problem.add(num_bombs_in_box(2, 3, ge, 1))
problem.add(num_bombs_in_box(3, 2, ge, 1))
obj = problem.minimize(num_bombs)

print("Placing as few bombs as possible on a %sx%s board such that all 1x6, 2x3 and 3x2 boxes have at least one bomb." % (H, W))
if problem.check() == sat:
    print("Minimum number of bombs satisfying the constraints == %s." % problem.lower(obj)) # 7
    m = problem.model()
    f = np.array([ [ 'B' if m.evaluate(bomb[r][c]) == 1 else '.' for c in range(W) ] for r in range(H) ]).reshape(H, W)
    print('%s' % '\n'.join(map(lambda row: ' '.join(map(str, row)), f)))
else:
    print("Z3 failed to find a solution.")

# http://forum.stratego.com/topic/1134-stratego-quizz-and-training-forum/?p=11667
# http://forum.stratego.com/topic/1134-stratego-quizz-and-training-forum/?p=441746

problem = Optimize()
problem.add(squares_are_allowed)
problem.add(num_bombs_in_box(2, 3, ge, 1))
problem.add(num_bombs_in_box(3, 2, ge, 1))
obj = problem.minimize(num_bombs)

print("Placing as few bombs as possible on a %sx%s board such that all 2x3 and 3x2 boxes have at least one bomb." % (H, W))
if problem.check() == sat:
    print("Minimum number of bombs satisfying the constraints == %s." % problem.lower(obj)) # 6
    m = problem.model()
    f = np.array([ [ 'B' if m.evaluate(bomb[r][c]) == 1 else '.' for c in range(W) ] for r in range(H) ]).reshape(H, W)
    print('%s' % '\n'.join(map(lambda row: ' '.join(map(str, row)), f)))
else:
    print("Z3 failed to find a solution.")
   
