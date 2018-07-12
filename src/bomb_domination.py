#!/usr/bin/python3

#          Copyright Rein Halbersma 2018.
# Distributed under the Boost Software License, Version 1.0.
#    (See accompanying file LICENSE_1_0.txt or copy at
#          http://www.boost.org/LICENSE_1_0.txt)

import numpy as np
from z3 import *

# Stratego setup area dimensions
H, W =  4, 10
bomb = [ [ Bool("bomb_%s%s" % (r, c)) for c in range(W) ] for r in range(H) ]
num_bombs = Sum([ If(bomb[r][c], 1, 0) for r in range(H) for c in range(W) ])

def at_least_one_per_box(h, w):
    return [
        PbGe([
            (bomb[r + dr][c + dc], 1)
            for dr in range(h)
            for dc in range(w)
        ], 1)
        for r in range(H - h + 1)
        for c in range(W - w + 1)
    ]

# http://forum.stratego.com/topic/1134-stratego-quizz-and-training-forum/?p=11667
# http://forum.stratego.com/topic/1134-stratego-quizz-and-training-forum/?p=441746

problem = Optimize()
problem.add(at_least_one_per_box(2, 3))
problem.add(at_least_one_per_box(3, 2))
obj = problem.minimize(num_bombs)

print("Placing as few bombs as possible on a %sx%s board such that all 2x3 and 3x2 boxes have at least one bomb." % (H, W))
if problem.check() == sat:
    print("Minimum number of bombs satisfying the constraints == %s." % problem.lower(obj)) # 6
    m = problem.model()
    f = np.array([ [ 'B' if m.evaluate(bomb[r][c]) else '.' for c in range(W) ] for r in range(H) ]).reshape(H, W)
    print('%s' % '\n'.join(map(lambda row: ' '.join(map(str, row)), f)))
else:
    print("Z3 failed to find a solution.")

# http://forum.stratego.com/topic/1134-stratego-quizz-and-training-forum/?p=11661
# http://forum.stratego.com/topic/1134-stratego-quizz-and-training-forum/?p=441745

problem.add(at_least_one_per_box(1, 6))

print("Placing as few bombs as possible on a %sx%s board such that all 1x6, 2x3 and 3x2 boxes have at least one bomb." % (H, W))
if problem.check() == sat:
    print("Minimum number of bombs satisfying the constraints == %s." % problem.lower(obj)) # 7
    m = problem.model()
    f = np.array([ [ 'B' if m.evaluate(bomb[r][c]) else '.' for c in range(W) ] for r in range(H) ]).reshape(H, W)
    print('%s' % '\n'.join(map(lambda row: ' '.join(map(str, row)), f)))
else:
    print("Z3 failed to find a solution.")

