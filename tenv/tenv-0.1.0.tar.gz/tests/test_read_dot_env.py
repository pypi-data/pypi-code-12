from unittest import TestCase
import os

from tenv._read_dot_env import read_file_values

import contextlib
@contextlib.contextmanager
def existing_file(fname, contents):
    with open('1.txt', 'w') as f:
        f.write(contents.strip())

    yield fname
    os.remove(fname)

class TestReadDotFile(TestCase):
    def test_read_correct_file(self):
        contents = """
DEBUG=True
DEBUG2=False
        """
        with existing_file('1.txt', contents) as fname:
            env = read_file_values(fname)

        self.assertEqual(env['DEBUG'], 'True')
        self.assertEqual(env['DEBUG2'], 'False')

    def test_read_empty_file(self):
        contents = ""
        with existing_file('1.txt', contents) as fname:
            env = read_file_values(fname)

        self.assertEqual(len(env), 0)

    def test_fail_on_invalid_file(self):
        contents = "DEBUG DEBUG=False"

        with existing_file('1.txt', contents) as fname:
            env = read_file_values(fname, fail_silently=False)

        self.assertTrue('DEBUG' not in env)
        self.assertEqual(len(env), 0)
