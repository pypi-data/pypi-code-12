from unittest import TestCase

from mock import patch
from yolapy import configuration
from yolapy.configuration import configure, get_config


@patch.dict('yolapy.configuration.config', clear=True)
class TestConfiguration(TestCase):

    def test_sets_a_simple_value(self):
        configure(FOO='bar')
        self.assertEqual(configuration.config['FOO'], 'bar')

    def test_gets_a_config(self):
        configuration.config = {'foo': 'bar'}
        self.assertEqual(get_config('foo'), 'bar')

    def test_raises_if_config_is_missing(self):
        configuration.config = {'foo': 'bar'}
        self.assertRaises(KeyError, get_config, 'baz')

    def test_uses_default_if_config_is_missing(self):
        configuration.config = {'foo': 'bar'}
        self.assertEqual(get_config('baz', 'qux'), 'qux')
