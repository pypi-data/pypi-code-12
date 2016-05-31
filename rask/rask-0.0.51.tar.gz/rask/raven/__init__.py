from logging import getLogger
from logging.config import dictConfig
from rask.options import options
from tornado.process import task_id

__all__ = ['Raven']

class Raven(object):
    __fmt = '%(log_color)s%(levelname)1.1s %(asctime)s %(name)s%(reset)s %(message)s'
    __logger = None
    __name = None

    def __init__(self,name='rask'):
        self.__name = name
    
    @property
    def logger(self):
        try:
            assert self.__logger
        except AssertionError:
            self.__config__()
            self.__logger = getLogger(self.__name)
        except:
            raise
        return self.__logger

    def __config__(self):
        dictConfig({
            'disable_existing_loggers':False,
            'formatters':{
                'rask':{
                    '()':'colorlog.ColoredFormatter',
                    'format':self.__fmt
                }
            },
            'handlers':{
                'default':{
                    'level':str(options.logging).upper(),
                    'class':'logging.StreamHandler',
                    "formatter": "rask"
                }
            },
            'loggers':{
                '': {
                    'handlers': ['default'],
                    'level':str(options.logging).upper(),
                    'propagate':True
                }
            },
            'version':1
        })
    
    def critical(self,arg):
        self.logger.critical(arg)
        return True

    def debug(self,arg):
        self.logger.debug(arg)
        return True

    def error(self,arg):
        self.logger.error(arg)
        return True

    def info(self,arg):
        self.logger.info(arg)        
        return True

    def mark(self,_):
        return '[%s]> %s' % (task_id(),_)
    
    def warning(self,arg):
        self.logger.warning(arg)
        return True
