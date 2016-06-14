"""Tests for act._log.

But actual tests use the public API via ``act.*``.

"""

import argparse
import logging
import re

import logbook
import pytest

import act


class TestLogLevelAction:
    """Tests for the LogLevelAction class.

    Instead of pretending we know what the argparse API expects and
    how it might change we use functional-level tests instead and try
    to implement a --loglevel option.

    """

    @pytest.fixture
    def parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-l', '--level', action=act.log.LogLevelAction)
        return parser

    @pytest.mark.parametrize('level', ['debug', 'DEBUG', 'DeBuG'])
    def test_valid_debug(self, parser, level):
        args = parser.parse_args(['-l', level])
        assert args.level == logbook.DEBUG

    @pytest.mark.parametrize('level', ['1', '8', '-1', 'foo'])
    def test_loglevel_invalid(self, parser, level):
        with pytest.raises(SystemExit):
            parser.parse_args(['-l', level])


class TestLogbookSetup:

    @pytest.mark.parametrize(['in_level', 'out_level'],
                             [(0, logbook.NOTSET),
                              ('DEBUG', logbook.DEBUG),
                              ('INFO', logbook.INFO),
                              ('NOTICE', logbook.NOTICE),
                              ('WARNING', logbook.WARNING),
                              ('ERROR', logbook.ERROR),
                              ('CRITICAL', logbook.CRITICAL)])
    def test_level(self, in_level, out_level):
        handler = act.log.setup_logbook(in_level)
        assert handler.level == out_level

    @pytest.mark.parametrize('level', [-1, 8, 'foo'])
    def test_wrong_level(self, level):
        with pytest.raises(LookupError):
            act.log.setup_logbook(level)

    def test_format(self, capsys):
        logger = logbook.Logger('testmod')
        handler = act.log.setup_logbook('INFO')
        with handler:
            logger.info('hi there')
        stdout, stderr = capsys.readouterr()
        datepattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d+ +'
        fmtpattern = r'INFO +testmod +hi there'
        assert re.match(datepattern + fmtpattern, stdout)
        assert stderr == ''

    def test_logging_redir(self):
        act.log.setup_logbook('DEBUG')
        with logbook.TestHandler() as testhandler:
            logging.info('hello')
        assert testhandler.has_info('hello')
