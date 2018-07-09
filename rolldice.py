import random
import regex

class DiceGroupException(Exception): #Exception for when dice group is malformed, ie '12d6>7!'
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

class DiceOperatorException(Exception): #Exception for when incorrect or malformed operators are used between dice, ie '3d4 + -200'
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

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
    splits = list((m.start(), m.end()) for m in regex.finditer(pattern, string))
    starts = [0] + [i[1] for i in splits]
    ends = [i[0] for i in splits] + [len(string)]
    return [string[start:end] for start, end in zip(starts, ends)]

#Rolls a group of dice in 2d6, 3d10, etc. format and returns an array of the results.
def roll_group(group):
    group = regex.match(r'^(\d*)d(\d+)$', group)
    num_of_dice = int(group[1]) if group[1] != '' else 1
    type_of_dice = int(group[2])
    assert num_of_dice > 0
    assert type_of_dice in [2,3,4,6,8,10,12,20,100]
    
    result = []
    for i in range(num_of_dice):
        result.append(random.randint(1, type_of_dice))
    return result

def num_equal(result, operator, comparator):
    if operator == '<':
        return len([x for x in result if x < comparator])
    elif operator == '>':
        return len([x for x in result if x > comparator])
    elif operator == '=':
        return len([x for x in result if x == comparator])
    else:
        raise ValueError

