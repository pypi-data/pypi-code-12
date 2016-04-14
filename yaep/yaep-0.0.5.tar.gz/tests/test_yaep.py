import os
import io
from unittest import TestCase
from .utils import monkey_patch
import yaep


class TestEnv(TestCase):
    def test_not_in_env(self):
        assert(yaep.env('FOOA') is None)

    def test_default(self):
        assert(yaep.env('FOOB', 'bar') == 'bar')

    def test_sticky(self):
        assert(os.getenv('FOOC') is None)
        yaep.env('FOOC', 'bar', sticky=True)
        assert(os.getenv('FOOC') == 'bar')

    def test_convert_boolean(self):
        yaep.env('FOOD', 'True', sticky=True)
        assert(yaep.env('FOOD') is True)
        assert(yaep.env('FOOD', convert_booleans=False) == 'True')

    def test_raise_unset_exception(self):
        with self.assertRaises(yaep.exceptions.UnsetException):
            yaep.env('BEER', default=yaep.exceptions.UnsetException)

    def test_type_class(self):
        os.environ['FOOE'] = '5'
        assert(yaep.env('FOOE') == '5')
        assert(yaep.env('FOOE', type_class=int) == 5)

    def run_cases(self, test_cases, boolean_map=None):
        for given, expected in test_cases:
            try:
                assert(
                    yaep.env(
                        'YAEP_TEST_NOT_THERE',
                        given,
                        boolean_map
                    ) == expected
                )
            except AssertionError:
                print 'Error testing {} - expected {}, but got {}'.format(
                    given,
                    str(expected),
                    str(yaep.env('YAEP_TEST_NOT_THERE', given))
                )
                raise

    def test_boolean_defaults(self):
        test_cases = [
            (True, True),
            (False, False),
        ]

        self.run_cases(test_cases)


class TestPopulateEnv(TestCase):
    def test_populate_env(self):
        env_file = io.BytesIO('foo = bar\nbaz = biz\nBOO = FAR')
        with monkey_patch(yaep.yaep, 'open', lambda fn: env_file):
            yaep.yaep.populate_env()
            assert(yaep.env('foo') == 'bar')
            assert(yaep.env('baz') == 'biz')
            assert(yaep.env('BOO') == 'FAR')
