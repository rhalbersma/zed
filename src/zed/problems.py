#          Copyright Rein Halbersma 2018-2026.
# Distributed under the Boost Software License, Version 1.0.
#    (See accompanying file LICENSE_1_0.txt or copy at
#          http://www.boost.org/LICENSE_1_0.txt)

"""The six puzzles, and the Stratego boards they are played on.

Rectangles in params are (width, height) to match the board's W x H order: the
original "1x6" (one rank, six files) is (6, 1) here.
"""
from dataclasses import dataclass, field

from .board import Board, span, with_setup


@dataclass(frozen=True)
class Problem:
    name: str
    board: Board
    rule: str            # bomb_rect_cover | domination | independent | exactly_one
    sense: str           # 'min' or 'max'
    params: dict = field(default_factory=dict)
    expected: int = None


def lakes(*names):
    """Lake squares in algebraic notation, as in tabula's games/stratego.hpp."""
    return frozenset((ord(n[0]) - ord("a"), int(n[1:]) - 1) for n in names)


# The three boards defined in tabula/include/tabula/games/stratego.hpp.
L_ATTAQUE   = Board(9, 10, lakes("c6", "e6", "g6", "c5", "e5", "g5"))
CLASSIC     = Board(10, 10, lakes("c6", "d6", "g6", "h6", "c5", "d5", "g5", "h5"))
QUICK_ARENA = Board(8, 8, lakes("c5", "f5", "c4", "f4"))

# The 10x8 travel set: the classic board with two ranks taken out of the middle,
# and the two 2x2 lakes moved down with them.  Its army drops 1 captain, 2
# lieutenants, 2 sergeants, 1 miner, 3 scouts and 1 bomb from the classic 40, so
# 30 pieces fill a 10x3 setup area exactly, the way 40 fill the classic 10x4.
TRAVEL      = Board(10, 8, lakes("c5", "d5", "g5", "h5", "c4", "d4", "g4", "h4"))

# Puzzles I and II are played on one setup area alone, where bombs may go anywhere.
SETUP = Board(10, 4, frozenset(), ((span(0, 0, 9, 3), 40),))

# Bombs per setup area; the areas themselves are derived from the lake ranks.
# Classic has 6 bombs and 5 miners, travel 5 and 4: one spare bomb, so that a
# miner trading itself for each bomb still leaves the flag walled in.
#
# The rule holds across variants.  L'Attaque has 4 of each, one bomb short.  So
# does a 24-piece pocket set (three rows of eight, 4 bombs and 4 miners), while
# the 24-piece variant played on jijbent.nl -- one sergeant traded for a general
# and one miner for a scout, the majors merely renamed captains -- lands back on
# 3 miners to 4 bombs.  Quick Arena's
# own army is not recorded in tabula, which is why sweep.py varies the budget.
CLASSIC_BOMBS = with_setup(CLASSIC, 6)
TRAVEL_BOMBS  = with_setup(TRAVEL, 5)

CATALOG = [
    Problem("I   min bombs, 2x3 + 3x2",   SETUP, "bomb_rect_cover", "min",
            {"rectangles": [(3, 2), (2, 3)]}, 6),
    Problem("II  min bombs, + 1x6",       SETUP, "bomb_rect_cover", "min",
            {"rectangles": [(3, 2), (2, 3), (6, 1)]}, 7),
    Problem("III min scouts dominating",  CLASSIC, "domination",  "min", {}, 8),
    Problem("IV  max scouts independent", CLASSIC, "independent", "max", {}, 14),
    Problem("V   max scouts, 1 threat",   CLASSIC, "exactly_one", "max", {}, 18),
    Problem("VI  max scouts, 6 bombs",    CLASSIC_BOMBS, "independent", "max", {}, 24),
]
