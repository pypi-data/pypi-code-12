import six
import logging
import traceback

__DEFAULT_FMT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        ''' '''
        def handle(self, record):
            ''' '''

        def emit(self, record):
            ''' '''

        def createLock(self):
            ''' '''
            self.lock = None


def setup(name=None, lvl=None):
    ''' '''
    if lvl is None:
        lvl = logging.DEBUG

    logger = logging.getLogger(name)
    logger.setLevel(lvl)
    logger.addHandler(NullHandler())


def to_file(path, lvl, fmt=None, datefmt=None, name=None, **ops):
    ''' '''
    if fmt is None:
        fmt = __DEFAULT_FMT

    add_log_handler(logging.FileHandler(path, **ops), lvl, name, fmt, datefmt)


def to_console(lvl, fmt=None, datefmt=None, name=None, **ops):
    ''' '''
    if fmt is None:
        fmt = __DEFAULT_FMT

    add_log_handler(logging.StreamHandler(**ops), lvl, name, fmt, datefmt)


def add_log_handler(handler, level, name=None, fmt=None, datefmt=None):
    ''' '''
    logger = logging.getLogger(name)
    handler.setLevel(level)

    if fmt is not None:
        handler.setFormatter(logging.Formatter(fmt))

    logger.addHandler(handler)


def get_logger(obj):
    ''' '''
    if isinstance(obj, six.string_types):
        name = obj
    else:
        name =obj.__module__ + '.' + obj.__name__

    return logging.getLogger(name)


def loggable(obj):
    ''' '''
    if issubclass(obj, object):
        obj.logger = get_logger(obj)
        return obj
    else:
        raise TypeError()

def log_traceback(name):
    get_logger(name).debug(traceback.format_exc())
