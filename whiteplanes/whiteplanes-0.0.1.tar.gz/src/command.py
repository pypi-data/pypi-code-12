#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from exceptions import SyntaxError


########################################################################
# Push
########################################################################
class Push(object):

    Token, Step, IsNeedParameter = "  ", 2, True

    @classmethod
    def process(cls, *, context=None, parameter=None):
        """ Evaluate the PUSH command. """
        context.stack.append(int(parameter['param'], 2))


########################################################################
# Copy
########################################################################
class Copy(object):

    Token, Step, IsNeedParameter = " \t ", 3, True

    @classmethod
    def process(cls, *, context=None, parameter=None):
        """ Evaluate the COPY command. """
        index = int(parameter['param'], 2)
        context.stack.append(context.stack[index])


########################################################################
# Slide
########################################################################
class Slide(object):

    Token, Step, IsNeedParameter = " \t\n", 3, True

    @classmethod
    def process(cls, *, context=None, parameter=None):
        """ Evaluate the SLIDE command. """
        value = context.stack.pop()
        for index in range(0, int(parameter['param'], 2)):
            context.stack.pop()
        context.stack.append(value)


########################################################################
# Duplicate
########################################################################
class Duplicate(object):

    Token, Step, IsNeedParameter = " \n ", 3, False

    @classmethod
    def process(cls, *, context=None, parameter=None):
        """ Evaluate the DUPLICATE command. """
        context.stack.append(context.stack[-1])


########################################################################
# Swap
########################################################################
class Swap(object):

    Token, Step, IsNeedParameter = " \n\t", 3, False

    @classmethod
    def process(cls, *, context=None, parameter=None):
        """ Evaluate the SWAP command. """
        c = context
        c.stack[-1], c.stack[-2] = c.stack[-2], c.stack[-1]


########################################################################
# Discard
########################################################################
class Discard(object):

    Token, Step, IsNeedParameter = " \n\n", 3, False

    @classmethod
    def process(cls, *, context=None, parameter=None):
        """ Evaluate the DISCARD command. """
        context.stack.pop()


########################################################################
# Add
########################################################################
class Add(object):

    Token, Step, IsNeedParameter = "\t   ", 4, False

    @classmethod
    def process(cls, *, context=None, parameter=None):
        """ Evaluate the ADD command. """
        lhs, rhs = context.stack.pop(), context.stack.pop()
        context.stack.append(lhs + rhs)


########################################################################
# Sub
########################################################################
class Sub(object):

    Token, Step, IsNeedParameter = "\t  \t", 4, False

    @classmethod
    def process(cls, *, context=None, parameter=None):
        """ Evaluate the SUB command. """
        lhs, rhs = context.stack.pop(), context.stack.pop()
        context.stack.append(lhs - rhs)


########################################################################
# Mul
########################################################################
class Mul(object):

    Token, Step, IsNeedParameter = "\t  \n", 4, False

    @classmethod
    def process(cls, *, context=None, parameter=None):
        """ Evaluate the MUL command. """
        lhs, rhs = context.stack.pop(), context.stack.pop()
        context.stack.append(lhs * rhs)


########################################################################
# Div
########################################################################
class Div(object):

    Token, Step, IsNeedParameter = "\t \t ", 4, False

    @classmethod
    def process(cls, *, context=None, parameter=None):
        """ Evaluate the DIV command. """
        lhs, rhs = context.stack.pop(), context.stack.pop()
        context.stack.append(lhs / rhs)


########################################################################
# Mod
########################################################################
class Mod(object):

    Token, Step, IsNeedParameter = "\t \t\t", 4, False

    @classmethod
    def process(cls, *, context=None, parameter=None):
        """ Evaluate the MOD command. """
        lhs, rhs = context.stack.pop(), context.stack.pop()
        context.stack.append(lhs % rhs)


########################################################################
# Store
########################################################################
class Store(object):

    Token, Step, IsNeedParameter = "\t\t ", 3, False

    @classmethod
    def process(cls, *, context=None, parameter=None):
        """ Evaluate the STORE command. """
        value, address = context.stack.pop(), context.stack.pop()
        context.heap[address] = value


########################################################################
# Retrieve
########################################################################
class Retrieve(object):

    Token, Step, IsNeedParameter = "\t\t\t", 3, False

    @classmethod
    def process(cls, *, context=None, parameter=None):
        """ Evaluate the RETRIEVE command. """
        address = context.stack.pop()
        context.stack.append(context.heap[address])


########################################################################
# Register
########################################################################
class Register(object):

    Token, Step, IsNeedParameter = "\n  ", 3, True

    @classmethod
    def process(cls, *, context=None, parameter=None):
        """ Evaluate the REGISTER command. """
        context.labels[parameter['param']] = parameter['location']


