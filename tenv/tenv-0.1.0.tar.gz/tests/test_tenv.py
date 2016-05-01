from unittest import TestCase

import tenv
from tests.test_read_dot_env import existing_file


class TestEnvironDictCasts(TestCase):
    def setUp(self):
        contents = """
DEBUG=True
SECRET=rthtrh43t56hf
SECONDS=5
HEIGHT=0.12
PORTS=122,124,12
        """
        with existing_file('1.txt', contents) as fname:
            self.env = tenv.initialize_env(env_file=fname)

    def test_plain_string(self):
        self.assertEqual(self.env.get('DEBUG'), 'True')
        self.assertEqual(self.env.get('SECRET'), 'rthtrh43t56hf')

    def test_bool(self):
        self.assertEqual(self.env.getbool('DEBUG'), True)

    def test_int(self):
        self.assertEqual(self.env.getint('SECONDS'), 5)

    def test_float(self):
        self.assertEqual(self.env.getfloat('HEIGHT'), 0.12)

    def test_list(self):
        self.assertEqual(self.env.getlist('PORTS'), ['122', '124', '12'])

    def test_default_value(self):
        self.assertEqual(self.env.getbool('AVAVAV', default=True), True)
