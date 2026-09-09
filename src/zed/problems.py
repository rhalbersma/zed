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

# Puzzles I and II are played on one setup area alone, where bombs may go anywhere.
SETUP = Board(10, 4, frozenset(), ((span(0, 0, 9, 3), 40),))

# Classic Stratego with 6 bombs per setup area; the areas are derived from the lakes.
CLASSIC_BOMBS = with_setup(CLASSIC, 6)

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
