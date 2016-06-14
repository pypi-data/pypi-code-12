"""Tests for act._appbase.

But actual tests use the public API via ``act.*``.
"""

import os
import signal
import time
from unittest import mock

import logbook
import pytest

import act


class TestArgumentParser:

    @pytest.mark.parametrize('argv, err', [
        ([], logbook.INFO),
        (['-l', 'error'], logbook.ERROR),
        (['-l', 'debug'], logbook.DEBUG),
        (['-l', '0'], logbook.NOTSET),
    ])
    def test_parse_args_default(self, argv, err):
        app = act.AppBase()
        parser = app.argparser('name', 'description', '0.3.0')
        args = parser.parse_args(argv)
        assert args.log_level == err

    def test_parse_args_version(self, capsys):
        app = act.AppBase()
        parser = app.argparser('name', 'description', '0.4.0')
        with pytest.raises(SystemExit):
            parser.parse_args(['--version'])
        out, _ = capsys.readouterr()
        assert '0.4.0' in out


class TestApp:

    def test_app_initiation(self, monkeypatch, loghandler):
        monkeypatch.setattr(act.log, 'setup_logbook',
                            mock.Mock(return_value=loghandler))
        with act.AppBase() as appbase:
            assert appbase._loghandler == loghandler
            assert appbase.loghandler == loghandler

    def test_app_main_application_exit(self, monkeypatch, loghandler):
        monkeypatch.setattr(act.log, 'setup_logbook',
                            mock.Mock(return_value=loghandler))
        with pytest.raises(SystemExit) as err:
            with act.AppBase():
                raise act.ApplicationExit()
        assert err.value.code == 0
        assert not loghandler.records

    @pytest.mark.parametrize('exception', [Exception, act.FatalError])
    def test_app_exit_fatalerror(self, exception, monkeypatch, loghandler):
        monkeypatch.setattr(act.log, 'setup_logbook',
                            mock.Mock(return_value=loghandler))
        with pytest.raises(SystemExit) as err:
            with act.AppBase():
                raise exception
        assert err.value.code == 1
        assert loghandler.has_critical()

    @pytest.mark.parametrize('sig', [signal.SIGTERM, signal.SIGINT])
    def test_exit_signal(self, request, monkeypatch, sig, loghandler):
        int_handler = signal.getsignal(signal.SIGINT)
        term_handler = signal.getsignal(signal.SIGTERM)
        def fin():
            signal.signal(signal.SIGINT, int_handler)
            signal.signal(signal.SIGTERM, term_handler)
        request.addfinalizer(fin)
        monkeypatch.setattr(act.log, 'setup_logbook',
                            mock.Mock(return_value=loghandler))
        with pytest.raises(SystemExit):
            with act.AppBase() as appbase:
                appbase.install_signal_handler(appbase.app_exit_signal_handler)
                os.kill(os.getpid(), sig)
                time.sleep(3)
            pytest.fail('Did not exit using signal handler.')
        assert not loghandler.records

    def test_exit_no_errors(self, monkeypatch, loghandler):
        monkeypatch.setattr(act.log, 'setup_logbook',
                            mock.Mock(return_value=loghandler))
        pop_mock = mock.Mock()
        monkeypatch.setattr(loghandler, 'pop_application', pop_mock)
        appbase = act.AppBase()
        assert appbase.__exit__(None, None, None) is None
        assert pop_mock.called
