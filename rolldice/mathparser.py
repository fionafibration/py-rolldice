#!/usr/bin/python
# encoding: utf-8

'''
Thanks to louisfisch on GitHub for this wonderful math parser!
https://github.com/louisfisch/mathematical-expressions-parser
'''

import math


_FUNCTIONS = { # Extensible to allow calling more functions by adding a string name
    # And the actual function object
    'abs': abs,
}

class Parser:
    def __init__(self, string): # Initialize by starting at index 0
        self.string = string
        self.index = 0

    def __call__(self): # Main function of the parser, parses the string and returns the value
        value = self.parseExpression()
        
        if self.hasNext():
            raise Exception(
                "Unexpected character found: '" + self.peek() + "' at index " + str(self.index)
            )
        return int(value)

    def peek(self): # Look at the next char in the string
        return self.string[self.index:self.index + 1]

    def hasNext(self): # Checks whether there's more chars
        return self.index < len(self.string)

    # This is kind of reversed PEMDAS
    # Starts at addition, addition calls multiplication, etc.
    def parseExpression(self): 
        return self.parseAddition()

    def parseAddition(self): #Parse addition and subtraction
        values = [self.parseMultiplication()]
        
        while True:
            char = self.peek()
            
            if char == '+':
                self.index += 1
                values.append(self.parseMultiplication())
            elif char == '-':
                self.index += 1
                values.append(-1 * self.parseMultiplication())
            else:
                break
        
        return sum(values)

    def parseMultiplication(self): #Parse multiplication and division (floor)
        values = [self.parseParenthesis()]
            
        while True:
            char = self.peek()
                
            if char == '*':
                self.index += 1
                values.append(self.parseParenthesis())
            elif char == '/':
                div_index = self.index
                self.index += 1
                denominator = self.parseParenthesis()
                     
                if denominator == 0:
                    raise Exception(
                        "Division by 0 (occured at index " + str(div_index) + ")"
                    )
                values.append(1.0 / denominator) # Division
            else:
                break
                     
        value = 1 # Not a float so division doesn't ever return a float
        
        for factor in values: # Multiply up all the factors
            value *= factor
        return value

    def parseParenthesis(self): # Parse any values inside parentheses
        char = self.peek()
        
        if char == '(':
            self.index += 1
            value = self.parseExpression()
            
            if self.peek() != ')':
                raise Exception("No closing parenthesis found at character " + str(self.index))
            self.index += 1
            return value
        else:
            return self.parseNegative()

    def parseNegative(self): # Parse possible negative integers
        char = self.peek()
        
        if char == '-':
            self.index += 1
            return -1 * self.parseParenthesis()
        else:
            return self.parseValue()

    def parseValue(self): # Parse a number literal or a 'variable', which for our purposes is only a function
        char = self.peek()
        
        if char in '0123456789':
            return self.parseNumber()
        else:
            return self.parseVariable()
 
    def parseVariable(self): # Parse a function literal. May be expanded to variables
        var = []
        while self.hasNext():
            char = self.peek()
            
            if char.lower() in 'abcdefghijklmnopqrstuvwxyz':
                var.append(char)
                self.index += 1
            else:
                break
        var = ''.join(var)
        
        function = _FUNCTIONS.get(var.lower())
        if function != None:
            arg = self.parseParenthesis()
            return int(function(arg))
            
        raise Exception("Unrecognized variable: '" + var + "'")

    def parseNumber(self): # Parse a numerical literal
        strValue = ''
        char = ''

        while self.hasNext():
            char = self.peek()
            
            if char in '0123456789':
                strValue += char
            else:
                break
            self.index += 1

        if len(strValue) == 0:
            if char == '':
                raise Exception("Unexpected end found")
            else:
                raise Exception("Expecting to find a number at " + str(self.index) + " but instad found '" + char + "'")
            
        return int(strValue)
