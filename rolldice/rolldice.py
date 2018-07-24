#!/usr/bin/python
# encoding: utf-8

"""
py-dice-roll
Created by Finianb1
https://github.com/ThePlasmaRailgun/py-dice-roll/
Math parser thanks to DanTheDeckie on GitHub

https://github.com/danthedeckie/simpleeval
"""

import random
import ast
import regex
import operator
import math

class DiceGroupException(Exception):  # Exception for when dice group is malformed, ie '12d6>7!'
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class DiceOperatorException(Exception):  # Exception for when incorrect or malformed operators are used between dice
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


def gcd(a, b):
    """
    Computes GCD using Euclid's algorithm

    :param a: Number A
    :param b: Number B
    :return: gcd(a, b)
    """
    while b > 0:
        a, b = b, a % b
    return a


def lcm(a, b):
    """
    Computes LCM using GCD

    :param a: Number A
    :param b: Number B
    :return: lcm(a, b)
    """
    return a * b / gcd(a, b)


MAX_POWER = 40

def safe_power(a, b):
    """
    Same power of a ^ b
    :param a: Number a
    :param b: Number b
    :return: a ^ b
    """
    if abs(a) > MAX_POWER or abs(b) > MAX_POWER:
        raise ValueError('Number too high!')
    return a ** b


def rabin_miller(p):
    """
    Performs a rabin-miller primality test

    :param p: Number to test
    :return: Bool of whether num is prime
    """
    # From this stackoverflow answer: https://codegolf.stackexchange.com/questions/26739/super-speedy-totient-function
    if p < 2:
        return False
    if p != 2 and p % 2 == 0:
        return False
    s = p - 1
    while s % 2 == 0:
        s >>= 1
    for x in range(10):
        a = random.randrange(p - 1) + 1
        temp = s
        mod = pow(a, temp, p)
        while temp != p - 1 and mod != 1 and mod != p - 1:
            mod = (mod * mod) % p
            temp = temp * 2
        if mod != p - 1 and temp % 2 == 0:
            return False
    return True


DEFAULT_FUNCTIONS = {"abs": abs, 'gcd': gcd, 'lcm': lcm, 'ceil': math.ceil, 'floor': math.floor, 'prime': rabin_miller}

DEFAULT_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
               ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
               ast.Pow: safe_power, ast.Mod: operator.mod,
               ast.USub: operator.neg, ast.UAdd: operator.pos
               }

DEFAULT_OPS_NO_FLOAT = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
                        ast.Div: operator.floordiv,
                        ast.Pow: safe_power, ast.Mod: operator.mod,
                        ast.USub: operator.neg, ast.UAdd: operator.pos
                        }


class SimpleEval(object):
    expr = ""

    def __init__(self, *, functions=True, floats=True):
        """
        Initializes a SimpleEval object

        :param functions: Allow for parsing of function calls
        :param floats: Allow for parsing of floats, when set to division defaults to floordiv

        Parameters are currently not safe to change once initialized. Doing this will have no effect.
        """
        self.floats = floats

        if self.floats:
            self.operators = DEFAULT_OPS
        else:
            self.operators = DEFAULT_OPS_NO_FLOAT

        self.functions = DEFAULT_FUNCTIONS

        self.nodes = {
            ast.Num: self._eval_num,
            ast.UnaryOp: self._eval_unaryop,
            ast.BinOp: self._eval_binop,
        }

        if functions:
            self.nodes[ast.Call] = self._eval_call

    def eval(self, expr):
        """
        Evaluates an expression

        :param expr: Expression to evaluate
        :return: Result of expression
        """
        # set a copy of the expression aside, so we can give nice errors...

        self.expr = expr

        # and evaluate:
        return self._eval(ast.parse(expr.strip()).body[0].value)

    def _eval(self, node):
        """
        Evaluate a node

        :param node: Node to eval
        :return: Result of node
        """
        try:
            handler = self.nodes[type(node)]
        except KeyError:
            raise ValueError("Sorry, {0} is not available in this evaluator".format(type(node).__name__))

        return handler(node)

    def _eval_num(self, node):
        """
        Evaluate a numerical node

        :param node: Node to eval
        :return: Result of node
        """
        if self.floats:
            return node.n
        else:
            return int(node.n)

    def _eval_unaryop(self, node):
        """
        Evaluate a unary operator node (ie. -2, +3)
        Currently just supports positive and negative

        :param node: Node to eval
        :return: Result of node
        """
        return self.operators[type(node.op)](self._eval(node.operand))

    def _eval_binop(self, node):
        """
        Evaluate a binary operator node (ie. 2+3, 5*6, 3 ** 4)

        :param node: Node to eval
        :return: Result of node
        """
        return self.operators[type(node.op)](self._eval(node.left),
                                             self._eval(node.right))

    def _eval_call(self, node):
        """
        Evaluate a function call

        :param node: Node to eval
        :return: Result of node
        """
        try:
            func = self.functions[node.func.id]
        except KeyError:
            raise NameError(node.func.id)

        value = func(
            *(self._eval(a) for a in node.args),
            **dict(self._eval(k) for k in node.keywords)
        )

        if value is True:
            return 1
        elif value is False:
            return 0
        else:
            return value


