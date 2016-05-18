#coding:utf-8

import os
import sys
import traceback
import logging
from logging.handlers import RotatingFileHandler

__all__ = ['Logger']


class Logger(object):
    _no_handlers = True

    def __init__(self, **kwargs):
        assert kwargs.get('logfile'), 'Need logfile parameter.'
        assert kwargs.get('loglevel'), 'Need loglevel parameter.'
        self.loglevel = logging._levelNames[kwargs.get('loglevel')]
        self.max_file_size = kwargs.get('max_file_size', 10 * 1024 * 1024)
        self.backup_count = kwargs.get('backup_count', 3)
        self._setup_logging()
        if self._no_handlers:
            self._setup_handlers(logfilepath=kwargs.get('logfile'))

    def _setup_logging(self):
        self.logger = logging.getLogger()

    def _setup_handlers(self, logfilepath):
        if not os.path.exists(os.path.basename(logfilepath)):
            os.makedirs(os.path.basename(logfilepath))

        handler = RotatingFileHandler(filename=logfilepath, maxBytes=self.max_file_size, backupCount=self.backup_count)
        self.logger.setLevel(self.loglevel)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(module)s.%(funcName)s Line:%(lineno)d %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self._no_handlers = False

    def _log(self,message,level=logging.INFO):
        if level == logging.ERROR:
            ex_type, value, tb = sys.exc_info()
            errorlist = [line.lstrip() for line in traceback.format_exception(ex_type, value, tb)]
            errorlist.reverse()
            self.logger.log(level, "".join(errorlist))
        else:
            if isinstance(message,unicode):
                message=unicode.encode(message,'utf-8','ignore')
            self.logger.log(level, message)

    def debug(self, message):
        if logging.DEBUG >= self.loglevel:
            self._log(message, logging.DEBUG)

    def info(self, message):
        if logging.INFO >= self.loglevel:
            self._log(message, logging.INFO)

    def warn(self, message):
        if logging.WARN >= self.loglevel:
            self._log(message, logging.WARN)

    def error(self, message):
        if logging.ERROR >= self.loglevel:
            self._log(message, logging.ERROR)



# log = Logger()