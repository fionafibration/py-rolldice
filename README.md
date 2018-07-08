# py-dice-roll
A python module for parsing string representation of D&amp;D dice and rolling said dice.

## Usage:
```
import rolldice
rolldice.roll_dice('12d6 + 10')
```
That's it. The function will return a tuple containing the numerical result and a constructed representation string, in that order.

## Dice Syntax:

Dice syntax is loosely based on [CritDice](https://www.critdice.com/roll-advanced-dice/) syntax.  
#### Basic syntax:
```
4d10 + 17: Roll a 10-sided die 4 times and add 17 to the result
2d20 - 3: Roll a 20 sided die 2 times and subtract 3
1d4 * 3: Roll a 4 sided die once and multiply by 3
```
You get the idea. Spaces are optional and can actually be inserted anywhere in the rolls. `1 5 d 2 0 + 3 5` actually works.

#### Advanced syntax:

###### Keep Highest (K):
Used to (K)eep the highest roll. Can be followed by a number to keep that number of dice or by nothing to indicate keeping only one.
```
4d10K: Roll 4d10 and keep only the highest roll
7d12K3: Roll 7d12 and keep the highest three rolls
7d12K3 + 4: Roll as above then add 4
```

###### Keep Lowest (k):
Same as above but keeping the lowest.
```
3d3k: Roll 3d3 and keep the lowest roll
100d6k99: Roll 100d6 and keep all but the highest.
2d20k: Roll 2d20 and keep the lowest. This is a disadvantage roll in 5e
```

##### Drop Highest (X):
Used to drop the highest roll. Can be followed by a number to drop that number of dice or by nothing to indicate dropping just one.
```
6d8X: Roll 6d8 and drop the lowest
5d10X3 Roll 5d10 and drop the highest 3
```

##### Drop Lowest (x):
You get the idea.

##### Exploding Dice (!):
Exploding dice is usually known as 'Rule of 6' or 'Rule of 10,' as it is in Shadowrun. As long as the roll passes the specified comparison, another dice is rolled and added to the total. This process repeats until a number that does not match the comparison is rolled.
```
d20!: Roll a d20 and explode every time a 20 is rolled
d6! Roll a d6 and explode every time a 6 is rolled
d20!>10: Roll a d20 and explode every time a number higher than 10 is rolled
d12!<2: Roll a d12 and explode every time a 1 is rolled.
```

##### Count Successes (> or <):
Counts the number of rolls above or below a certain value.
```
4d20>19: Rolls 4d20 and counts the number of rolls above 19
10d12<3: Rolls 10d12 and counts the number of rolls below 3
```
  
That's all there is to it!

## Planned features:
- [ ] Allow for exploding on specific numbers instead of just comparisons
- [ ] Count failures as in CritDice syntax
- [ ] Penetrating dice
- [ ] Rerolling once or arbitrary number of times on a given condition
- [ ] Count successes not only as comparisons but on specific numbers 
