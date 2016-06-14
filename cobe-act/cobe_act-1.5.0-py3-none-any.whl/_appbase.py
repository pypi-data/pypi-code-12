"""A standard context manager based wrapper for topology applications.

This wrapper provides:
- a global log handler;
- standardised handling of exceptions from the client application;
- an args parser with default setting of log level;
- signal handler registration, with the option of a default handler.
"""

import argparse
import signal
import sys

import logbook

import act


class ApplicationExit(Exception):
    """Clean shutdown condition.

    Exception which can be used to signal normal application exit to
    the :class:`AppBase` context manager.  Upon catching this
    exception :class:`AppBase` will terminate the application
    with a return code of 0 (success).
    """
    pass


class FatalError(Exception):
    """Fatal error condition.

    Exception which can be used to signal a fatal error condition to
    the :class:`AppBase` context manager.  Upon catching this
    exception :class:`AppBase` will terminate the application with a
    non-zero return code.
    """


class ArgumentParser(argparse.ArgumentParser):
    """A parser with standardised log argument handling.

    This automatically adds:

    (a) arg option ``-l, --log-level`` with default log level ``INFO`` and
        adjusts the level of the log handler after parsing the arguments;

    (b) arg option ``--version`` to output the application version number
        and exit.
    """

    def __init__(self, loghandler, version, **kwargs):
        self._loghandler = loghandler
        super().__init__(**kwargs)
        self.add_argument(
            '-l', '--log-level',
            metavar='LEVEL',
            default=logbook.INFO,
            help='Log verbosity: debug, info, warning, error, or critical.',
            action=act.log.LogLevelAction,
        )
        self.add_argument(
            '--version',
            action='version',
            version='%(prog)s {}'.format(version),
        )

    def parse_args(self, *args, **kwargs):
        """Parse the arguments and return the arg namespace object.

        Additionally, the loghandler's level is set based on the
        ``--log-level`` parameter.
        """
        args = super().parse_args(*args, **kwargs)
        self._loghandler.level = args.log_level
        return args


class AppBase:
    """A standard context manager based approach to running applications.

    This context manager provides:

    (a) a global loghandler;

    (b) standardised handling of exceptions from the client application;

    (c) :meth:`argparser`, which provides command line arguments
        parsing with built-in handling of logging command line
        options;

    (d) :meth:`install_signal_handler` to configure signal handling,
        with optional signal handler :meth:`app_exit_signal_handler`
        that returns an :class:`ApplicationExit` exception in the
        event of a SIGTERM or SIGINT signal.

    If the code running inside the context manager raises an
    exception, :func:`sys.exit` is called.  Depending on the exception
    some information might be logged as well:

    ApplicationExit
       Nothing is logged, ``sys.exit(0)`` is called.

    FatalError
       The exception message is logged, ``sys.exit(1)`` is called.

    Exception
       For any other sub-classes of :class:`Exception` the message
       "Unexpected fatal error: " is logged with the exception message
       and a full traceback.

    If the code running inside the context manager ends without an
    exception the context manager will only unconfigure the log
    handler.  As :func:`sys.exit` is not called, code after the context
    manager will continue to be run.

    An example of how to use this::

       with act.AppBase() as appbase:
           appbase.install_signal_handler(appbase.app_exit_signal_handler)
           parser = appbase.argparser(name='hello',
                                      description='Say hello',
                                      version='0.3.0)
           parser.add_argument('--message', default=None, type=str,
                               help='Use a custom message')
           args = parser.parse_args(argv)
           if args.message:
               print(msg)
           else:
               print('Hello world')
    """

    def __init__(self):
        self._loghandler = act.log.setup_logbook(logbook.DEBUG)

    @property
    def loghandler(self):
        """The registered loghandler.

        This context manager configures an application-wide log
        handler which is active while inside the context manager, this
        gives access to this handler.  This would allow, for example,
        changing the log level.
        """
        return self._loghandler

    def __enter__(self):
        """Push the loghandler to the application stack."""
        self._loghandler.push_application()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Application teardown.

        This catches exceptions from the application and de-registers
        the log handler.  See the class description for a full
        description of the exception handling.
        """
        if exc_type == ApplicationExit:
            self._loghandler.pop_application()
            sys.exit(0)
        elif exc_type == FatalError:
            logbook.critical(exc_value)
            self._loghandler.pop_application()
            sys.exit(1)
        elif exc_type != None:
            logbook.critical('Unexpected fatal error: {}',
                             exc_value, exc_info=True)
            self._loghandler.pop_application()
            sys.exit(1)
        else:
            self._loghandler.pop_application()
            return None

    def argparser(self, name, description, version):
        """Create and return an :class:`argparse.ArgumentParser` instance.

        This creates a customised :class:`argparse.ArgumentParser`
        instance which adds the ``--log-level`` option by default and
        is integrated with :attr:`loghandler` so that the level of the
        handler is automatically adjusted when the arguments are
        parsed.

        :param str name: The name of the application.
        :param str description: The text to display before the
           argument help.
        :param str version: The version of the application.

        :returns: An instantiated instance of arg parser
           :class:`argparse.ArgumentParser`.
        """
        return ArgumentParser(loghandler=self._loghandler,
                              version=version,
                              prog=name,
                              description=description)

    @staticmethod
    def app_exit_signal_handler(signal_no, stack_frame):  # pylint: disable=unused-argument
        """A standard signal handler.

        When installed as signal handler this will simply raise
        :class:`ApplicationExit` which will cause the context manager
        to exit successfully.
        """
        raise ApplicationExit('Terminating on signal')

    @staticmethod
    def install_signal_handler(handler):
        """Install a signal handler on default termination signals.

        This installs the provided handler function for the default
        termination signals.
        """
        signal.signal(signal.SIGTERM, handler)
        signal.signal(signal.SIGINT, handler)
