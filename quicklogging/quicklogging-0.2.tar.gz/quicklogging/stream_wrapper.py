"""
Module quicklogging.stream_wrapper
====================================

.. autoclass:: StreamWrapper

"""
import warnings

from .base import get_logger


class StreamWrapper:
    """Implementation detail"""

    INSTANCES = {}

    def __init__(self, original_stream, logfunc, catch_all=False, warn=False):
        self.original_stream = original_stream
        self.logfunc = logfunc
        self.catch_all = catch_all
        self.warn = warn

        self.fed_loggers = set()
        self.fed_logger_children = set()

    def _intercepting_logger(self):
        target_logger = get_logger(stackoverhead=2)
        if self.catch_all:
            return target_logger
        target_logger_name = target_logger.name

        if (
            target_logger_name in self.fed_loggers
        ) or any(
            target_logger_name.startswith(parent)
            for parent in self.fed_logger_children
        ):
            return target_logger
        return None

    def flush(self):
        pass

    def write(self, message):
        message = message.strip()

        if not message:
            return

        if self.warn:
            warnings.warn("print() detected: {}".format(message))

        target_logger = self._intercepting_logger()

        if target_logger is None:
            self.original_stream.write(message)
            return

        self.logfunc(message, stackoverhead=2)

    def include_in_catch(self, loggername, include_children):
        """include a
        :param bool include_children: also include children of the logger?
        """
        self.fed_loggers.add(loggername)
        if include_children:
            self.fed_logger_children.add(loggername)

    @classmethod
    def get_wrapper(cls, stream_name, stream, *args, **kwargs):
        if stream_name in cls.INSTANCES:
            wrapper, creation_args = cls.INSTANCES[stream_name]

            if creation_args != (args, kwargs):
                warnings.warn(
                    "Existing instance of {} was created with args {}"
                    "and you are trying to fetch it with different args: {}"
                    "".format(cls, creation_args, (args, kwargs))
                )

            return wrapper, False

        wrapper = cls(stream, *args, **kwargs)
        cls.INSTANCES[stream_name] = wrapper, (args, kwargs)
        return wrapper, True
