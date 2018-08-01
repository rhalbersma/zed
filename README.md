Z3-Python scripts to solve N-queens type puzzles on a Stratego board
====================================================================

[![License](https://img.shields.io/badge/license-Boost-blue.svg)](https://opensource.org/licenses/BSL-1.0)
[![](https://tokei.rs/b1/github/rhalbersma/zed)](https://github.com/rhalbersma/zed)

##### Bomb domination

The minimum number of bombs on a Stratego setup area such that each 2x3 and 3x2 rectangle has at least one bomb.   
The minimum number of bombs satisfying the constraints == 6.   

    . . . . . . . . . .
    . B . . B . . B . .
    . . B . . B . . B .
    . . . . . . . . . .

The minimum number of bombs on a Stratego setup area such that each 2x3, 3x2 and 1x6 rectangle has at least one bomb.   
The minimum number of bombs satisfying the constraints == 7.   

    . . . . . B . . . .
    . B . . B . . B . .
    . . B . . . . . B .
    . . . . . B . . . .

##### Scout domination

The minimum number of scouts on a Stratego board such that each square is occupied or threatened by a scout.   
The minimum number of scouts satisfying the constraints == 8.   

    . 2 . . . . . . . .
    . . . . . 2 . . . .
    . 2 . . . . . . . .
    2 . . . . . . . . .
    . . # # . . # # . .
    . . # # . . # # . .
    . . . . . . . . . 2
    . . . . . . . . 2 .
    . 2 . . . . . . . .
    . . . . 2 . . . . .

##### Scout independence

The maximum number of scouts on a Stratego board such that no scout threatens another scout.   
The maximum number of scouts satisfying the constraints == 14.   

    . . . . . . . 2 . .
    . . . 2 . . . . . .
    . . 2 . . . . . . .
    . . . . . . 2 . . .
    2 . # # 2 . # # 2 .
    . 2 # # . 2 # # . 2
    . . . . . . 2 . . .
    . . 2 . . . . . . .
    . . . . . . . 2 . .
    . . . 2 . . . . . .

##### Scout cover

The maximum number of scouts on a Stratego board such that each scout threatens exactly one other scout.
The maximum number of scouts satisfying the constraints == 18.

    2 . . . . . . . . .
    . . . . . . . . . 2
    . . . 2 . . . 2 . .
    . . 2 . . . 2 . . .
    . 2 # # . . # # . 2
    2 . # # 2 2 # # 2 .
    . . . . . . . . 2 .
    . 2 . . . . . . . .
    . . . . . . 2 2 . .
    . . 2 2 . . . . . .

##### Scout independence in the presence of bombs

The maximum number of scouts on a Stratego board such that no scout threatens another scout.   
The maximum number of scouts satisfying the constraints == 14.   

    . . . . . . . 2 . .
    . . . 2 . . . . . .
    . . 2 . . . . . . .
    . . . . . . 2 . . .
    2 . # # 2 . # # 2 .
    . 2 # # . 2 # # . 2
    . . . . . . 2 . . .
    . . 2 . . . . . . .
    . . . . . . . 2 . .
    . . . 2 . . . . . .

##### Roadmap

- [ ] Add proper unit testing
- [ ] Add Travis CI badge
- [ ] Add CodeCov badge
- [x] Experiment with the Z3 Pseudo-Boolean solvers
- [x] Solve the [scout/bomb placement puzzle](http://forum.stratego.com/topic/1134-stratego-quizz-and-training-forum/?p=11671) posted by user [The Prof](http://forum.stratego.com/user/572-the-prof/)

##### Acknowledgments

This repository was inspired by a series of puzzles posted on the [Stratego.com](http://forum.stratego.com/topic/1134-stratego-quizz-and-training-forum/) web forum by users [Napoleon 1er](http://forum.stratego.com/user/791-napoleon-1er/) and [maxroelofs](http://forum.stratego.com/user/489-maxroelofs/). Thanks to [Wieger Wesselink](http://www.win.tue.nl/~wieger/) for introducing me to the world of SMT solvers, and for stimulating discussion. Wieger Wesselink and [Hans Zantema](https://www.win.tue.nl/~hzantema/) were the first to solve the mixed scout/bomb independence problem.

License
-------

Copyright Rein Halbersma 2018.  
Distributed under the [Boost Software License, Version 1.0](http://www.boost.org/users/license.html).  
(See accompanying file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