class DiceBag:
    def __init__(self, roll='0', *, functions=True, floats=True):  # Initialize dicebag with a default roll of a 0 literal
        """
        Initializes dicebag.

        :param roll: Roll to initialize with or if no roll is supplied, '0'
        :param functions: Whether to allow function calls. Defaults to yes
        :param floats: Whether to allow for parsing floats. Defaults to yes. When set to false division will act as floor division
        :return: None
        """
        self._roll = None
        self._last_roll = None
        self._last_explanation = None
        self.floats = floats
        self.functions = functions

        self.roll = roll

    def roll_dice(self):  # Roll dice with current roll
        """
        Rolls dicebag and sets last_roll and last_explanation to roll results

        :return: Roll results.
        """
        roll = roll_dice(self.roll, floats=self.floats, functions=self.functions)

        self._last_roll = roll[0]
        self._last_explanation = roll[1]

        return self.last_roll, self.last_explanation

    def __call__(self):  # Allow for calling the object, same thing as self.roll_dice
        """
        Just call the roll_dice method.

        :return: Roll result
        """
        return self.roll_dice()

    @property
    def roll(self):  # Standard getter
        """
        Standard getter for roll

        :return: Roll
        """
        return self._roll

    @roll.setter
    def roll(self, value):
        """
        Setter for roll, verifies the roll is valid

        :param value: Roll
        :return: None
        """
        if type(value) != str:  # Make sure dice roll is a str
            raise TypeError('Dice roll must be a string in dice notation')
        try:
            roll_dice(value)  # Make sure dice roll parses as a valid roll and not an error
        except Exception as e:
            raise ValueError('Dice roll specified was not a valid diceroll.\n%s\n' % str(e))
        else:
            self._roll = value

    @property
    def last_roll(self):
        """
        Standard getter. Makes last_roll read-only.

        :return:
        """
        return self._last_roll

    @property
    def last_explanation(self):
        """
        Standard getter. Makes last_explanation read-only.

        :return:
        """
        return self._last_explanation


def zero_width_split(pattern, string):
    """
    Split a string on a regex that only matches zero-width strings

    :param pattern: Regex pattern that matches zero-width strings
    :param string: String to split on.
    :return: Split array
    """
    splits = list((m.start(), m.end()) for m in regex.finditer(pattern, string))
    starts = [0] + [i[1] for i in splits]
    ends = [i[0] for i in splits] + [len(string)]
    return [string[start:end] for start, end in zip(starts, ends)]


def roll_group(group):
    """
    Rolls a group of dice in 2d6, 3d10, d12, etc. format

    :param group: String of dice group
    :return: Array of results
    """
    group = regex.match(r'^(\d*)d(\d+)$', group, regex.IGNORECASE)
    num_of_dice = int(group[1]) if group[1] != '' else 1
    type_of_dice = int(group[2])
    assert num_of_dice > 0

    result = []
    for i in range(num_of_dice):
        result.append(random.randint(1, type_of_dice))
    return result


