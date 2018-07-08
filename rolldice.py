import random
import re

class DiceGroupException(Exception): #Exception for when dice group is malformed, ie '12d6>7!'
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

class DiceOperatorException(Exception): #Exception for when incorrect or malformed operators are used between dice, ie '3d4 + -200'
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

#Self explanatory
def unzip(seq):
    return (seq[::2], seq[1::2])

#Joins a list of contents on a list of separators, with spaces in between.
def join_on_list(separators, contents):
    string = list(contents[0])
    for i, content in enumerate(contents[1:]):
        string.extend(list(' %s %s' % (separators[i], content)))
    return ''.join(string)

#Allows splitting on a regex that matches zero-width or empty strings.
def zero_width_split(pattern, string):
    splits = list((m.start(), m.end()) for m in re.finditer(pattern, string))
    starts = [0] + [i[1] for i in splits]
    ends = [i[0] for i in splits] + [len(string)]
    return [string[start:end] for start, end in zip(starts, ends)]

#Rolls a group of dice in 2d6, 3d10, etc. format and returns an array of the results.
def dice_group(group):
    group = re.match(r'^(\d+)d(\d+)$', group)
    num_of_dice = int(group[1])
    type_of_dice = int(group[2])
    assert num_of_dice > 0
    assert type_of_dice in [2,3,4,6,8,10,12,20,100]
    
    result = []
    for i in range(num_of_dice):
        result.append(random.randint(1, type_of_dice))
    return result
    
def roll_dice(roll):
    roll = ''.join(roll.split())
    roll = zero_width_split(r'((?<=[\+*-])(?=[^\+*-]))|((?<=[^\+*-])(?=[\+*-]))', roll) #Split the string on the boundary between +-* characters and every other character

    string = []
    
    dice_groups, ops = unzip(roll)
    assert len(dice_groups) == len(ops) + 1
    results = []

    for group in dice_groups:
        explode = re.match(r'^d(\d+)!$', group) #Regex for exploding dice, ie. d10!, d100!, d12!, etc.
        
        comparison = re.match(r'^(\d+d(\d+))([<>])(\d+)$', group) #Regex for dice with comparison, ie. 2d10>4, 5d3<2, etc.

        complode = re.match(r'^d(\d+)!([<>])(\d+)$', group) #Regex for exploding dice with a comparison, ie. d20!>10, d6!<2

        keep = re.match(r'^(\d+d\d+)([Kk])(\d*)$', group) #Regex for keeping a number of dice, ie. 2d10K, 2d10k3, etc.

        drop = re.match(r'^(\d+d\d+)([Xx])(\d*)$', group) #As above but with dropping dice and X
        
        normal = re.match(r'^(\d+d\d+)$', group) #Regex for normal dice rolls

        literal = re.match(r'^(\d+)$', group) #Regex for number literals. Note that preceding negative signs are not used, simply subtract.
        
        if explode != None: #Handle exploding dice without a comparison modifier. 
            type_of_dice = int(explode[1])
            assert type_of_dice in [2,3,4,6,8,10,12,20,100]
            
            result = []
            result.append(random.randint(1, type_of_dice))
            while result[-1] == type_of_dice: #Roll the dice
                result.append(random.randint(1, type_of_dice))
            results.append(sum(result))

            roll = ','.join([('!' + str(i) if i == type_of_dice else str(i)) for i in result]) #Build a string of the dice rolls, adding an exclamation mark
                                                                                               #before every roll that resulted in an explosion.

        elif complode != None and complode[2] == '>': #Handle exploding dice with a comparison modifier
            type_of_dice = int(complode[1])
            assert type_of_dice in [2,3,4,6,8,10,12,20,100]

            comparator = int(complode[3])

            more_than = True if complode[2] == '>' else False

            #Ensure that the comparator is within bounds.
            if more_than:
                assert comparator > 0 and comparator < type_of_dice
            else:
                assert comparator > 1 and comparator <= type_of_dice  

            result = []
            result.append(random.randint(1, type_of_dice))
            if more_than: #Roll the dice
                while result[-1] > comparator:
                    result.append(random.randint(1, type_of_dice)) 
            else:
                while result[-1] < comparator:
                    result.append(random.randint(1, type_of_dice))

            results.append(sum(result))
            
            roll = ','.join([('!' + str(i) if i > comparator else str(i)) for i in result]) if more_than else ','.join([('!' + str(i) if i < comparator else str(i)) for i in result]) #Same as on normal explode except including a ternary                                                                                                                                                                            #whether it's more than or less than.


        elif keep != None: #Handle rolling dice and keeping the x highest or lowest values
            group_result = dice_group(keep[1])
            group_result.sort(reverse=True if keep[2] == 'K' else False) #Uppercase is keep highest and lowercase is keep lowest.

            num_to_keep = int(keep[3] if keep[3] != '' else 1)
            assert num_to_keep < len(group_result) and num_to_keep >= 1
            
            results.append(sum(group_result[:num_to_keep]))
            roll = ','.join([str(i) for i in group_result[:num_to_keep]]) + ' ~~ ' + ','.join([str(i) for i in group_result[num_to_keep:]]) #This time format the string with all kept rolls on the left and dropped rolls on the right
        
        elif drop != None:
            group_result = dice_group(drop[1])
            group_result.sort(reverse=True if drop[2] == 'X' else False) #Same thing as keep dice

            num_to_drop = int(drop[3] if drop[3] != '' else 1)
            assert num_to_drop < len(group_result) and num_to_drop >= 1
                           
            results.append(sum(group_result[:num_to_drop]))
            roll = ','.join([str(i) for i in group_result[num_to_drop:]]) + ' ~~ ' + ','.join([str(i) for i in group_result[:num_to_drop]]) #Same as above.
            
        elif comparison != None:
            group_result = dice_group(comparison[1])
            if comparison[3] == '>':
                results.append(sum(list(map(lambda x: 1 if (x > int(comparison[4])) else 0, group_result)))) #Check every one of the returned dice values to see if they're over the given term and sum.
                roll = ','.join([('!' + str(i) if (i > int(comparison[4])) else str(i)) for i in group_result]) #Craft the string, adding an exclamation mark before every string that passed the comparison.
            else:
                results.append(sum(list(map(lambda x: 1 if (x < int(comparison[4])) else 0, group_result)))) #Check every one of the returned dice values to see if they're under the given term and sum.
                roll = ','.join([('!' + str(i) if (i < int(comparison[4])) else str(i)) for i in group_result]) #Craft the string, adding an exclamation mark before every string that passed the comparison.
            
        elif normal != None: 
            group_result = dice_group(group)
            results.append(sum(group_result))
            roll = ','.join([str(i) for i in group_result])

        elif literal != None:
            results.append(int(literal[1])) #Just append the integer value
            
        else:
            raise DiceGroupException('"%s" is not a valid dicegroup.' % group)

        string.append('(%s)' % roll)

    sum_of_dice = results[0] #Start the sum by taking the first term as positive
    for i, result in enumerate(results[1:]): #For each term after that, add, subtract, or multiply depending on what the operator is
        if ops[i] == '+':
            sum_of_dice += result
        elif ops[i] == '-':
            sum_of_dice -= result
        elif ops[i] == '*':
            sum_of_dice *= result
        else:
            raise DiceOperatorException('"%s" is not a valid operator. Please use only +, -, and *' % ops[i])
        
    explanation = join_on_list(ops, string) #Re-add in the operators.

    return (sum_of_dice, explanation)
    
