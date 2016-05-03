import logging
import os


class Logger:
    CRITICAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET

    def __init__(self, filename, overwrite=False):
        _format = "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s"
        _date_format = "%Y-%m-%d %H:%M:%S"
        _file_mode = "a"
        if overwrite is True:
            _file_mode = "w"

        logging.basicConfig(filename=filename, level=logging.NOTSET, format= _format, datefmt=_date_format,
                            filemode=_file_mode)
        self.internalLogger = logging.getLogger(filename.split(os.pathsep)[-1])

    def set_format(self, new_format):
        logging.basicConfig(format=new_format)

    def set_date_format(self, new_date_format):
        logging.basicConfig(datefmt=new_date_format)

    def log(self, msg, level=NOTSET):
        if level == Logger.CRITICAL:
            self.internalLogger.critical(msg)
        elif level == Logger.ERROR:
            self.internalLogger.error(msg)
        elif level == Logger.WARNING:
            self.internalLogger.warning(msg)
        elif level == Logger.INFO:
            self.internalLogger.info(msg)
        else:
            self.internalLogger.debug(msg)

    def critical(self, msg):
        self.log(msg, Logger.CRITICAL)

    def error(self, msg):
        self.log(msg, Logger.ERROR)

    def warn(self, msg):
        self.log(msg, Logger.WARNING)

    def info(self, msg):
        self.log(msg, Logger.INFO)

    def debug(self, msg):
        self.log(msg, Logger.DEBUG)