def num_equal(result, operator, comparator):
    """
    Returns the number of elements in a list that pass a comparison

    :param result: The list of results of a dice roll
    :param operator: Operator in string to perform comparison on:
        Either '+', '-', or '*'
    :param comparator: The value to compare
    :return:
    """
    if operator == '<':
        return len([x for x in result if x < comparator])
    elif operator == '>':
        return len([x for x in result if x > comparator])
    elif operator == '=':
        return len([x for x in result if x == comparator])
    else:
        raise ValueError


def roll_dice(roll, *, functions=True, floats=True):
    """
    Rolls dice in dice notation with advanced syntax used according to tinyurl.com/pydice

    :param roll: Roll in dice notation
    :return: Result of roll, and an explanation string
    """
    roll = ''.join(roll.split())
    roll = regex.sub(r'(?<=d)%', '100', roll, regex.IGNORECASE)
    roll = roll.replace('^', '**')
    roll = zero_width_split(r'((?<=[\(\),%^\/+*-])(?=.))|((?<=.)(?=[\(\),%^\/+*-]))', roll)  # Split the string on the boundary between operators and other chars

    string = []

    results = []

    for group in roll:
        if group in '()/=<>,%^+*-' or group in DEFAULT_FUNCTIONS: #Append operators without modification
            results.append(group)
            string.append(group)
            continue
        try:
            explode = regex.match(r'^((\d*)d(\d+))!$', group, regex.IGNORECASE)  # Regex for exploding dice, ie. 2d10!, 4d100!, d12!, etc.

            specific_explode = regex.match(r'^((\d*)d(\d+))!(\d+)$', group)  # Regex for exploding dice on specific number, ie. d20!10 or d12!4

            comparison_explode = regex.match(r'^((\d*)d(\d+))!([<>])(\d+)$', group, regex.IGNORECASE)  # Regex for exploding dice with a comparison, ie. d20!>10, d6!<2

            penetrate = regex.match(r'^((\d*)d(\d+))!p$', group, regex.IGNORECASE)  # Penetrating dice are the same as exploding except any dice after the initial number are added with a -1 penalty

            specific_penetrate = regex.match(r'^((\d*)d(\d+))!p(\d+)$', group, regex.IGNORECASE)  # See above

            comparison_penetrate = regex.match(r'^((\d*)d(\d+))!p([<>])(\d+)$', group, regex.IGNORECASE)  # See above

            reroll = regex.match(r'^((\d*)d(\d+))([Rr])$', group, regex.IGNORECASE) # Reroll on a one, matches 1d6R, 4d12r, etc.

            specific_reroll = regex.match(r'^((\d*)d(\d+))([Rr])(\d+)$', group, regex.IGNORECASE) # Reroll on a specific number

            comparison_reroll =  regex.match(r'^((\d*)d(\d+))([Rr])([<>])(\d+)$', group, regex.IGNORECASE) # Reroll on a comparison

            success_comparison = regex.match(r'^((?:\d*)d(\d+))([<>])(\d+)$', group, regex.IGNORECASE)  # Regex for dice with comparison, ie. 2d10>4, 5d3<2, etc.

            success_fail_comparison = regex.match(r'^((?:\d*)d(\d+))(?|((<)(\d+)f(>)(\d+))|((>)(\d+)f(<)(\d+)))$', group, regex.IGNORECASE)  # Regex for dice with success comparison and failure comparison.

            keep = regex.match(r'^((?:\d*)d\d+)([Kk])(\d*)$', group, regex.IGNORECASE)  # Regex for keeping a number of dice, ie. 2d10K, 2d10k3, etc.

            drop = regex.match(r'^((?:\d*)d\d+)([Xx])(\d*)$', group, regex.IGNORECASE)  # As above but with dropping dice and X

            individual = regex.match(r'^((\d*)d(\d+))([asm])(\d+)$', group, regex.IGNORECASE) #Regex for rolling dice with a modifier attached to each roll

            normal = regex.match(r'^((\d*)d(\d+))$', group, regex.IGNORECASE)  # Regex for normal dice rolls

            literal = regex.match(r'^(\d+)(?!\.)$', group, regex.IGNORECASE)  # Regex for number literals.

            float_literal = regex.match(r'^(\.\d+)|(\d+.\d+)$', group, regex.IGNORECASE) # Regex for floats

            if explode is not None:  # Handle exploding dice without a comparison modifier.
                type_of_dice = int(explode[3])

                result = []
                last_result = roll_group(explode[1])
                result.extend(last_result)
                number_to_roll = num_equal(last_result, '=', type_of_dice)
                while number_to_roll != 0:
                    last_result = roll_group(str(number_to_roll) + 'd' + str(type_of_dice)) # Reroll dice
                    result.extend(last_result)
                    number_to_roll = num_equal(last_result, '=', type_of_dice) # Check how many dice we have to reroll again

                results.append(sum(result))
                roll = ','.join([('!' + str(i) if i == type_of_dice else str(i)) for i in result])  # Build a string of the dice rolls, adding an exclamation mark before every roll that resulted in an explosion.
                string.append('[%s]' % roll)

            elif specific_explode is not None:  # Handle exploding dice without a comparison modifier.
                type_of_dice = int(specific_explode[3])

                comparator = int(specific_explode[4])

                assert  0 < comparator <= type_of_dice

                result = []
                last_result = roll_group(specific_explode[1])
                result.extend(last_result)
                number_to_roll = num_equal(last_result, '=', comparator)
                while number_to_roll != 0:
                    last_result = roll_group(str(number_to_roll) + 'd' + str(type_of_dice))
                    result.extend(last_result)
                    number_to_roll = num_equal(last_result, '=', comparator)

                results.append(sum(result))
                roll = ','.join([('!' + str(i) if i == comparator else str(i)) for i in result])  # Build a string of the dice rolls, adding an exclamation mark before every roll that resulted in an explosion.
                string.append('[%s]' % roll)

            elif comparison_explode is not None:  # Handle exploding dice with a comparison modifier
                type_of_dice = int(comparison_explode[3])

                comparator = int(comparison_explode[5])

                if comparison_explode[4] == '>':  # Ensure comparison is within bounds
                    assert  0 < comparator < type_of_dice
                else:
                    assert  1 < comparator <= type_of_dice

                result = []
                last_result = roll_group(comparison_explode[1])
                result.extend(last_result)
                if comparison_explode[4] == '>':
                    number_to_roll = num_equal(last_result, '>', comparator)
                    while number_to_roll != 0:
                        last_result = roll_group(str(number_to_roll) + 'd' + str(type_of_dice))
                        result.extend(last_result)
                        number_to_roll = num_equal(last_result, '>', comparator)
                    roll = ','.join([('!' + str(i) if i > comparator else str(i)) for i in
                                     result])  # Same as on other explodes except with a > or < comparison

                else:
                    number_to_roll = num_equal(last_result, '<', comparator)
                    while number_to_roll != 0:
                        last_result = roll_group(str(number_to_roll) + 'd' + str(type_of_dice))
                        result.extend(last_result)
                        number_to_roll = num_equal(last_result, '<', comparator)
                    roll = ','.join([('!' + str(i) if i < comparator else str(i)) for i in
                                     result])  # Same as on other explodes except with a > or < comparison

                results.append(sum(result))
                string.append('[%s]' % roll)

            elif penetrate is not None:  # Handle penetrating dice without a comparison modifier.
                type_of_dice = int(penetrate[3])

                first_num = int(penetrate[2])

                result = []
                last_result = roll_group(penetrate[1])
                result.extend(last_result)
                number_to_roll = num_equal(last_result, '=', type_of_dice)
                while number_to_roll != 0:
                    last_result = roll_group(str(number_to_roll) + 'd' + str(type_of_dice))
                    result.extend(last_result)
                    number_to_roll = num_equal(last_result, '=', type_of_dice)

                pre_result = result[:first_num]  # Add the first rolls with no modifier
                pre_result.extend([x - 1 for x in result[first_num:]])  # Add the second rolls with a -1 modifier

                results.append(sum(pre_result))

                roll = ','.join(['!' + str(i) if i == type_of_dice else str(i) for i in result[:first_num]])  # Add the first numbers, without the -1 but with a ! when roll is penetration
                roll += (',' if len(pre_result) > first_num else '')  # Only add the comma in between if there's at least one penetration
                roll += ','.join([('!' + str(i) + '-1' if i == type_of_dice else str(i) + '-1') for i in result[first_num:]])  # Add the penetration dice with the '-1' tacked on the end
                string.append('[%s]' % roll)

            elif specific_penetrate is not None:  # Handle penetrating dice without a comparison modifier.
                type_of_dice = int(specific_penetrate[3])

                first_num = int(specific_penetrate[2])

                comparator = int(specific_penetrate[4])

                assert 0 < comparator <= type_of_dice

                result = []
                last_result = roll_group(specific_penetrate[1])
                result.extend(last_result)
                number_to_roll = num_equal(last_result, '=', comparator)
                while number_to_roll != 0:
                    last_result = roll_group(str(number_to_roll) + 'd' + str(type_of_dice))
                    result.extend(last_result)
                    number_to_roll = num_equal(last_result, '=', comparator)

                pre_result = result[:first_num]  # Same as normal penetration
                pre_result.extend([x - 1 for x in result[first_num:]])

                results.append(sum(pre_result))

                roll = ','.join(['!' + str(i) if i == comparator else str(i) for i in result[:first_num]])  # Same as above
                roll += (',' if len(pre_result) > first_num else '')
                roll += ','.join([('!' + str(i) + '-1' if i == comparator else str(i) + '-1') for i in result[first_num:]])
                string.append('[%s]' % roll)

            elif comparison_penetrate is not None:  # Handle penetrating dice without a comparison modifier.
                type_of_dice = int(comparison_penetrate[3])

                comparator = int(comparison_penetrate[5])

                first_num = int(comparison_penetrate[2])

                if comparison_penetrate[4] == '>':  # Ensure comparison is within bounds
                    assert 0 < comparator < type_of_dice
                else:
                    assert 1 < comparator <= type_of_dice

                result = []
                last_result = roll_group(comparison_penetrate[1])
                result.extend(last_result)

                # Do penetration based on more than or less than sign.
                if comparison_penetrate[4] == '>':
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

                if comparison_penetrate[4] == '>':
                    roll = ','.join(
                        ['!' + str(i) if i > comparator else str(i) for i in result[:first_num]])  # Same as above
                    roll += (',' if len(pre_result) > first_num else '')
                    roll += ','.join(
                        [('!' + str(i) + '-1' if i > comparator else str(i) + '-1') for i in result[first_num:]])
                else:
                    roll = ','.join(
                        ['!' + str(i) if i < comparator else str(i) for i in result[:first_num]])  # Same as above
                    roll += (',' if len(pre_result) > first_num else '')
                    roll += ','.join(
                        [('!' + str(i) + '-1' if i < comparator else str(i) + '-1') for i in result[first_num:]])
                string.append('[%s]' % roll)

            elif reroll is not None:  # Handle rerolling dice without a comparison modifier (ie. on 1)
                type_of_dice = int(reroll[3])

                result_strings = []
                roll_strings = []
                result = roll_group(reroll[1])
                repeat = True if reroll[4] == 'R' else False # Reroll just once or infinite number of times

                if repeat: #Handle rerolling the dice and building a string of all the rerolled ones
                    for i in range(len(result)):
                        prev = [result[i]]
                        while result[i] == 1:
                            result[i] = random.randint(1, type_of_dice)
                            prev.append(result[i])

                        roll_strings.append([str(x) for x in prev])

                else:
                    for i in range(len(result)):
                        prev = [result[i]]
                        if result[i] == 1:
                            result[i] = random.randint(1, type_of_dice)
                            prev.append(result[i])

                        roll_strings.append([str(x) for x in prev])

                results.append(sum(result))
                for roll_string in roll_strings:
                    roll_string.reverse()
                    result_strings.append('%s' % roll_string[0] + ('~' if len(roll_string) > 1 else '') + '~'.join(roll_string[1:])) #Build the string

                roll = ','.join(result_strings)
                string.append('[%s]' % roll)

            elif specific_reroll is not None:  # Handle rerolling dice on a specific number, see reroll
                type_of_dice = int(specific_reroll[3])
                comparator = int(specific_reroll[5])

                assert 0 < comparator <= type_of_dice # Ensure comparison is within bounds

                result_strings = []
                roll_strings = []
                result = roll_group(specific_reroll[1])
                repeat = True if specific_reroll[4] == 'R' else False

                if repeat:
                    for i in range(len(result)):
                        prev = [result[i]]
                        while result[i] == comparator:
                            result[i] = random.randint(1, type_of_dice)
                            prev.append(result[i])

                        roll_strings.append([str(x) for x in prev])

                else:
                    for i in range(len(result)):
                        prev = [result[i]]
                        if result[i] == comparator:
                            result[i] = random.randint(1, type_of_dice)
                            prev.append(result[i])

                        roll_strings.append([str(x) for x in prev])

                results.append(sum(result))
                for roll_string in roll_strings:
                    roll_string.reverse()
                    result_strings.append('%s' % roll_string[0] + ('~' if len(roll_string) > 1 else '') + '~'.join(roll_string[1:]))

                roll = ','.join(result_strings)
                string.append('[%s]' % roll)

            elif comparison_reroll is not None:  # Handle rerolling dice with a comparison modifier.
                type_of_dice = int(comparison_reroll[3])
                comparator = int(comparison_reroll[6])

                if comparison_reroll[5] == '>':  # Ensure comparison is within bounds
                    assert 0 < comparator < type_of_dice
                else:
                    assert 1 < comparator <= type_of_dice

                result_strings = []
                roll_strings = []
                result = roll_group(comparison_reroll[1])
                repeat = True if comparison_reroll[4] == 'R' else False
                if comparison_reroll[5] == '>':
                    if repeat:
                        for i in range(len(result)):
                            prev = [result[i]]
                            while result[i] > comparator:
                                result[i] = random.randint(1, type_of_dice)
                                prev.append(result[i])

                            roll_strings.append([str(x) for x in prev])

                    else:
                        for i in range(len(result)):
                            prev = [result[i]]
                            if result[i] > comparator:
                                result[i] = random.randint(1, type_of_dice)
                                prev.append(result[i])

                            roll_strings.append([str(x) for x in prev])
                else:
                    if repeat:
                        for i in range(len(result)):
                            prev = [result[i]]
                            while result[i] < comparator:
                                result[i] = random.randint(1, type_of_dice)
                                prev.append(result[i])

                            roll_strings.append([str(x) for x in prev])

                    else:
                        for i in range(len(result)):
                            prev = [result[i]]
                            if result[i] < comparator:
                                result[i] = random.randint(1, type_of_dice)
                                prev.append(result[i])

                            roll_strings.append([str(x) for x in prev])

                results.append(sum(result))
                for roll_string in roll_strings:
                    roll_string.reverse()
                    result_strings.append('%s' % roll_string[0] + ('~' if len(roll_string) > 1 else '') + '~'.join(roll_string[1:]))

                roll = ','.join(result_strings)
                string.append('[%s]' % roll)

            elif success_comparison is not None:
                group_result = roll_group(success_comparison[1])
                result = []
                result_string = []

                type_of_dice = int(success_comparison[2])

                comparator = int(success_comparison[4])

                if success_comparison[3] == '>':  # Ensure comparison is within bounds
                    assert 0 < comparator < type_of_dice
                else:
                    assert 1 < comparator <= type_of_dice

                for die in group_result:
                    if success_comparison[3] == '>':
                        result.append(1 if die > comparator else 0)
                        result_string.append('!' + str(die) if die > comparator else str(die))
                    else:
                        result.append(1 if die < comparator else 0)
                        result_string.append('!' + str(die) if die < comparator else str(die))

                results.append(sum(result))
                roll = ','.join(result_string)  # Craft the string, adding an exclamation mark before every string that passed the comparison.
                string.append('[%s]' % roll)

            elif success_fail_comparison is not None:
                group_result = roll_group(success_fail_comparison[1])

                result = []
                result_string = []

                type_of_dice = int(success_fail_comparison[2])
                success_comp = int(success_fail_comparison[5])
                fail_comp = int(success_fail_comparison[7])

                # Ensure both comparisons are within bounds
                if success_fail_comparison[4] == '>':
                    assert 0 < success_comp < type_of_dice
                    assert 1 < fail_comp <= type_of_dice
                else:
                    assert 1 < success_comp <= type_of_dice
                    assert 0 < fail_comp < type_of_dice

                for die in group_result:
                    if success_fail_comparison[4] == '>':  # Get the actual list of successes and fails with both comparisons
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

                results.append(sum(result))  #
                roll = ','.join(result_string)
                string.append('[%s]' % roll)

            elif keep is not None:  # Handle rolling dice and keeping the x highest or lowest values
                group_result = roll_group(keep[1])
                group_result.sort(reverse=True if keep[
                                                      2] == 'K' else False)  # Uppercase is keep highest and lowercase is keep lowest.

                num_to_keep = int(keep[3] if keep[3] != '' else 1)
                assert 1 <= num_to_keep < len(group_result)

                results.append(sum(group_result[:num_to_keep]))
                roll = ','.join([str(i) for i in group_result[
                                                 :num_to_keep]]) + ' ~~ '  # This time format the string with all kept rolls on the left and dropped rolls on the right
                roll += ','.join([str(i) for i in group_result[num_to_keep:]])
                string.append('[%s]' % roll)

            elif drop is not None:
                group_result = roll_group(drop[1])
                group_result.sort(reverse=True if drop[2] == 'X' else False)  # Same thing as keep dice

                num_to_drop = int(drop[3] if drop[3] != '' else 1)
                assert 1 <= num_to_drop < len(group_result)

                results.append(sum(group_result[:num_to_drop]))
                roll = ','.join([str(i) for i in group_result[num_to_drop:]]) + ' ~~ '  # Same as above.
                roll += ','.join([str(i) for i in group_result[:num_to_drop]])
                string.append('[%s]' % roll)

            elif individual is not None:
                group_result = roll_group(individual[1])
                result = []
                for i, j in enumerate(group_result): #add to each roll
                    if individual[4] == 'a':
                        result.append(j + int(individual[5]))

                    elif individual[4] == 's':
                        result.append(j - int(individual[5]))

                    elif individual[4] == 'm':
                        result.append(j * int(individual[5]))

                    else:
                        raise ValueError
                results.append(sum(result))
                roll = ','.join([str(x) + individual[4] + individual[5] for x in group_result]) #Create string with the modifier on each roll
                string.append('[%s]' % roll)

            elif normal is not None:
                group_result = roll_group(group)
                results.append(sum(group_result))
                roll = ','.join([str(i) for i in group_result])
                string.append('[%s]' % roll)

            elif literal is not None:
                results.append(int(literal[1]))  # Just append the integer value
                string.append(literal[1])

            elif float_literal is not None:
                if floats:
                    results.append(float(group))
                    string.append(group)
                else:
                    raise TypeError
            else:
                raise Exception

        except Exception:
            raise DiceGroupException('"%s" is not a valid dicegroup.' % group)

    parser = SimpleEval(floats=floats, functions=functions) #The parser object parses the dice rolls and functions
    try:
        final_result = parser.eval(''.join([str(x) for x in results])) #Call the parser to parse into one value
        if not floats:
            final_result = int(final_result)
    except Exception:
        raise DiceOperatorException('Error parsing operators and or functions')

    #Create explanation string and remove extraneous spaces
    explanation = ''.join(string)
    explanation = zero_width_split(r'((?<=[\/%^+\/])(?![\/,]))|((?<![\/,])(?=[\/%^+]))|((?<=[^\(\)])(?=-))|(?<=-)(?=[^\d\(\)a-z\[\]])|(?<=\d-)(?=.)|(?<=,)(?![^[]*])|(?<=([^,]\*))(?!\*)|(?<![,\*])(?=\*)', explanation) #Split on ops to properly format the explanation
    explanation = ' '.join(explanation)
    explanation = explanation.strip()
    explanation = regex.sub(r'[ \t]{2,}', ' ', explanation)

    return final_result, explanation

if __name__ == '__main__':
    while True:
        print('%s, %s' % roll_dice(input()))
