# -*- coding: utf-8 -*-

from link.dbrequest.tree import Node, Value
from link.dbrequest.ast import AST

from copy import deepcopy


class Comparable(object):

    EXISTS = '?'
    LT = '<'
    LTE = '<='
    EQ = '=='
    NE = '!='
    GTE = '>='
    GT = '>'
    LIKE = '~='

    def __init__(self, *args, **kwargs):
        super(Comparable, self).__init__(*args, **kwargs)

        self.operator = self.EXISTS
        self.value = Value(True)

    def _compare(self, operator, value):
        if not isinstance(value, Node):
            value = Value(value)

        self.operator = operator
        self.value = value

        return self

    def __lt__(self, value):
        return self._compare(self.LT, value)

    def __le__(self, value):
        return self._compare(self.LTE, value)

    def __eq__(self, value):
        return self._compare(self.EQ, value)

    def __ne__(self, value):
        return self._compare(self.NE, value)

    def __ge__(self, value):
        return self._compare(self.GTE, value)

    def __gt__(self, value):
        return self._compare(self.GT, value)

    def __invert__(self):
        return self._compare(self.EXISTS, False)

    def __mod__(self, value):
        return self._compare(self.LIKE, value)


class CombinableCondition(object):

    AND = '&'
    OR = '|'

    def _combine(self, operator, value, _reversed):
        if not isinstance(value, Node):
            raise TypeError(
                'Expected Node value, got {0}'.format(value.__class__.__name__)
            )

        if _reversed:
            result = CombinedCondition(value, operator, self)

        else:
            result = CombinedCondition(self, operator, value)

        return result

    def __and__(self, value):
        return self._combine(self.AND, value, False)

    def __or__(self, value):
        return self._combine(self.OR, value, False)

    def __rand__(self, value):
        return self._combine(self.AND, value, True)

    def __ror__(self, value):
        return self._combine(self.OR, value, True)


class CombinedCondition(Node):
    def __init__(self, left, operator, right, inverted=False, *args, **kwargs):
        super(CombinedCondition, self).__init__(operator, *args, **kwargs)

        self.left = left
        self.right = right
        self.inverted = inverted

    def get_ast(self):
        ast = [
            self.left.get_ast(),
            AST('join', self.name),
            self.right.get_ast()
        ]

        if self.inverted:
            return AST('not', ast)

        else:
            return ast

    def __invert__(self):
        c = deepcopy(self)
        c.inverted = True
        return c


class C(Node, Comparable, CombinableCondition):
    def get_ast(self):
        return [
            AST('prop', self.name),
            AST('cond', self.operator),
            self.value.get_ast()
        ]
