from rask.base import Base
from tornado.log import gen_log
from tornado.process import task_id

__all__ = ['Raven']

class Raven(Base):
    __logger = None

    @property
    def logger(self):
        try:
            assert self.__logger
        except AssertionError:
            self.__logger = gen_log
        except:
            raise
        return self.__logger

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
