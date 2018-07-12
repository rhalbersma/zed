#!/usr/bin/python3

#          Copyright Rein Halbersma 2018.
# Distributed under the Boost Software License, Version 1.0.
#    (See accompanying file LICENSE_1_0.txt or copy at
#          http://www.boost.org/LICENSE_1_0.txt)

from itertools import chain
import numpy as np
from z3 import *

# Stratego board dimensions
H, W =  10, 10
scout = [ [ Bool("scout_%s%s" % (r, c)) for c in range(W) ] for r in range(H) ]
num_scouts = Sum([ If(scout[r][c], 1, 0) for r in range(H) for c in range(W) ])
lakes_are_forbidden = [ Not(scout[r][c]) for r in range(4, 6) for c in chain(range(2, 4), range(6, 8)) ]

# https://en.wikipedia.org/wiki/Dominating_set
# http://forum.stratego.com/topic/1134-stratego-quizz-and-training-forum/?p=441845

at_least_one_per_open_row    = [ PbGe([ (scout[r][c], 1) for c in range(W) ], 1) for r in chain(range(0, 4), range(6, H)) ]
at_least_one_per_open_column = [ PbGe([ (scout[r][c], 1) for r in range(H) ], 1) for c in chain(range(0, 2), range(4, 6), range(8, W)) ]

problem = Optimize()
problem.add(lakes_are_forbidden)
problem.add(at_least_one_per_open_row)
problem.add(at_least_one_per_open_column)
obj = problem.minimize(num_scouts)

print("Placing as few scouts as possible on a %sx%s Stratego board such that they threaten every square." % (H, W))
if problem.check() == sat:
    print("Minimum number of scouts satisfying constraints == %s." % problem.upper(obj)) # 8
    m = problem.model()
    f = np.array([ [ '2' if m.evaluate(scout[r][c]) else ('#' if r in range(4, 6) and c in chain(range(2, 4), range(6, 8)) else '.') for c in range(W) ] for r in range(H) ]).reshape(H, W)
    print('%s' % '\n'.join(map(lambda row: ' '.join(map(str, row)), f)))
else:
    print("Z3 failed to find a solution.")
   