########################################################################
# Call
########################################################################
class Call(object):

    Token, Step, IsNeedParameter = "\n \t", 3, True

    @classmethod
    def process(cls, *, context=None, parameter=None):
        """ Evaluate the CALL command. """
        context.callstack.append(parameter['location'])
        context.counter = context.labels[parameter['param']]


########################################################################
# Jump
########################################################################
class Jump(object):

    Token, Step, IsNeedParameter = "\n \n", 3, True

    @classmethod
    def process(cls, *, context=None, parameter=None):
        """ Evaluate the JUMP command. """
        context.counter = context.labels[parameter['param']]


########################################################################
# Equal
########################################################################
class Equal(object):

    Token, Step, IsNeedParameter = "\n\t ", 3, True

    @classmethod
    def process(cls, *, context=None, parameter=None):
        """ Evaluate the TEST[EQUAL] command. """
        if context.stack.pop() == 0:
            context.counter = context.labels[parameter['param']]


########################################################################
# Less
########################################################################
class Less(object):

    Token, Step, IsNeedParameter = "\n\t\t", 3, True

    @classmethod
    def process(cls, *, context=None, parameter=None):
        """ Evaluate the TEST[LESS] command. """
        if context.stack.pop() < 0:
            context.counter = context.labels[parameter['param']]


########################################################################
# Return
########################################################################
class Return(object):

    Token, Step, IsNeedParameter = "\n\t\n", 3, False

    @classmethod
    def process(cls, *, context=None, parameter=None):
        """ Evaluate the RETURN command. """
        context.counter = context.callstack.pop()


########################################################################
# End
########################################################################
class End(object):

    Token, Step, IsNeedParameter = "\n\n\n", 3, False

    @classmethod
    def process(cls, *, context=None, parameter=None):
        """ Evaluate the END command. """
        context.counter = sys.maxsize - 1


########################################################################
# Cout
########################################################################
class Cout(object):

    Token, Step, IsNeedParameter = "\t\n  ", 4, False

    @classmethod
    def process(cls, *, context=None, parameter=None):
        """ Evaluate the OUTPUT[CHARACTER] command. """
        value = context.stack.pop()
        context.output(chr(value))


########################################################################
# Iout
########################################################################
class Iout(object):

    Token, Step, IsNeedParameter = "\t\n \t", 4, False

    @classmethod
    def process(cls, *, context=None, parameter=None):
        """ Evaluate the OUTPUT[INT] command. """
        value = context.stack.pop()
        context.output(value)


########################################################################
# Cin
########################################################################
class Cin(object):

    Token, Step, IsNeedParameter = "\t\n\t ", 4, False

    @classmethod
    def process(cls, *, context=None, parameter=None):
        """ Evaluate the INPUT[CHARACTER] command. """
        address = context.stack.pop()
        value = context.input("CIN")
        context.heap[address] = ord(value)


########################################################################
# Iin
########################################################################
class Iin(object):

    Token, Step, IsNeedParameter = "\t\n\t\t", 4, False

    @classmethod
    def process(cls, *, context=None, parameter=None):
        """ Evaluate the INPUT[INT] command. """
        address = context.stack.pop()
        value = context.input("IIN")
        context.heap[address] = value


########################################################################
# Command
########################################################################
class Command(object):

    def __init__(self, name, *, parameter=None):
        self.name = name
        self.parameter = parameter

    def __call__(self, *, context=None):
        self.name.process(context=context, parameter=self.parameter)

    Instructions = [
        Push, Copy, Slide, Duplicate, Swap, Discard, Add, Sub, Mul, Div, Mod,
        Store, Retrieve, Register, Call, Jump, Equal, Less, Return, End,
        Cout, Iout, Cin, Iin
    ]

    @classmethod
    def make(cls, code):
        cur, commands, count = 0, 0, len(code)
        while cur < count:
            instruction, param, cur = cls.make_instruction(code=code, cursor=cur)
            yield Command(instruction, parameter={'param': param, 'location': commands})
            commands += 1

    @classmethod
    def make_instruction(cls, *, code="", cursor=0):
        token = code[cursor:] if ((cursor + 3) - len(code)) >= 0 else code[cursor:cursor + 4]
        for instruction in cls.Instructions:
            if "".join(token[0:instruction.Step]) == instruction.Token:
                cur = cursor + instruction.Step
                param, index = cls.parameter(code, cur) if instruction.IsNeedParameter else (None, 0)
                cur += index
                return instruction, param, cur
        raise SyntaxError("syntax error, invalid command")

    @classmethod
    def parameter(cls, code, index):
        param = ""
        for character in code[index:]:
            if character == " ":
                param += "0"
            elif character == "\t":
                param += "1"
            elif character == "\n":
                return (param, len(param) + 1)
        raise SyntaxError("syntax error, invalid command")

    @classmethod
    def characters(cls):
        return [" ", "\t", "\n"]
