Stratego armies
===============

The boards in `src/zed/problems.py` come with armies, and the armies turn out to
be more interesting than the boards. This note collects what can be checked about
them by counting. It is a side road off the [main README](../README.md); only the
last section touches the solver at all.

The five armies
---------------

| | Classic 40 | L'Attaque 36 | Travel 30 | pocket 24 | jijbent 24 |
|---|---|---|---|---|---|
| marshal    | 1 | 1 | 1 | 1 | 1 |
| general    | 1 | 1 | 1 | - | 1 |
| colonel    | 2 | 2 | 2 | 2 | 2 |
| major      | 3 | 2 | 3 | 3 | - |
| captain    | 4 | 4 | 3 | - | 3 |
| lieutenant | 4 | 4 | 2 | - | - |
| sergeant   | 4 | 4 | 2 | 4 | 3 |
| miner      | 5 | 4 | 4 | 4 | 3 |
| scout      | 8 | 8 | 5 | 4 | 5 |
| spy        | 1 | 1 | 1 | 1 | 1 |
| bomb       | 6 | 4 | 5 | 4 | 4 |
| flag       | 1 | 1 | 1 | 1 | 1 |

*Classic* and *L'Attaque* are the published games; the sizes follow from their
boards, since a setup area is always filled exactly. *Travel 30* is the 10x8
travel set. The two 24-piece armies both belong to an 8-wide board: *pocket 24*
is the set catalogued on the Stratego.com forum in March 2018, and *jijbent 24*
is the variant played on jijbent.nl and yourturnmyturn.com, attributed there to
Vincent de Boer. Sources at the end.

Test 1: the bomb margin
-----------------------

Classic has 5 miners and 6 bombs. If every miner trades itself for a bomb, one
bomb is still standing to wall in the flag, so **miners == bombs - 1** reads like
a deliberate rule rather than a coincidence.

    Classic 40     5 miners, 6 bombs    OK
    L'Attaque 36   4 miners, 4 bombs    one bomb short
    Travel 30      4 miners, 5 bombs    OK
    pocket 24      4 miners, 4 bombs    one bomb short
    jijbent 24     3 miners, 4 bombs    OK

This is the only test here that needs no reference army *and* no counting
argument -- it comes straight out of how the game ends.

Test 2: densities
-----------------

Since the setup area is filled exactly, an army's composition is a set of
densities: a bomb count is the fraction of your own setup area that is bombs.

    army                   bombs         miners         scouts
    Classic 40         6   15.0%      5   12.5%      8   20.0%
    L'Attaque 36       4   11.1%      4   11.1%      8   22.2%
    Travel 30          5   16.7%      4   13.3%      5   16.7%
    pocket 24          4   16.7%      4   16.7%      4   16.7%
    jijbent 24         4   16.7%      3   12.5%      5   20.8%

    deviation from the classic ratio, in pieces:
      L'Attaque 36  bombs -1.4   miners -0.5   scouts +0.8
      Travel 30     bombs +0.5   miners +0.2   scouts -1.0
      pocket 24     bombs +0.4   miners +1.0   scouts -0.8
      jijbent 24    bombs +0.4   miners +0.0   scouts +0.2

The jijbent army is a faithful scale-down: within half a piece on all three
counts, exactly on the ratio for miners. The pocket set is not scaled but flat --
4 sergeants, 4 miners, 4 scouts, 4 bombs -- which is why its three densities are
identical.

This test cannot say anything about the classic army, which supplies the
yardstick and scores zero by construction.

Test 3: pyramid and ladder
--------------------------

A force should be a pyramid -- never fewer of a rank than of the rank above it --
and ideally leave no gap in the ladder from marshal down to scout. Neither
property refers to a reference army.

    Classic 40    ladder complete   pyramid OK
    L'Attaque 36  ladder complete   pyramid OK
    Travel 30     ladder complete   pyramid breaks at lieutenant
    pocket 24     gaps: general, captain, lieutenant       pyramid OK
    jijbent 24    gaps: major, lieutenant                  pyramid OK

The travel set is the only army that breaks the pyramid: 2 lieutenants under 3
captains. And the rank the pocket set is missing is the general, which the next
test shows is the expensive one to lose.

The 24-piece gaps are a trade rather than an oversight. With flag, spy and 4
bombs fixed, 18 pieces remain for 9 ranks, and the cheapest gapless pyramid is
1-1-2-2-2-2-2-3-3. That satisfies the margin rule but leaves only 3 scouts,
12.5% against the classic 20%: at this size a complete ladder and a healthy
scout count cannot both be had. The jijbent army spends two cheap ranks, the
major and the lieutenant, and buys 5 scouts at 20.8%. The pocket set spends
three including the general and still ends up scout-poor at 16.7%, paying the
price without collecting the benefit.

Test 4: hunters
---------------

