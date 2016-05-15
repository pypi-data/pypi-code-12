import unittest
import logging
import sys
import re
from cStringIO import StringIO
import mock

from loap import LogOptionsArgumentParser


class LogOptionsArgumentParserTestCase (unittest.TestCase):
    def setUp(self):
        p = mock.patch('logging.basicConfig')
        self.addCleanup(p.stop)

        self.m_basicConfig = p.start()
        self.loap = LogOptionsArgumentParser()

    def _test_parse_args(self, args, expectedLogLevel):
        self.loap.parse_args(args)

        self.m_basicConfig.assert_called_once_with(
            loglevel=expectedLogLevel,
            stream=mock.ANY,
            format=mock.ANY,
            datefmt=mock.ANY,
        )

    def test_parse_empty(self):
        self._test_parse_args([], logging.INFO)

    def test_parse_quiet(self):
        self._test_parse_args(['--quiet'], logging.WARN)

    def test_parse_q(self):
        self._test_parse_args(['-q'], logging.WARN)

    def test_parse_debug(self):
        self._test_parse_args(['--debug'], logging.DEBUG)

    def _test_help_pattern(self, pattern):
        rgx = re.compile(pattern, re.MULTILINE)

        real_stdout = sys.stdout
        fake_stdout = StringIO()
        sys.stdout = fake_stdout
        try:
            self.assertRaises(
                SystemExit,
                self.loap.parse_args,
                ['--help'])
        finally:
            sys.stdout = real_stdout

        self.assertRegexpMatches(fake_stdout.getvalue(), rgx)

    def test_help_describes_quiet(self):
        self._test_help_pattern(
            r'^ *--quiet, -q +Log only warnings and errors$',
        )

    def test_help_describes_debug(self):
        self._test_help_pattern(
            r'^ *--debug +Log all messages, including debug messages$',
        )
