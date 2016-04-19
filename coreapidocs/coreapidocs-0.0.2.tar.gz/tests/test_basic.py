import unittest


class TestBasic(unittest.TestCase):

    def setUp(self):
        super(TestBasic, self).setUp()

    def test_example(self):
        self.assertEqual(2, 2)
