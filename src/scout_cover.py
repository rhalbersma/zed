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
num_scout_pairs = Int('k')
lakes_are_forbidden = [ Not(scout[r][c]) for r in range(4, 6) for c in chain(range(2, 4), range(6, 8)) ]

# http://forum.stratego.com/topic/1134-stratego-quizz-and-training-forum/?p=11670

# Cache the row and column sum into variables.
num_scouts_per_open_row           = [ Sum([ If(scout[r][c], 1, 0) for c in range(W)    ]) for r in chain(range(0, 4), range(6, H)) ]
num_scouts_per_row_in_left_lane   = [ Sum([ If(scout[r][c], 1, 0) for c in range(0, 2) ]) for r in range(4, 6) ]
num_scouts_per_row_in_center_lane = [ Sum([ If(scout[r][c], 1, 0) for c in range(4, 6) ]) for r in range(4, 6) ]
num_scouts_per_row_in_right_lane  = [ Sum([ If(scout[r][c], 1, 0) for c in range(8, W) ]) for r in range(4, 6) ]
num_scouts_per_open_column        = [ Sum([ If(scout[r][c], 1, 0) for r in range(H)    ]) for c in chain(range(0, 2), range(4, 6), range(8, W)) ]
num_scouts_per_column_below_lakes = [ Sum([ If(scout[r][c], 1, 0) for r in range(0, 4) ]) for c in chain(range(2, 4), range(6, 8)) ]
num_scouts_per_column_above_lakes = [ Sum([ If(scout[r][c], 1, 0) for r in range(6, H) ]) for c in chain(range(2, 4), range(6, 8)) ]

# At most one scout pair (i.e. two scouts) per row or column.
at_most_two_per_open_row           = [ num_scouts_per_open_row[ir]           <= 2 for ir, _ in enumerate(chain(range(0, 4), range(6, H))) ]
at_most_two_per_row_in_left_lane   = [ num_scouts_per_row_in_left_lane[ir]   <= 2 for ir, _ in enumerate(range(4, 6)) ]
at_most_two_per_row_in_center_lane = [ num_scouts_per_row_in_center_lane[ir] <= 2 for ir, _ in enumerate(range(4, 6)) ]
at_most_two_per_row_in_right_lane  = [ num_scouts_per_row_in_right_lane[ir]  <= 2 for ir, _ in enumerate(range(4, 6)) ]
at_most_two_per_open_column        = [ num_scouts_per_open_column[ic]        <= 2 for ic, _ in enumerate(chain(range(0, 2), range(4, 6), range(8, W))) ]
at_most_two_per_column_below_lakes = [ num_scouts_per_column_below_lakes[ic] <= 2 for ic, _ in enumerate(chain(range(2, 4), range(6, 8))) ]
at_most_two_per_column_above_lakes = [ num_scouts_per_column_above_lakes[ic] <= 2 for ic, _ in enumerate(chain(range(2, 4), range(6, 8))) ]

# For each square with a scout, there is another scout in either the same row or the same column.
# We express these constraints in terms of the already computed row and column sums.
# Or(And(x == 2, y == 1), And(x == 1, y == 2)) is about 4x faster than x + y == 3 (which has to rely on 0 <= x <= 2 and 0 <= y <= 2 for integer x, y).

open_rows_cols = [ 
    Implies(
        scout[r][c], 
        Or(
            And(num_scouts_per_open_row[ir] == 2, num_scouts_per_open_column[ic] == 1),
            And(num_scouts_per_open_row[ir] == 1, num_scouts_per_open_column[ic] == 2)
        )
    ) 
    for ir, r in enumerate(chain(range(0, 4), range(6, H)))
    for ic, c in enumerate(chain(range(0, 2), range(4, 6), range(8, W)))
]

