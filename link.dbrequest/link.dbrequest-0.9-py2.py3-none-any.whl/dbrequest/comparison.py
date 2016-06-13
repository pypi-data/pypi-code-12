# -*- coding: utf-8 -*-

from link.dbrequest.tree import Node, Value
from link.dbrequest.ast import AST

from copy import deepcopy


class Comparable(object):
    """
    Base class for conditions, overriding logical operators.
    Check if property exists by default.
    """

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
        """
        Set comparison operator and compared value.

        :param operator: Comparison operator
        :type operator: str

        :param value: Compared value
        :type value: Node, or any Python type

        :returns: Itself
        :rtype: Comparable
        """

        if not isinstance(value, Node):
            value = Value(value)

        self.operator = operator
        self.value = value

        return self

    def __lt__(self, value):
        """
        Compare to value with operator <

        :param value: compared value
        :type value: Node, or any Python type

        :returns: Itself
        :rtype: Comparable
        """

        return self._compare(self.LT, value)

    def __le__(self, value):
        """
        Compare to value with operator <=

        :param value: compared value
        :type value: Node, or any Python type

        :returns: Itself
        :rtype: Comparable
        """

        return self._compare(self.LTE, value)

    def __eq__(self, value):
        """
        Compare to value with operator ==

        :param value: compared value
        :type value: Node, or any Python type

        :returns: Itself
        :rtype: Comparable
        """

        return self._compare(self.EQ, value)

    def __ne__(self, value):
        """
        Compare to value with operator !=

        :param value: compared value
        :type value: Node, or any Python type

        :returns: Itself
        :rtype: Comparable
        """

        return self._compare(self.NE, value)

    def __ge__(self, value):
        """
        Compare to value with operator >=

        :param value: compared value
        :type value: Node, or any Python type

        :returns: Itself
        :rtype: Comparable
        """

        return self._compare(self.GTE, value)

    def __gt__(self, value):
        """
        Compare to value with operator >

        :param value: compared value
        :type value: Node, or any Python type

        :returns: Itself
        :rtype: Comparable
        """

        return self._compare(self.GT, value)

    def __invert__(self):
        """
        Check if property does not exist

        :returns: Itself
        :rtype: Comparable
        """

        return self._compare(self.EXISTS, False)

    def __mod__(self, value):
        """
        Compare to value with operator <

        :param value: compared value
        :type value: Node, or any Python type

        :returns: Itself
        :rtype: Comparable
        """

        return self._compare(self.LIKE, value)


class CombinableCondition(object):
    """
    Combine conditions with boolean operators.
    """

    AND = '&'
    OR = '|'
    XOR = '^'

    def _combine(self, operator, value, _reversed):
        """
        Combine condition with value using operator.

        :param operator: Boolean operator
        :type operator: str

        :param value: Condition to combine with
        :type value: CombinableCondition

        :returns: Combined condition
        :rtype: CombinedCondition
        """

        if not isinstance(value, CombinableCondition):
            raise TypeError(
                'Expected CombinableCondition value, got {0}'.format(
                    value.__class__.__name__
                )
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

    def __xor__(self, value):
        return self._combine(self.XOR, value, False)

    def __rand__(self, value):
        return self._combine(self.AND, value, True)

    def __ror__(self, value):
        return self._combine(self.OR, value, True)

    def __rxor__(self, value):
        return self._combine(self.XOR, value, True)


class CombinedCondition(Node, CombinableCondition):
    """
    Combination of two conditions.

    :param left: left condition
    :type left: CombinableCondition

    :param operator: combination condition
    :type operator: str

    :param right: right condition
    :type right: CombinableCondition

    :param inverted: Equivalent of ``not (<condition>)`` (default: False)
    :type inverted: bool
    """

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
        """
        Negates the combined condition

        :returns: New combined condition
        :rtype: CombinedCondition
        """

        c = deepcopy(self)
        c.inverted = True
        return c


class C(Node, Comparable, CombinableCondition):
    """
    Condition on a property.
    """

    def get_ast(self):
        return [
            AST('prop', self.name),
            AST('cond', self.operator),
            self.value.get_ast()
        ]
