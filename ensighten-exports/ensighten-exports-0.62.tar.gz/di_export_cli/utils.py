import gzip
import logging
from logging.handlers import RotatingFileHandler
import os

class gzopen(object):

    def __init__(self, fname):

        f = open(fname)
        if fname.endswith('.gz'):
            self.f = gzip.GzipFile(fileobj=f)
        else:
            self.f = f

    # Define '__enter__' and '__exit__' to use in
    # 'with' blocks. Always close the file and the
    # GzipFile if applicable.
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        try:
            self.f.fileobj.close()
        except AttributeError:
            pass
        finally:
            self.f.close()

    # Reproduce the interface of an open file
    # by encapsulation.
    def __getattr__(self, name):
        return getattr(self.f, name)

    def __iter__(self):
        return iter(self.f)

    def next(self):
        return next(self.f)


def setup_logger(path, level=logging.DEBUG):
    log_directory = os.path.join(path, 'log')
    if not os.path.isdir(log_directory):
        os.makedirs(log_directory)
    file_name = os.path.join(log_directory, 'sync.log')

    log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(module)s(%(lineno)d): %(message)s')
    handler = RotatingFileHandler(file_name, mode='a', maxBytes=5*1024*1024, backupCount=2, encoding=None, delay=0)

    handler.setFormatter(log_formatter)
    handler.setLevel(level)
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(handler)
