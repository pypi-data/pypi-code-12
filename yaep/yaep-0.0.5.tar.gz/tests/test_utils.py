import io
import ConfigParser
from unittest import TestCase
from yaep.utils import SectionHeader, str_to_bool


class TestSectionHeader(TestCase):
    def setUp(self):
        self.fp = io.BytesIO('foo = bar\nbaz = biz')
        self.expected = [('foo', 'bar'), ('baz', 'biz')]

    def test_needed(self):
        cp = ConfigParser.SafeConfigParser()
        self.assertRaises(
            ConfigParser.MissingSectionHeaderError,
            cp.readfp,
            self.fp
        )

    def test_header(self):
        cp = ConfigParser.SafeConfigParser()
        cp.readfp(SectionHeader(self.fp))

        assert(self.expected == cp.items(SectionHeader.header))


class TestStrToBool(TestCase):
    def run_cases(self, test_cases, boolean_map=None):
        for string, expected in test_cases:
            try:
                assert(str_to_bool(string, boolean_map) == expected)
            except AssertionError:
                print 'Error testing {} - expected {}, but got {}'.format(
                    string,
                    str(expected),
                    str(str_to_bool(string))
                )
                raise

    def test_bools(self):
        test_cases = [
            ('True', True),
            ('true', True),
            ('tRue', True),
            ('1', True),
            ('False', False),
            ('false', False),
            ('faLse', False),
            ('0', False)
        ]

        self.run_cases(test_cases)

    def test_nonbool_str(self):
        test_cases = [
            ('Pony', 'Pony'),
            (u'Pony', u'Pony')
        ]

        self.run_cases(test_cases)

    def test_nonstr(self):
        self.assertRaises(AttributeError, str_to_bool, 1)

    def test_custom_boolmap(self):
        test_cases = [
            ('True', True),
            ('true', True),
            ('tRue', True),
            ('1', True),
            ('Pony', True)
        ]

        self.run_cases(test_cases, boolean_map={
            True: ['True', '1', 'Pony']
        })
