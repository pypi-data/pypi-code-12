# from __future__ import division
import math
from random import randint
import re

from pyparsing import alphanums
from pyparsing import alphas
from pyparsing import CaselessLiteral
from pyparsing import Combine
from pyparsing import Forward
from pyparsing import Literal
from pyparsing import nums
from pyparsing import Optional
from pyparsing import ParseException
from pyparsing import StringEnd
from pyparsing import Word
from pyparsing import ZeroOrMore


DEBUG_NO = ""
DEBUG_MIN = "MIN"
DEBUG_MAX = "MAX"
DEBUG_YES = "YES"


def _dice_grammar(exprStack, varStack):

    def pushFirst(str, loc, toks):
        exprStack.append(toks[0])

    def assignVar(str, loc, toks):
        varStack.append(toks[0])

    point = Literal('.')
    e = CaselessLiteral('E')
    plusorminus = Literal('+') | Literal('-')
    number = Word(nums)
    integer = Combine(Optional(plusorminus) + number)
    floatnumber = Combine(
        integer + Optional(point + Optional(number)) + Optional(e + integer))

    ident = Word(alphas, alphanums + '_')

    plus = Literal("+")
    minus = Literal("-")
    mult = Literal("*")
    div = Literal("/")

    lpar = Literal("(").suppress()
    rpar = Literal(")").suppress()
    addop = plus | minus
    multop = mult | div
    expop = Literal("^")
    dieop = Literal("d")
    assign = Literal("=")

    expr = Forward()
    atom = (
        (e | floatnumber | integer | ident).setParseAction(pushFirst) |
        (lpar + expr.suppress() + rpar))
    roll = Forward()
    roll << atom + ZeroOrMore((dieop + roll).setParseAction(pushFirst))

    factor = Forward()
    factor << roll + ZeroOrMore((expop + factor).setParseAction(pushFirst))

    term = factor + ZeroOrMore((multop + factor).setParseAction(pushFirst))

    expr << term + ZeroOrMore((addop + term).setParseAction(pushFirst))
    bnf = Optional((ident + assign).setParseAction(assignVar)) + expr

    return bnf + StringEnd()


# Recursive function that evaluates the stack
def evaluateStack(s, variables, roll_list, debug):
    def _randint_upto(size):
        if debug == DEBUG_MAX:
            return size
        if debug == DEBUG_MIN:
            return 1
        return randint(1, size)

    def _roll(amount, size):
        rolls = []
        amt = int(amount)
        sz = int(size)
        key = "%sd%s" % (amt, sz)
        sum = 0
        if size == 0:
            return 0
        for i in range(amt):
            roll = _randint_upto(sz)
            rolls.append(roll)
            sum += roll
        if key not in roll_list:
            roll_list[key] = []
        roll_list[key].append(rolls)
        return sum

    # map operator symbols to corresponding arithmetic operations
    opn = {
        "+": (lambda a, b: a + b),
        "-": (lambda a, b: a - b),
        "*": (lambda a, b: a * b),
        "/": (lambda a, b: a / b),
        "d": (lambda a, b: _roll(a, b)),
        "^": (lambda a, b: a ** b)}

    op = s.pop()
    if op in "+-*/^d":
        op2 = evaluateStack(s, variables, roll_list, debug)
        op1 = evaluateStack(s, variables, roll_list, debug)
        return opn[op](op1, op2)
    elif op == "PI":
        return math.pi
    elif op == "E":
        return math.e
    elif re.search('^[a-zA-Z][a-zA-Z0-9_]*$', op):
        if op in variables:
            return variables[op]
        else:
            return 0
    elif re.search('^[-+]?[0-9]+$', op):
        return int(op)
    else:
        return float(op)


class CaughtRollParsingError(Exception):
    def __init__(self, err):
        message = "Parse failure\n%s\n%s\n%s" % (
            err.line, " " * (err.column - 1) + "^", err)
        super(CaughtRollParsingError, self).__init__(message)


def _do_roll(input_string, variables, debug):
    exprStack = []
    varStack = []
    roll_list = {}
    pattern = _dice_grammar(exprStack, varStack)

    if input_string != '':
        # try parsing the input string
        try:
            pattern.parseString(input_string)
        except ParseException as err:
            raise CaughtRollParsingError(err)

        # calculate result , store a copy in ans , display the result to user
        result = evaluateStack(exprStack, variables, roll_list, debug)
        variables['ans'] = result

        if len(varStack) == 1:
            variables[varStack.pop()] = result
        return result, roll_list


def roll(input_string, variables={}, debug=DEBUG_NO):
    return _do_roll(input_string, variables, debug)
