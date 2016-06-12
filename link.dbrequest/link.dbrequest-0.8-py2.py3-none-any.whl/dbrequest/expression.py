# -*- coding: utf-8 -*-

from link.dbrequest.tree import Node, Value
from link.dbrequest.ast import AST


class CombinableExpression(object):
    """
    Base class for expressions, overriding mathematical expressions.
    """

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

    def _combine(self, operator, value, _reversed):
        """
        Combine this CombinableExpression with another.

        :param operator: Mathematical operator used for combination
        :type operator: str

        :param value: Value to combine with
        :type value: Node or any Python type

        :param _reversed: Combination direction
        :type _reversed: bool

        :returns: Combined expression
        :rtype: CombinedExpression
        """

        if not isinstance(value, Node):
            value = Value(value)

        if _reversed:
            result = CombinedExpression(value, operator, self)

        else:
            result = CombinedExpression(self, operator, value)

        return result

    def __add__(self, value):
        """
        Combine with operator +

        :param value: Value to combine with
        :type value: Node or any Python type

        :returns: Combined expression
        :rtype: CombinedExpression
        """

        return self._combine(self.ADD, value, False)

    def __sub__(self, value):
        """
        Combine with operator -

        :param value: Value to combine with
        :type value: Node or any Python type

        :returns: Combined expression
        :rtype: CombinedExpression
        """

        return self._combine(self.SUB, value, False)

    def __mul__(self, value):
        """
        Combine with operator *

        :param value: Value to combine with
        :type value: Node or any Python type

        :returns: Combined expression
        :rtype: CombinedExpression
        """

        return self._combine(self.MUL, value, False)

    def __truediv__(self, value):
        """
        Combine with operator /

        :param value: Value to combine with
        :type value: Node or any Python type

        :returns: Combined expression
        :rtype: CombinedExpression
        """

        return self._combine(self.DIV, value, False)

    def __div__(self, value):
        """
        Combine with operator /
        Python2 compatibility

        :param value: Value to combine with
        :type value: Node or any Python type

        :returns: Combined expression
        :rtype: CombinedExpression
        """

        return self._combine(self.DIV, value, False)

    def __mod__(self, value):
        """
        Combine with operator %

        :param value: Value to combine with
        :type value: Node or any Python type

        :returns: Combined expression
        :rtype: CombinedExpression
        """

        return self._combine(self.MOD, value, False)

    def __pow__(self, value):
        """
        Combine with operator **

        :param value: Value to combine with
        :type value: Node or any Python type

        :returns: Combined expression
        :rtype: CombinedExpression
        """

        return self._combine(self.POW, value, False)

    def __lshift__(self, value):
        """
        Combine with operator <<

        :param value: Value to combine with
        :type value: Node or any Python type

        :returns: Combined expression
        :rtype: CombinedExpression
        """

        return self._combine(self.BITLSHIFT, value, False)

    def __rshift__(self, value):
        """
        Combine with operator >>

        :param value: Value to combine with
        :type value: Node or any Python type

        :returns: Combined expression
        :rtype: CombinedExpression
        """

        return self._combine(self.BITRSHIFT, value, False)

    def __and__(self, value):
        """
        Combine with operator &

        :param value: Value to combine with
        :type value: Node or any Python type

        :returns: Combined expression
        :rtype: CombinedExpression
        """

        return self._combine(self.BITAND, value, False)

    def __or__(self, value):
        """
        Combine with operator |

        :param value: Value to combine with
        :type value: Node or any Python type

        :returns: Combined expression
        :rtype: CombinedExpression
        """

        return self._combine(self.BITOR, value, False)

    def __xor__(self, value):
        """
        Combine with operator ^

        :param value: Value to combine with
        :type value: Node or any Python type

        :returns: Combined expression
        :rtype: CombinedExpression
        """

        return self._combine(self.BITXOR, value, False)

    def __radd__(self, value):
        """
        Combine with operator + if left value does not support the combination

        :param value: Value to combine with
        :type value: Node or any Python type

        :returns: Combined expression
        :rtype: CombinedExpression
        """

        return self._combine(self.ADD, value, True)

    def __rsub__(self, value):
        """
        Combine with operator - if left value does not support the combination

        :param value: Value to combine with
        :type value: Node or any Python type

        :returns: Combined expression
        :rtype: CombinedExpression
        """

        return self._combine(self.SUB, value, True)

    def __rmul__(self, value):
        """
        Combine with operator * if left value does not support the combination

        :param value: Value to combine with
        :type value: Node or any Python type

        :returns: Combined expression
        :rtype: CombinedExpression
        """

        return self._combine(self.MUL, value, True)

    def __rtruediv__(self, value):
        """
        Combine with operator / if left value does not support the combination

        :param value: Value to combine with
        :type value: Node or any Python type

        :returns: Combined expression
        :rtype: CombinedExpression
        """

        return self._combine(self.DIV, value, True)

    def __rdiv__(self, value):
        """
        Combine with operator / if left value does not support the combination
        Python2 compatibility

        :param value: Value to combine with
        :type value: Node or any Python type

        :returns: Combined expression
        :rtype: CombinedExpression
        """

        return self._combine(self.DIV, value, True)

    def __rmod__(self, value):
        """
        Combine with operator % if left value does not support the combination

        :param value: Value to combine with
        :type value: Node or any Python type

        :returns: Combined expression
        :rtype: CombinedExpression
        """

        return self._combine(self.MOD, value, True)

    def __rpow__(self, value):
        """
        Combine with operator ** if left value does not support the combination

        :param value: Value to combine with
        :type value: Node or any Python type

        :returns: Combined expression
        :rtype: CombinedExpression
        """

        return self._combine(self.POW, value, True)

    def __rlshift__(self, value):
        """
        Combine with operator << if left value does not support the combination

        :param value: Value to combine with
        :type value: Node or any Python type

        :returns: Combined expression
        :rtype: CombinedExpression
        """

        return self._combine(self.BITLSHIFT, value, True)

    def __rrshift__(self, value):
        """
        Combine with operator >> if left value does not support the combination

        :param value: Value to combine with
        :type value: Node or any Python type

        :returns: Combined expression
        :rtype: CombinedExpression
        """

        return self._combine(self.BITRSHIFT, value, True)

    def __rand__(self, value):
        """
        Combine with operator & if left value does not support the combination

        :param value: Value to combine with
        :type value: Node or any Python type

        :returns: Combined expression
        :rtype: CombinedExpression
        """

        return self._combine(self.BITAND, value, True)

    def __ror__(self, value):
        """
        Combine with operator | if left value does not support the combination

        :param value: Value to combine with
        :type value: Node or any Python type

        :returns: Combined expression
        :rtype: CombinedExpression
        """

        return self._combine(self.BITOR, value, True)

    def __rxor__(self, value):
        """
        Combine with operator ^ if left value does not support the combination

        :param value: Value to combine with
        :type value: Node or any Python type

        :returns: Combined expression
        :rtype: CombinedExpression
        """

        return self._combine(self.BITXOR, value, True)


class CombinedExpression(Node, CombinableExpression):
    """
    Combination of two expressions.

    :param left: left expression
    :type left: CombinableExpression

    :param operator: combination expression
    :type operator: str

    :param right: right expression
    :type right: CombinableExpression
    """

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
    """
    Expression referencing a property, usable in mathematical expressions to
    represent a formula applied on the referenced property.
    """

    def get_ast(self):
        return AST('ref', self.name)


class F(E):
    """
    Function, representing a mathematical function.

    :param funcname: Mathematical function
    :type funcname: str

    :param arguments: List of expressions/values to use as function arguments
    :type arguments: list
    """

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
