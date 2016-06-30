"""
Tests for core module.
"""
import unittest


class TestCase(unittest.TestCase):

    def setUp(self):
        pass
    
    def test_blabla(self):
        pass


def suite():
    return unittest.makeSuite(TestCase, 'test')


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
