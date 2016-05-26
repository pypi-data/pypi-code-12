import unittest
from woodstove import boolean


class _Bool(boolean.Operand):
    def __init__(self, value):
        self.value = value

    def __bool__(self):
        return bool(self.value)


ZERO = _Bool(False)
ONE = _Bool(True)


def _gen1():
    '''
    Generator for single boolean digit.
    '''
    for x in (ZERO, ONE):
        yield x


def _gen2():
    '''
    Generator for two boolean digits.
    '''
    for x in _gen1():
        for y in _gen1():
            yield (x, y)


def _gen3():
    '''
    Generator for three boolean digits.
    '''
    for x, y in _gen2():
        for z in _gen1():
            yield (z, y, z)


class TestBoolean(unittest.TestCase):
    '''
    Ensure the woodstove boolean module complies with the laws of boolean
    algebra.
    '''

    def test_associativity_of_and(self):
        '''
        Associativity of AND
        x & (y & z) = (x & y) & z
        '''
        for x, y, z in _gen3():
            self.assertEqual(
                    bool((x & (y & z))),
                    bool(((x & y) & z)),
            )


    def test_associativity_of_or(self):
        '''
        Associativity of OR
        x | (y | z) = (x | y) | z
        '''
        for x, y, z in _gen3():
            self.assertEqual(
                    bool(x | (y | z)),
                    bool((x | y) | z),
            )

    def test_commutativity_of_and(self):
        '''
        Commutativity on AND
        x & y = y & x
        '''
        for x, y in _gen2():
            self.assertEqual(
                    bool(x & y),
                    bool(y & x),
            )


    def test_commutativity_of_or(self):
        '''
        Commutativity of OR
        x | y = y | x
        '''
        for x, y in _gen2():
            self.assertEqual(
                    bool(x | y),
                    bool(y | x),
            )

    def test_distributivity_of_and_over_or(self):
        '''
        Distributivity of AND over OR
        x & (y | z) = (x & y) | (x & z)
        '''
        for x, y, z in _gen3():
            self.assertEqual(
                    bool(x & (y | z)),
                    bool((x & y) | (x & z)),
            )

    def test_identity_for_and(self):
        '''
        Identity for AND
        x & 1 = x
        '''
        for x in _gen1():
            self.assertEqual(
                    bool(x & ONE),
                    bool(x),
            )

    def test_identity_for_or(self):
        '''
        Identity for OR
        x | 0 = x
        '''
        for x in _gen1():
            self.assertEqual(
                    bool(x | ZERO),
                    bool(x),
            )

    def test_annihilator_of_and(self):
        '''
        Annihilator of AND
        x & 0 = 0
        '''
        for x in _gen1():
            self.assertEqual(
                    bool(x & ZERO),
                    bool(ZERO),
            )

    def test_idempotence_of_and(self):
        '''
        Idempotence of AND
        x & x = x
        '''
        for x in _gen1():
            self.assertEqual(
                    bool(x & x),
                    bool(x),
            )

    def test_idempotence_of_or(self):
        '''
        Idempotence of OR
        x | x = x
        '''
        for x in _gen1():
            self.assertEqual(
                    bool(x | x),
                    bool(x),
            )

    def test_absorption_1(self):
        '''
        Absorption 1
        x & (x | y) = x
        '''
        for x, y in _gen2():
            self.assertEqual(
                    bool(x & (x | y)),
                    bool(x),
            )

    def test_absorption_2(self):
        '''
        Absorption 2
        x | (x & y) = x
        '''
        for x, y in _gen2():
            self.assertEqual(
                    bool(x | (x & y)),
                    bool(x),
            )

    def test_distributivity_of_or_over_and(self):
        '''
        Distributivity of OR over AND
        x | (y & z) = (x | y) & (x | z)
        '''
        for x, y, z in _gen3():
            self.assertEqual(
                    bool(x | (y & z)),
                    bool((x | y) & (x | z)),
            )

    def test_annihilator_of_or(self):
        '''
        Annihilator of OR
        x | 1 = 1
        '''
        for x in _gen1():
            self.assertEqual(
                    bool(x | ONE),
                    bool(ONE),
            )

    def test_complementation_1(self):
        '''
        Complementation 1
        x & ~x = 0
        '''
        for x in _gen1():
            self.assertEqual(
                    bool(x & ~x),
                    bool(ZERO),
            )

    def test_complementation_2(self):
        '''
        Complementation 2
        x | ~x = 1
        '''
        for x in _gen1():
            self.assertEqual(
                    bool(x | ~x),
                    bool(ONE),
            )

    def test_double_negation(self):
        '''
        Double negation
        ~~x = x
        '''
        for x in _gen1():
            self.assertEqual(
                    bool(~~x),
                    bool(x),
            )

    def test_de_morgan_1(self):
        '''
        De Morgan 1
        (~x) & (~y) = ~(x | y)
        '''
        for x, y in _gen2():
            self.assertEqual(
                    bool((~x) & (~y)),
                    bool(~(x | y)),
            )
    
    def test_de_morgan_2(self):
        '''
        De Morgan 2
        (~x) | (~y) = ~(x & y)
        '''
        for x, y in _gen2():
            self.assertEqual(
                    bool((~x) | (~y)),
                    bool(~(x & y)),
            )
