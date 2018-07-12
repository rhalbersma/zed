Z3-Python scripts to solve N-queens type puzzles on a Stratego board
====================================================================

[![License](https://img.shields.io/badge/license-Boost-blue.svg)](https://opensource.org/licenses/BSL-1.0)
[![](https://tokei.rs/b1/github/rhalbersma/zed)](https://github.com/rhalbersma/zed)

##### Bomb domination

Placing as few bombs as possible on a 4x10 board such that all 2x3 and 3x2 boxes have at least one bomb.
Minimum number of bombs satisfying the constraints == 6.

    . . . . . . . . . .
    . B . . B . . B . .
    . . B . . B . . B .
    . . . . . . . . . .

Placing as few bombs as possible on a 4x10 board such that all 1x6, 2x3 and 3x2 boxes have at least one bomb.
Minimum number of bombs satisfying the constraints == 7.

    . . . . B . . . . .
    . . B . . B . . B .
    . B . . . . . B . .
    . . . . B . . . . .

##### Scout domination

Placing as few scouts as possible on a 10x10 Stratego board such that they threaten every square.
Minimum number of scouts satisfying constraints == 8.

    . . . . . 2 . . . .
    . . . . . . . . 2 .
    2 . . . . . . . . .
    . . . . 2 . . . . .
    . . # # . . # # . .
    . . # # . . # # . .
    . . . . . . . . . 2
    . 2 . . . . . . . .
    . . . . . . . . . 2
    . . . . . . . . . 2

##### Scout independence

Placing as many scouts as possible on a 10x10 Stratego board such that they don't threaten each other.
Maximum number of scouts satisfying constraints == 14.

    . . . 2 . . . . . .
    . . 2 . . . . . . .
    . . . . . . 2 . . .
    . . . . . . . 2 . .
    2 . # # 2 . # # 2 .
    . 2 # # . 2 # # . 2
    . . . . . . 2 . . .
    . . . . . . . 2 . .
    . . . 2 . . . . . .
    . . 2 . . . . . . .

##### Scout cover

Maximum number of scout pairs on a 10x10 Stratego board such that scouts within pairs only threaten each other.
Z3 found a solution for 9 scout pairs:

    . . . 2 . . . 2 . .
    . 2 . . . . 2 . . .
    . . . . . . . . . 2
    . . 2 . . 2 . . . .
    . . # # 2 . # # 2 .
    2 . # # 2 . # # 2 .
    . . . . . . . . . 2
    2 . . . . . . . . .
    . . . . . . 2 2 . .
    . . 2 2 . . . . . .

Z3 failed to find a solution for 10 pairs.

##### Roadmap

- [ ] Add proper unit testing
- [ ] Add Travis CI badge
- [ ] Add CodeCov badge
- [x] Experiment with the largely undocumented Z3 Pseudo-Boolean solvers
- [ ] Attempt to solve the [bomb/scout placement puzzle](http://forum.stratego.com/topic/1134-stratego-quizz-and-training-forum/?p=11671) posted by user [The Prof](http://forum.stratego.com/user/572-the-prof/)

##### Acknowledgments

This repository was inspired by a series of puzzles posted on the [Stratego.com](http://forum.stratego.com/topic/1134-stratego-quizz-and-training-forum/) web forum by users [Napoleon 1er](http://forum.stratego.com/user/791-napoleon-1er/) and [maxroelofs](http://forum.stratego.com/user/489-maxroelofs/). Thanks to Wieger Wesselink for introducing me to the world of SMT solvers and for stimulating discussion.

License
-------

Copyright Rein Halbersma 2018.  
Distributed under the [Boost Software License, Version 1.0](http://www.boost.org/users/license.html).  
(See accompanying file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
