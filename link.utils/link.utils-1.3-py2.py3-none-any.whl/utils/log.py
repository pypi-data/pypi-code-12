# -*- coding: utf-8 -*-

from b3j0f.conf import Configurable, category, Parameter

from link.utils.filter import Filter
from link.utils import CONF_BASE_PATH

import traceback
import logging


def logrecord_to_dict(record):
    """
    Transform a LogRecord object into a dict.

    :param record: record to transform
    :type record: LogRecord

    :returns: record as a JSON serializable dict
    :rtype: dict
    """

    document = {
        'name': record.name,
        'level': record.levelno,
        'pathname': record.pathname,
        'lineno': record.lineno,
        'msg': record.msg % record.args,
        'func': record.funcName
    }

    if record.exc_info is not None:
        document['exc_info'] = {
            'type': record.exc_info[0].__name__,
            'msg': str(record.exc_info[1]),
            'traceback': ''.join(traceback.format_tb(record.exc_info[2]))
        }

    try:
        document['sinfo'] = record.sinfo

    except AttributeError:
        document['sinfo'] = None

    return document


class LogFilter(logging.Filter):
    """
    Filter log records using ``link.utils.filter.Filter``.
    """

    @property
    def log_filter(self):
        if not hasattr(self, '_log_filter'):
            self.log_filter = None

        return self._log_filter

    @log_filter.setter
    def log_filter(self, value):
        if value is not None:
            value = Filter(value)

        self._log_filter = value

    def filter(self, record):
        if self.log_filter is not None:
            document = logrecord_to_dict(record)
            return self.log_filter.match(document)

        else:
            return super(LogFilter, self).filter(record)


cls = logging.getLoggerClass()

if not hasattr(cls, '__configurable__') or not cls.__configurable__:
    @Configurable(
        paths='{0}/logging.conf'.format(CONF_BASE_PATH),
        conf=category(
            'LOGGING',
            Parameter(name='log_format'),
            Parameter(name='log_level'),
            Parameter(name='log_filter', ptype=dict)
        )
    )
    class ConfigurableLogger(cls):
        """
        Configurable logger.
        """

        __configurable__ = True

        @property
        def log_format(self):
            if not hasattr(self, '_log_format'):
                self.log_format = None

            return self._log_format

        @log_format.setter
        def log_format(self, value):
            if value is not None:
                formatter = logging.Formatter(value)
                self.handler.setFormatter(formatter)

            self._log_format = value

        @property
        def log_level(self):
            if not hasattr(self, '_log_level'):
                self.log_level = None

            return self._log_level

        @log_level.setter
        def log_level(self, value):
            if value is not None:
                try:
                    lvl = getattr(logging, value.upper())

                except AttributeError:
                    lvl = logging.INFO

                self.handler.setLevel(lvl)

            self._log_level = value

        @property
        def log_filter(self):
            if not hasattr(self, '_log_filter'):
                self.log_filter = None

            return self._log_filter

        @log_filter.setter
        def log_filter(self, value):
            self.filter.log_filter = value
            self._log_filter = value

        def __init__(self, name):
            cls.__init__(self, name)

            self.handler = logging.StreamHandler()
            self.addHandler(self.handler)

            self.filter = LogFilter()
            self.handler.addFilter(self.filter)

    logging.setLoggerClass(ConfigurableLogger)