below_lakes = [ 
    Implies(
        scout[r][c], 
        Or(
            And(num_scouts_per_open_row[ir + 0] == 2, num_scouts_per_column_below_lakes[ic] == 1),
            And(num_scouts_per_open_row[ir + 0] == 1, num_scouts_per_column_below_lakes[ic] == 2)
        ) 
    ) 
    for ir, r in enumerate(range(0, 4))
    for ic, c in enumerate(chain(range(2, 4), range(6, 8)))
]

above_lakes = [ 
    Implies(
        scout[r][c], 
        Or(
            And(num_scouts_per_open_row[ir + 4] == 2, num_scouts_per_column_above_lakes[ic] == 1),
            And(num_scouts_per_open_row[ir + 4] == 1, num_scouts_per_column_above_lakes[ic] == 2)
        )
    ) 
    for ir, r in enumerate(range(6, H))
    for ic, c in enumerate(chain(range(2, 4), range(6, 8)))
]

left_lane = [ 
    Implies(
        scout[r][c],
        Or( 
            And(num_scouts_per_row_in_left_lane[ir] == 2, num_scouts_per_open_column[ic + 0] == 1),
            And(num_scouts_per_row_in_left_lane[ir] == 1, num_scouts_per_open_column[ic + 0] == 2)
        )
    ) 
    for ir, r in enumerate(range(4, 6))
    for ic, c in enumerate(range(0, 2))
]

center_lane = [ 
    Implies(
        scout[r][c],
        Or( 
            And(num_scouts_per_row_in_center_lane[ir] == 2, num_scouts_per_open_column[ic + 2] == 1),
            And(num_scouts_per_row_in_center_lane[ir] == 1, num_scouts_per_open_column[ic + 2] == 2)
        )
    ) 
    for ir, r in enumerate(range(4, 6))
    for ic, c in enumerate(range(4, 6))
]

right_lane = [ 
    Implies(
        scout[r][c], 
        Or(
            And(num_scouts_per_row_in_right_lane[ir] == 2, num_scouts_per_open_column[ic + 4] == 1),
            And(num_scouts_per_row_in_right_lane[ir] == 1, num_scouts_per_open_column[ic + 4] == 2)
        )
    ) 
    for ir, r in enumerate(range(4, 6))
    for ic, c in enumerate(range(8, W))
]

def search_solution(N):
    problem = Solver()

    problem.add(num_scouts == 2 * num_scout_pairs)
    problem.add(lakes_are_forbidden)

    # one constraints per row or column
    problem.add(at_most_two_per_open_row)
    problem.add(at_most_two_per_open_column)
    problem.add(at_most_two_per_column_below_lakes)
    problem.add(at_most_two_per_column_above_lakes)
    problem.add(at_most_two_per_row_in_left_lane)
    problem.add(at_most_two_per_row_in_center_lane)
    problem.add(at_most_two_per_row_in_right_lane)

    # one constraint per square occupied by a scout
    problem.add(open_rows_cols)
    problem.add(below_lakes)
    problem.add(above_lakes)
    problem.add(left_lane)
    problem.add(center_lane)
    problem.add(right_lane)

    problem.add(num_scout_pairs == N)

    if problem.check() == sat:
        m = problem.model()
        print("Z3 found a solution for %s scout pairs:" % m.evaluate(num_scout_pairs))
        f = np.array([ [ '2' if m.evaluate(scout[r][c]) else ('#' if r in range(4, 6) and c in chain(range(2, 4), range(6, 8)) else '.') for c in range(W) ] for r in range(H) ]).reshape(H, W)
        print('%s' % '\n'.join(map(lambda row: ' '.join(map(str, row)), f)))
    else:
        print("Z3 failed to find a solution for %s scout pairs." % N)

print("Maximum number of scout pairs on a %sx%s Stratego board such that scouts within pairs only threaten each other." % (H, W))
# This problem is too large to be solved with Optimize().maximize(scout_pairs)
# Instead, we search for a solution with 9 scout pairs, and disproof a solution with 10 scout pairs
set_param(verbose = 1)
search_solution(9)
search_solution(10) # takes ~20 minutes
   