def roll_dice(roll):
    roll = ''.join(roll.split())
    roll = zero_width_split(r'((?<=[\+*-])(?=[^\+*-]))|((?<=[^\+*-])(?=[\+*-]))', roll) #Split the string on the boundary between +-* characters and every other character'

    string = []
    
    roll_groups, ops = unzip(roll)
    
    try:
        assert len(roll_groups) == len(ops) + 1
    except:
        raise DiceOperatorException('Too many terms in the dice roll.')
    results = []

    for group in roll_groups:
        try:
            explode = regex.match(r'^((\d*)d(\d+))!$', group) #Regex for exploding dice, ie. 2d10!, 4d100!, d12!, etc.

            specplode = regex.match(r'^((\d*)d(\d+))!(\d+)$', group) #Regex for exploding dice on specific number, ie. d20!10 or d12!4

            complode = regex.match(r'^((\d*)d(\d+))!([<>])(\d+)$', group) #Regex for exploding dice with a comparison, ie. d20!>10, d6!<2

            penetrate = regex.match(r'^((\d*)d(\d+))!p$', group) #Penetrating dice are the same as exploding except any dice after the initial number are added with a -1 penalty

            specpen = regex.match(r'^((\d*)d(\d+))!p(\d+)$', group) #See above

            compen = regex.match(r'^((\d*)d(\d+))!p([<>])(\d+)$', group) #See above

            comparison = regex.match(r'^((?:\d*)d(\d+))([<>])(\d+)$', group) #Regex for dice with comparison, ie. 2d10>4, 5d3<2, etc.

            compfail = regex.match(r'^((?:\d*)d(\d+))(?|((<)(\d+)f(>)(\d+))|((>)(\d+)f(<)(\d+)))$', group) #Regex for dice with success comparison and failure comparison.

            keep = regex.match(r'^((?:\d*)d\d+)([Kk])(\d*)$', group) #Regex for keeping a number of dice, ie. 2d10K, 2d10k3, etc.

            drop = regex.match(r'^((?:\d*)d\d+)([Xx])(\d*)$', group) #As above but with dropping dice and X
            
            normal = regex.match(r'^((\d*)d(\d+))$', group) #Regex for normal dice rolls

            literal = regex.match(r'^(\d+)$', group) #Regex for number literals. Note that preceding negative signs are not used, simply subtract
            
            if explode != None: #Handle exploding dice without a comparison modifier. 
                type_of_dice = int(explode[3])
                assert type_of_dice in [2,3,4,6,8,10,12,20,100]
                
                result = []
                last_result = roll_group(explode[1])
                result.extend(last_result)
                number_to_roll = num_equal(last_result, '=', type_of_dice)
                while number_to_roll != 0:
                    last_result = roll_group(str(number_to_roll) + 'd' + str(type_of_dice))
                    result.extend(last_result)
                    number_to_roll = num_equal(last_result, '=', type_of_dice)
                
                results.append(sum(result))
                roll = ','.join([('!' + str(i) if i == type_of_dice else str(i)) for i in result]) #Build a string of the dice rolls, adding an exclamation mark
                                                                                                   #before every roll that resulted in an explosion.

            elif specplode != None: #Handle exploding dice without a comparison modifier. 
                type_of_dice = int(specplode[3])
                assert type_of_dice in [2,3,4,6,8,10,12,20,100]

                comparator = int(specplode[4])

                assert comparator > 0 and comparator <= type_of_dice
                
                result = []
                last_result = roll_group(specplode[1])
                result.extend(last_result)
                number_to_roll = num_equal(last_result, '=', comparator)
                while number_to_roll != 0:
                    last_result = roll_group(str(number_to_roll) + 'd' + str(type_of_dice))
                    result.extend(last_result)
                    number_to_roll = num_equal(last_result, '=', comparator)
                
                results.append(sum(result))
                roll = ','.join([('!' + str(i) if i == comparator else str(i)) for i in result]) #Build a string of the dice rolls, adding an exclamation mark
                                                                                                   #before every roll that resulted in an explosion.

            elif complode != None: #Handle exploding dice with a comparison modifier
                type_of_dice = int(complode[3])
                assert type_of_dice in [2,3,4,6,8,10,12,20,100]

                comparator = int(complode[5])

                if complode[4] == '>': #Ensure comparison is within bounds
                    assert comparator > 0 and comparator < type_of_dice
                else:
                    assert comparator > 1 and comparator <= type_of_dice
                
                result = []
                last_result = roll_group(complode[1])
                result.extend(last_result)
                if complode[4] == '>':
                    number_to_roll = num_equal(last_result, '>', comparator)
                    while number_to_roll != 0:
                        last_result = roll_group(str(number_to_roll) + 'd' + str(type_of_dice))
                        result.extend(last_result)
                        number_to_roll = num_equal(last_result, '>', comparator)
                    roll = ','.join([('!' + str(i) if i > comparator else str(i)) for i in result])#Same as on other explodes except with a > or < comparison
                    
                else:
                    number_to_roll = num_equal(last_result, '<', comparator)
                    while number_to_roll != 0:
                        last_result = roll_group(str(number_to_roll) + 'd' + str(type_of_dice))
                        result.extend(last_result)
                        number_to_roll = num_equal(last_result, '<', comparator)
                    roll = ','.join([('!' + str(i) if i < comparator else str(i)) for i in result])#Same as on other explodes except with a > or < comparison

                results.append(sum(result))

            elif penetrate != None: #Handle penetrating dice without a comparison modifier. 
                type_of_dice = int(penetrate[3])
                assert type_of_dice in [2,3,4,6,8,10,12,20,100]

                first_num = int(penetrate[2])
                
                result = []
                last_result = roll_group(penetrate[1])
                result.extend(last_result)
                number_to_roll = num_equal(last_result, '=', type_of_dice)
                while number_to_roll != 0:
                    last_result = roll_group(str(number_to_roll) + 'd' + str(type_of_dice))
                    result.extend(last_result)
                    number_to_roll = num_equal(last_result, '=', type_of_dice)
                    
                pre_result = result[:first_num] #Add the first rolls with no modifier
                pre_result.extend([x - 1 for x in result[first_num:]]) #Add the second rolls with a -1 modifier
                
                results.append(sum(pre_result))
                
                roll = ','.join(['!' + str(i) if i == type_of_dice else str(i) for i in result[:first_num]]) #Add the first numbers, without the -1 but with a ! when roll is penetration
                roll += (',' if len(pre_result) > first_num else '') #Only add the comma in between if there's at least one penetration
                roll += ','.join([('!' + str(i) + '-1' if i == type_of_dice else str(i) + '-1') for i in result[first_num:]]) #Add the penetration dice with the '-1' tacked on the end

            elif specpen != None: #Handle penetrating dice without a comparison modifier. 
                type_of_dice = int(specpen[3])
                assert type_of_dice in [2,3,4,6,8,10,12,20,100]

                first_num = int(specpen[2])

                comparator = int(specpen[4])

                assert comparator > 0 and comparator <= type_of_dice
                
                result = []
                last_result = roll_group(specpen[1])
                result.extend(last_result)
                number_to_roll = num_equal(last_result, '=', comparator)
                while number_to_roll != 0:
                    last_result = roll_group(str(number_to_roll) + 'd' + str(type_of_dice))
                    result.extend(last_result)
                    number_to_roll = num_equal(last_result, '=', comparator)

                pre_result = result[:first_num] #Same as normal penetration
                pre_result.extend([x - 1 for x in result[first_num:]])
                
                results.append(sum(pre_result))
                
                roll = ','.join(['!' + str(i) if i == comparator else str(i) for i in result[:first_num]]) #Same as above
                roll += (',' if len(pre_result) > first_num else '') 
                roll += ','.join([('!' + str(i) + '-1' if i == comparator else str(i) + '-1') for i in result[first_num:]]) 

            elif compen != None: #Handle penetrating dice without a comparison modifier. 
                type_of_dice = int(compen[3])
                assert type_of_dice in [2,3,4,6,8,10,12,20,100]

                comparator = int(compen[5])

                first_num = int(compen[2])

                if compen[4] == '>': #Ensure comparison is within bounds
                    assert comparator > 0 and comparator < type_of_dice
                else:
                    assert comparator > 1 and comparator <= type_of_dice
                
                result = []
                last_result = roll_group(compen[1])
                result.extend(last_result)
                if compen[4] == '>':
                    number_to_roll = num_equal(last_result, '>', comparator)
                    while number_to_roll != 0:
                        last_result = roll_group(str(number_to_roll) + 'd' + str(type_of_dice))
                        result.extend(last_result)
                        number_to_roll = num_equal(last_result, '>', comparator)
    
                else:
                    number_to_roll = num_equal(last_result, '<', comparator)
                    while number_to_roll != 0:
                        last_result = roll_group(str(number_to_roll) + 'd' + str(type_of_dice))
                        result.extend(last_result)
                        number_to_roll = num_equal(last_result, '<', comparator)
                
                pre_result = result[:first_num]
                pre_result.extend([x - 1 for x in result[first_num:]])
                results.append(sum(pre_result))
                
                if compen[4] == '>':
                    roll = ','.join(['!' + str(i) if i > comparator else str(i) for i in result[:first_num]]) #Same as above
                    roll += (',' if len(pre_result) > first_num else '')
                    roll += ','.join([('!' + str(i) + '-1' if i > comparator else str(i) + '-1') for i in result[first_num:]])
                else:
                    roll = ','.join(['!' + str(i) if i < comparator else str(i) for i in result[:first_num]]) #Same as above
                    roll += (',' if len(pre_result) > first_num else '')
                    roll +=','.join([('!' + str(i) + '-1' if i < comparator else str(i) + '-1') for i in result[first_num:]])
                                
            elif comparison != None:
                group_result = roll_group(comparison[1])
                result = []
                result_string = []

                type_of_dice = int(comparison[2])
                
                comparator = int(comparison[4])
                
                if comparison[3] == '>': #Ensure comparison is within bounds
                    assert comparator > 0 and comparator < type_of_dice
                else:
                    assert comparator > 1 and comparator <= type_of_dice
                
                for die in group_result:
                    if comparison[3] == '>':
                        result.append(1 if die > comparator else 0)
                        result_string.append('!' + str(die) if die > comparator else str(die))
                    else:
                        result.append(1 if die < comparator else 0)
                        result_string.append('!' + str(die) if die < comparator else str(die))
                        
                results.append(sum(result))
                roll = ','.join(result_string) #Craft the string, adding an exclamation mark before every string that passed the comparison.
                    
            elif compfail != None:
                group_result = roll_group(compfail[1])

                result = []
                result_string = []

                type_of_dice = int(compfail[2])
                success_comp = int(compfail[5])
                fail_comp = int(compfail[7])

                #Ensure both comparisons are within bounds
                if compfail[4] == '>':
                    assert success_comp > 0 and success_comp < type_of_dice
                    assert fail_comp > 1 and fail_comp <= type_of_dice
                else:
                    assert success_comp > 1 and success_comp <= type_of_dice
                    assert fail_comp > 0 and fail_comp < type_of_dice

                for die in group_result:
                    if compfail[4] == '>': #Get the actual list of successes and fails with both comparisons
                        if die > success_comp:
                            result.append(1)
                            result_string.append('!' + str(die))
                        elif die < fail_comp:
                            result.append(-1)
                            result_string.append('*' + str(die))
                        else:
                            result.append(0)
                            result_string.append(str(die))
                    else:
                        if die < success_comp:
                            result.append(1)
                            result_string.append('!' + str(die))
                        elif die > fail_comp:
                            result.append(-1)
                            result_string.append('*' + str(die))
                        else:
                            result.append(0)
                            result_string.append(str(die))
                            
                results.append(sum(result)) #
                roll = ','.join(result_string)

            elif keep != None: #Handle rolling dice and keeping the x highest or lowest values
                group_result = roll_group(keep[1])
                group_result.sort(reverse=True if keep[2] == 'K' else False) #Uppercase is keep highest and lowercase is keep lowest.

                num_to_keep = int(keep[3] if keep[3] != '' else 1)
                assert num_to_keep < len(group_result) and num_to_keep >= 1
                
                results.append(sum(group_result[:num_to_keep]))
                roll = ','.join([str(i) for i in group_result[:num_to_keep]]) + ' ~~ ' #This time format the string with all kept rolls on the left and dropped rolls on the right
                roll += ','.join([str(i) for i in group_result[num_to_keep:]]) 
            
            elif drop != None:
                group_result = roll_group(drop[1])
                group_result.sort(reverse=True if drop[2] == 'X' else False) #Same thing as keep dice

                num_to_drop = int(drop[3] if drop[3] != '' else 1)
                assert num_to_drop < len(group_result) and num_to_drop >= 1
                               
                results.append(sum(group_result[:num_to_drop]))
                roll = ','.join([str(i) for i in group_result[num_to_drop:]]) + ' ~~ '  #Same as above.
                roll += ','.join([str(i) for i in group_result[:num_to_drop]])
                
            elif normal != None: 
                group_result = roll_group(group)
                results.append(sum(group_result))
                roll = ','.join([str(i) for i in group_result])

            elif literal != None:
                results.append(int(literal[1])) #Just append the integer value
                roll = literal[1]
            
            else:
                raise Exception
            
        except:
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
            raise DiceOperatorException('Invalid operator. Please only use +, -, and *')
        
    explanation = join_on_list(ops, string) #Re-add in the operators.

    return (sum_of_dice, explanation)
    
