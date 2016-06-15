from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from logging.handlers import TimedRotatingFileHandler
import os
import subprocess
import sys


def setup_logger(
    logger,
    debug=False,
    stdout=False,
    log_to_file=None,
    add_thread_id=False,
    logging_level=None,
    use_path=False,
    suppress_stream_handler_broken_pipe_error=True,
):
    """Setup a given logger with the parameters given.

    The logger being edited always outputs to stdout or stderr with
    logging.StreamHandler in the standard logging module in additional to
    other handlers.

    Args:
        logger: The standard module logging.Logger instance to be edited
        debug: A boolean. True if the logger should be set to debug level.
            This argument is overridden if a non-None argument is passed to
            the logging_level parameter.
        stdout: A boolean to indicate the logger should use stdout or stderr
            for the logging.StreamHandler
        log_to_file: A filepath for a file being logged to.
            logging.handlers.TimedRotatingFileHandler and a new file is used
            daily with the old file renamed with the date.
        add_thread_id: A boolean. True if the logging format string should
            include the thread id.
        use_path: A boolean. True if the logging format string should use the
            file path name instead of the module name.
        suppress_stream_handler_broken_pipe_error: A boolean. True if
            suppressing the broken pipe error caused by flusing the stream in
            logging.StreamHandler. It's usually because of the output is
            getting piped to the unix "head" command on other commands that
            closes the standard input pipe prematurely.

    Returns:
        Nothing, since the logger is edited in-place.
    """
    if logging_level is None:
        if debug:
            logging_level = logging.DEBUG
        else:
            logging_level = logging.INFO

    formatter = create_logging_formatter(
        add_thread_id=add_thread_id,
        use_path=use_path
    )
    hdlr = create_stream_handler(
        formatter=formatter,
        stdout=stdout,
        suppress_stream_handler_broken_pipe_error=(
            suppress_stream_handler_broken_pipe_error
        ),
    )

    logger.handlers = []  # clear the existing handlers
    logger.addHandler(hdlr)
    logger.setLevel(logging_level)

    if log_to_file is not None:
        init_command = 'mkdir -p %s' % os.path.dirname(log_to_file)

        subprocess.check_call(init_command, shell=True)

        hdlr = TimedRotatingFileHandler(
            log_to_file,
            when="midnight",
            interval=1,
        )
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)


def suppress_stream_handler_broken_pipe_error_in_flush(stream_handler):
    old_flush = stream_handler.flush
    def wrapper(*args, **kwargs):
        try:
            old_flush(*args, **kwargs)
        except IOError as e:
            if e.errno == 32:
                return
            else:
                raise
    stream_handler.flush = wrapper


def create_plain_logger(
    logger_name,
    debug=False,
    stdout=True,
    logging_level=None,
    suppress_stream_handler_broken_pipe_error=True,
):
    plain_logger = logging.getLogger(logger_name)
    plain_logger.propagate = False

    if logging_level is None:
        if debug:
            logging_level = logging.DEBUG
        else:
            logging_level = logging.INFO

    plain_logger.setLevel(logging_level)

    if stdout:
        out = sys.stdout
    else:
        out = sys.stderr

    formatter = logging.Formatter(
        fmt="%(message)s",
        datefmt="%Y",  # does not matter
    )
    handler = create_stream_handler(
        formatter=formatter,
        stdout=stdout,
        suppress_stream_handler_broken_pipe_error=(
            suppress_stream_handler_broken_pipe_error
        ),
    )

    plain_logger.addHandler(handler)
    return plain_logger


def create_logging_formatter(add_thread_id=False, use_path=False):
    format_str = "%(asctime)s"

    if add_thread_id:
        format_str += " thread:%(thread)s"

    format_str += " %(levelname)s "

    if use_path:
        format_str += "%(pathname)s"
    else:
        format_str += "%(name)s"

    format_str += ":%(lineno)s: %(message)s"

    detail_formatter = logging.Formatter(
        fmt=format_str,
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    return detail_formatter


def create_stream_handler(
    formatter=None,
    stdout=False,
    suppress_stream_handler_broken_pipe_error=True,
):
    if formatter is None:
        formatter = create_logging_formatter()

    if stdout:
        stream = sys.stdout
    else:
        stream = sys.stderr

    hdlr = logging.StreamHandler(stream=stream)
    hdlr.setFormatter(formatter)

    if suppress_stream_handler_broken_pipe_error:
        suppress_stream_handler_broken_pipe_error_in_flush(hdlr)
    return hdlr


if __name__ == '__main__':
    """
    Run this module with: python -m sorno.logging

    Otherwise it will fail because the name of this module, "logging", is the
    same as the standard module name. When a file is run as a script, e.g.
    python sorno/logging.py, it's not seen as inside a package and the
    enclosing directory is put at the first path in the modue search path.
    """

    plain_stdout_logger = create_plain_logger(
        "plain_logger",
        stdout=True,
    )
    plain_stdout_logger.info("plain stdout logger at info level")
    plain_stdout_logger.debug("should not see this one")

    plain_stdout_debug_logger = create_plain_logger(
        "plain_debug_logger",
        stdout=True,
        debug=True,
    )
    plain_stdout_debug_logger.info("plain stdout debug logger at info level")
    plain_stdout_debug_logger.debug("plain stdout debug logger at debug level")

    plain_stderr_logger = create_plain_logger(
        "plain_stderr_logger",
        stdout=False,
    )
    plain_stderr_logger.info("plain stderr logger at info level")
    plain_stderr_logger.debug("should not see this one")
