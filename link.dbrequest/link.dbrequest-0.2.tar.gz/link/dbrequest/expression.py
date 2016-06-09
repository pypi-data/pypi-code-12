# -*- coding: utf-8 -*-

from link.dbrequest.tree import Node, Value
from link.dbrequest.ast import AST


class CombinableExpression(object):

    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIV = '/'
    MOD = '%'
    POW = '**'

    BITLSHIFT = '<<'
    BITRSHIFT = '>>'
    BITAND = '&'
    BITOR = '|'
    BITXOR = '^'

    def _combine(self, operator, value, reversed):
        if not isinstance(value, Node):
            value = Value(value)

        if reversed:
            result = CombinedExpression(value, operator, self)

        else:
            result = CombinedExpression(self, operator, value)

        return result

    def __add__(self, value):
        return self._combine(self.ADD, value, False)

    def __sub__(self, value):
        return self._combine(self.SUB, value, False)

    def __mul__(self, value):
        return self._combine(self.MUL, value, False)

    def __truediv__(self, value):
        return self._combine(self.DIV, value, False)

    def __div__(self, value):
        return self._combine(self.DIV, value, False)

    def __mod__(self, value):
        return self._combine(self.MOD, value, False)

    def __pow__(self, value):
        return self._combine(self.POW, value, False)

    def __lshift__(self, value):
        return self._combine(self.BITLSHIFT, value, False)

    def __rshift__(self, value):
        return self._combine(self.BITRSHIFT, value, False)

    def __and__(self, value):
        return self._combine(self.BITAND, value, False)

    def __or__(self, value):
        return self._combine(self.BITOR, value, False)

    def __xor__(self, value):
        return self._combine(self.BITXOR, value, False)

    def __radd__(self, value):
        return self._combine(self.ADD, value, True)

    def __rsub__(self, value):
        return self._combine(self.SUB, value, True)

    def __rmul__(self, value):
        return self._combine(self.MUL, value, True)

    def __rtruediv__(self, value):
        return self._combine(self.DIV, value, True)

    def __rdiv__(self, value):
        return self._combine(self.DIV, value, True)

    def __rmod__(self, value):
        return self._combine(self.MOD, value, True)

    def __rpow__(self, value):
        return self._combine(self.POW, value, True)

    def __rlshift__(self, value):
        return self._combine(self.BITLSHIFT, value, True)

    def __rrshift__(self, value):
        return self._combine(self.BITRSHIFT, value, True)

    def __rand__(self, value):
        return self._combine(self.BITAND, value, True)

    def __ror__(self, value):
        return self._combine(self.BITOR, value, True)

    def __rxor__(self, value):
        return self._combine(self.BITXOR, value, True)


class CombinedExpression(Node):
    def __init__(self, left, operator, right, *args, **kwargs):
        super(CombinedExpression, self).__init__(operator, *args, **kwargs)

        self.left = left
        self.right = right

    def get_ast(self):
        return [
            self.left.get_ast(),
            AST('op', self.name),
            self.right.get_ast()
        ]


class E(Node, CombinableExpression):
    def get_ast(self):
        return AST('ref', self.name)


class F(E):
    def __init__(self, funcname, *arguments):
        super(F, self).__init__(funcname)

        self.arguments = [
            arg if isinstance(arg, Node) else Value(arg)
            for arg in arguments
        ]

    def get_ast(self):
        return AST('func', {
            'func': self.name,
            'args': [
                arg.get_ast()
                for arg in self.arguments
            ]
        })
