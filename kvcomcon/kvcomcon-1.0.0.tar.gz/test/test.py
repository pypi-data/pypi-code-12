# pylint: disable=missing-docstring

import os
from unittest import TestCase

from kvcomcon import ConfigError, config_from_path

class TestKvComCon(TestCase):
    def setUp(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))

    def test_from_path(self):
        path = os.path.join(self.script_dir, 'test1.config')
        result = list(config_from_path(path))

        self.assertEqual(result, [('foo', 'bar 123')])

    def test_error(self):
        with self.assertRaises(ConfigError):
            try:
                path = os.path.join(self.script_dir, 'invalid.config')
                list(config_from_path(path))
            except ConfigError as err:
                self.assertEqual(err.message,
                                 'error parsing {} line 2'.format(path))
                self.assertEqual(err.filename, path)
                self.assertEqual(err.line_number, 2)
                self.assertEqual(err.line, 'asdf')

                raise
