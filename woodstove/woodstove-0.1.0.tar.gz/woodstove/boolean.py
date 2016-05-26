'''
Boolean expression support.
'''


class Operand(object):
    '''
    Boolean expression operand
    '''

    def __and__(self, other):
        '''
        Support AND (&) operator

        @param other:
        '''
        return And(self, other)

    def __or__(self, other):
        '''
        Support OR (|) operator

        @param other:
        '''
        return Or(self, other)

    def __invert__(self):
        '''
        Support NOT (~) operator
        '''
        return Not(self)

    def __repr__(self):
        '''
        '''
        return '%s()' % (self.__class__.__name__,)

    def __nonzero__(self):
        '''
        '''
        return int(self.__bool__())

    def __bool__(self):
        '''
        '''
        return False


class UnaryOper(Operand):
    '''
    Unary operator base class.
    '''

    def __init__(self, value):
        '''

        @param value:
        '''
        self.value = value

    def __repr__(self):
        '''
        '''
        return '%s(%r)' % (self.__class__.__name__, self.value)


class BinaryOper(Operand):
    '''
    Binary operator base class.
    '''

    def __init__(self, left, right):
        '''

        @param left:
        @param right:
        '''
        self.left = left
        self.right = right

    def __repr__(self):
        '''
        '''
        return '%s(%r, %r)' % (self.__class__.__name__, self.left, self.right)


class And(BinaryOper):
    '''
    AND (&) Operator
    '''

    def __bool__(self):
        '''
        Evaluate expression

        @return:
        '''
        return (self.left and self.right).__bool__()


class Or(BinaryOper):
    '''
    OR (|) Operator
    '''

    def __bool__(self):
        '''
        Evaluate expression

        @return:
        '''
        return (self.left or self.right).__bool__()


class Not(UnaryOper):
    '''
    NOT (~) Operator
    '''

    def __bool__(self):
        '''
        Evaluate expression

        @return:
        '''
        return (not self.value)