Count each rank's *hunters*: the enemy pieces that can take it, meaning
everything strictly above it, plus the spy in the marshal's case. A piece with a
single hunter can only be lost to an ambush, since its one predator is the last
thing it will ever attack.

    Classic 40    marshal 1   general 1   colonel 2      one-hunter pieces: 2  (1 marshal, 1 general)
    L'Attaque 36  marshal 1   general 1   colonel 2      one-hunter pieces: 2
    Travel 30     marshal 1   general 1   colonel 2      one-hunter pieces: 2
    jijbent 24    marshal 1   general 1   colonel 2      one-hunter pieces: 2
    pocket 24     marshal 1   colonel 1 (x2)             one-hunter pieces: 3  (1 marshal, 2 colonels)

Four of the five armies carry exactly two near-invulnerable pieces, and both are
unique. The pocket set carries three, and two of them are the same piece: you can
send one colonel hunting without risking the other, and the opponent cannot tell
them apart. Losing a general is losing it; losing a colonel leaves a spare.

This is what a general is for. Trading a sergeant for one is not about filling a
gap in the ladder as such, it is about putting a second hunter over the colonels,
taking them from one to two and the army from three one-hunter pieces back to the
usual two.

Repairs
-------

Every published army here is one or two swaps away from passing all four tests.

| army | defect | repair |
|---|---|---|
| L'Attaque 36 | 1.4 bombs short | scout -> bomb, giving 5 bombs, 4 miners, 7 scouts |
| pocket 24 | colonels duplicated and near-invulnerable; bomb margin | sergeant -> general, miner -> scout |
| Travel 30 | pyramid dip, one scout short | major -> scout, merge lieutenant and sergeant |

For L'Attaque, note that its miners are not in surplus but half a piece short, so
trading a miner for a scout does not repair it: that leaves the bombs untouched
and pushes both other counts further out, to -1.5 miners and +1.8 scouts. Only a
scout for a bomb fixes all three, at -0.4, -0.5 and -0.2. That is what removing 1
major, 1 miner, 1 bomb and 1 scout from classic gives, rather than the 1 major, 1
miner and 2 bombs actually removed.

For the pocket set, the two swaps land exactly on the jijbent army. The three
majors are the same three pieces under a different name, so nothing else changes.
The swaps are independent: miner-for-scout fixes the bomb margin and the scout
density, sergeant-for-general fixes the hunter count, and neither helps with the
other's problem.

For the travel set, a single swap is not enough. Its 10 removed pieces all came
out of the bottom and middle of the ladder -- 2 lieutenants, 2 sergeants, 3
scouts -- so lieutenants, sergeants and scouts are each a piece short while the
majors sit in surplus at +0.75. Trading a major for a scout puts the scouts
exactly on the classic ratio, but the lieutenant and sergeant deficits survive
any single move. Merging those two ranks into one rank of 4 repairs it: the
ladder becomes 1-1-2-2-3-4-4-6, a pyramid again, with scouts on the ratio, bombs
and miners inside half a piece and the margin rule intact.

Shrink the army, shorten the ladder
-----------------------------------

| army | ranks | pieces per rank |
|---|---|---|
| Classic 40 | 9 | 4.4 |
| Travel 30, repaired | 8 | 3.8 |
| jijbent 24 | 7 | 3.4 |
| pocket 24 | 6 | 4.0 |

The published travel set kept all nine ranks and could not fill them evenly,
which is where its pyramid dip came from. The pocket set went the other way,
cutting to six ranks when seven was right, and cutting the general.

Is the classic army well balanced?
----------------------------------

The density table cannot answer this, since classic defines its yardstick. Three
things that do not depend on it point the same way.

The margin rule is structural rather than a ratio, and classic satisfies it.

The jijbent army was designed independently, for a different board, and landed
within half a piece of the classic proportions on all three counts.

And *scout saturation* -- the real scout count over the maximum number of
mutually invisible scouts the board admits, which is puzzle VI's answer, so a
denominator classic has no say in -- puts classic and jijbent together and the
three criticised armies elsewhere:

    classic     8 / 24 = 33.3%      jijbent 24   5 / 16 = 31.2%
    l_attaque   8 / 20 = 40.0%      pocket 24    4 / 16 = 25.0%      travel  5 / 20 = 25.0%

That last one is the only place in this note where the solver does any work.

Sources
-------

The pocket set and the jijbent army both come from the *Morx Stratego Collection*
thread on the Stratego.com forum, March 2018, since taken offline. Morx
catalogued the set as three rows of eight; Master Mind gave its roster; Don_Homer
described the jijbent variant and attributed it to Vincent de Boer; Wogomite
observed that without a general the colonels are overpowered, which is Test 4
arrived at from play rather than from counting.

The classic and L'Attaque rosters are the published games. The travel roster is
the classic army less 1 captain, 2 lieutenants, 2 sergeants, 1 miner, 3 scouts
and 1 bomb.
