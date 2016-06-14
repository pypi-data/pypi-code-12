"""Various common logging related functionality."""


import argparse
import sys

import logbook


class LogLevelAction(argparse.Action):
    """A custom argparse action to validate loglevel as either int or string.

    Valid log levels are 0, "NOTSET", "DEBUG", "INFO", "WARNING",
    "ERROR" and "CRITICAL" in any case.  (Technically speaking there
    is also a "NOTICE" level but we don't use that.)
    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, value, option_string=None):
        try:
            intval = int(value)
        except ValueError:
            try:
                intval = logbook.lookup_level(value.upper())
            except LookupError as err:
                raise argparse.ArgumentError(
                    self, 'Invalid log level: {!r}'.format(value)) from err
        else:
            if intval != logbook.NOTSET:
                raise argparse.ArgumentError(
                    self, 'Invalid log level: {!r}'.format(value))
        setattr(namespace, self.dest, intval)


def setup_logbook(level='INFO'):
    """Create a handler for the application.

    This sets up a handler to use for the application the way we have
    logging configured normally, using stdout as destination for use
    by a process manager.  Using this ensures all our applications
    have consistent formatting etc.

    Use it like this::

       def mainloop(argv):
           args = parse_cmdline(argv)
           handler = act.log.setup_logbook(args.log_level)
           handler.push_application()  # optional, no need for with-statement
           with handler.applicationbound():
               # The actual application goes here
               run()

    Then your ``main()`` which calls mainloop can simply use the
    standard pattern while using logbook for the logging::

       def main(argv):
           try:
               mainloop(argv)
           except MyFatalError as err:
               logbook.critical(str(err))
               sys.exit(1)
           except Exception as err:
               logbook.critical(str(err), exc_info=True)
               sys.exit(1)

    This is designed to work well together with the
    :class:`LogLevelAction` so a value produced by that can be used
    here directly.

    :param str level: The desired loglevel, can be either a valid
       string or an integer in as one of the logbook.DEBUG and
       sibilings constants.  Note that logbook does not support custom
       loglevels.

    :raises LookupError: If a bad loglevel was passed in.
    :return: The global logbook handler.

    """
    # Extra check because logbook's lookup_level() does not verify
    # integer ranges.
    levels = {logbook.NOTSET,
              logbook.DEBUG,
              logbook.INFO,
              logbook.WARNING,
              logbook.ERROR,
              logbook.CRITICAL}
    if isinstance(level, int) and level not in levels:
        raise LookupError('Invalid loglevel')
    log_format = ('{record.time:%Y-%m-%d %H:%M:%S.%f} '
                  '{record.level_name:8} {record.channel:14} {record.message}')
    handler = logbook.StreamHandler(stream=sys.stdout,
                                    level=level,
                                    format_string=log_format)
    logbook.compat.redirect_logging()
    return handler
