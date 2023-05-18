# py-rolldice
A python module for parsing string representation (aka Dice Notation) of dice rolls and rolling said dice.

## Usage:
Usage is very simple. Simply install py-rolldice with:
```
python -m pip install py-rolldice
```
 Then import it as usual and run the roll_dice function:
```
import rolldice
result, explanation = rolldice.roll_dice('12d6 + 10')
```
That's it. The function takes the string representation of your dice roll and will return a tuple containing the numerical result and a constructed representation string, in that order.
#### Functions and Floats:
By default the dice roller will parse floats and a limited set of function calls. This can be disabled if you want:
```
roll_dice('abs(-2)') # Will work
roll_dice('abs(-2)', functions=False) # Won't work

roll_dice('3 / 2') # Division will return a float
roll_dice('3 / 2', floats=False) # Division will be floor division

roll_dice('4.5') # Will work
roll_dice('4.5', floats=False) # Won't work
```
These also work on the DiceBag class.
## Dice Syntax:

Dice syntax is based on [CritDice](https://www.critdice.com/roll-advanced-dice/) syntax.  
#### Basic syntax:
```
4d10 + 17: Roll a 10-sided die 4 times and add 17 to the result
2d20 - 3: Roll a 20 sided die 2 times and subtract 3
1d4 * 3: Roll a 4 sided die once and multiply by 3
d4 * 3: Same as above, leaving out the number of dice will default to 1
5d6 / 3: Roll 5d6 and divide by 3
5d6 // 3: Same as above but floor division
2d10 ** 1d20: Roll 2d10 and exponentiate to the power of 1d20. Completely useless. Please never do this.
1d6 ** 1d6 ** 1d6 ** 1d6: OH GOD PLEASE NO
```
You get the idea. Spaces are optional and can actually be inserted anywhere in the rolls. `1 5 d 2 0 + 3 5` actually works. Operators follow PEMDAS. e.g: 
```
roll_dice('2*3+5') # Will return 11, following PEMDAS
roll_dice('2*(3+5)') # Will return 16, using parentheses precedence
```
Dice rolling also supports some functions, for no reason other than because I can.
```
abs(2d6-7): Absolute value of 2d6-7
gcd(2d6, 2d6): GCD of 2d6 and 2d6
lcm(7, 4d20): LCM of 7 and 4d20
floor(2d6 / 2): Floor of 2d6 / 2
ceil(2d6 / 2): Ceiling of 2d6 / 2
prime(2d6): 1 if 2d6 is prime else 0
max(2d6, ... ,3d4): returns biggest result
min(2d6, ... ,3d4): returns smallest result
```
Other functions may be added.
##### Note about exponentiation:
I have made a check to attempt to protect your soft, fragile CPUs from the menace of the pow() function, but you still have to be careful.
Exponentiation is right-associative, because math.
#### Advanced syntax:
##### Keep Highest (K):
Used to (K)eep the highest roll. Can be followed by a number to keep that number of dice or by nothing to indicate keeping only one.
```
4d10K: Roll 4d10 and keep only the highest roll
7d12K3: Roll 7d12 and keep the highest three rolls
7d12K3 + 4: Roll as above then add 4
```

##### Keep Lowest (k):
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
2d20!: Roll 2d20 and explode every time a 20 is rolled
7d20!3: Roll 7d20 and explode every time a 3 is rolled
4d6! Roll 4d6 and explode every time a 6 is rolled
d20!>10: Roll a d20 and explode every time a number higher than 10 is rolled
3d12!<2: Roll 3d12 and explode every time a 1 is rolled.
```

##### Count Successes (> or <):
Counts the number of rolls above or below a certain value.
```
4d20>19: Rolls 4d20 and counts the number of rolls above 19
10d12<3: Rolls 10d12 and counts the number of rolls below 3
```

##### Count failures (f):
Addition to counting successes to specify an additional 'failure' condition. Each failure will decrease the score by 1 while each success will still increase by 1.
```
10d10>6f<3: Roll 10d10 and count successes over 6 and failures under 3
4d20<5f>19: Roll 4d20 and count successes under 5 and failures over 19
5d100<5f>3: Invalid, you cannot have your failure and success comparison both be more than or less than.
```

##### Penetrating Dice (!p):
Penetrating dice are the same as exploding dice except all rolls from explosions are added with a -1 modifier.
```
2d20!: Roll 2d20 and penetrate every time a 20 is rolled
7d20!3: Roll 7d20 and penetrate every time a 3 is rolled
4d6! Roll 4d6 and penetrate every time a 6 is rolled
d20!>10: Roll a d20 and penetrate every time a number higher than 10 is rolled
3d12!<2: Roll 3d12 and penetrate every time a 1 is rolled.
```

##### Individual modifiers (a, s, m):
Add, subtract, or multiply each individual dice roll.
```
2d20a3: Add three to each roll
4d12s4: Subtract four from each roll
6d4m3: Multiply each roll by 3
```

##### Reroll on number (R or r):
Reroll on 1, a specific number, or a comparison. R to reroll until condition is not met and r to reroll just once.
```
4d20R: Reroll until there are no ones
5d6r6: Reroll once on a 6
7d12R>4: Reroll until there are no numbers above 4
``` 

## Dicebag Class:

The dicebag class provides an easy way to store a certain roll and reroll it. 
Usage:
```
from rolldice import *
dicebag = DiceBag() #Initializes with a roll of '0'
# OR
dicebag = DiceBag('12d6 + 2d20K') #Initializes with a roll of '12d6 + 2d20K'

result, explanation = dicebag.roll_dice() #Repeat as needed

# The last roll is also stored in dicebag.lastroll
assert result = dicebag.last_roll and explanation = dicebag.last_explanation
```
That's all there is to it!

## Planned features:
- [X] Allow for exploding on specific numbers instead of just comparisons
- [X] Count failures as in CritDice syntax
- [X] Penetrating dice
- [X] DiceBag object for repeating dice rolls and storing as an object.
- [X] Rerolling once or arbitrary number of times on a given condition
- [X] Parse PEMDAS properly
- [X] Safe mathematical parser
- [X] Even better AST parser supporting all the goodies
## Suggestions
If you have any other ideas for features, just make a suggestion and I'll see what I can do!
