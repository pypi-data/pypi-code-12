from rask.ioengine import IOEngine
from rask.raven import Raven

__all__ = ['Base']

class Base(object):
    __active = False
    __ioengine = None
    __log = None
    __promises = None
    __uuid = None

    @property
    def active(self):
        try:
            assert self.__active
        except AssertionError:
            pass
        except:
            raise
        return self.__active

    @active.setter
    def active(self,_):
        try:
            assert _
        except AssertionError:
            self.__active = False
        except:
            raise
        else:
            self.__active = True
            self.ioengine.loop.add_callback(self.__promise_consume__)
    
    @property
    def ioengine(self):
        try:
            assert self.__ioengine
        except AssertionError:
            self.__ioengine = IOEngine()
        except:
            raise
        return self.__ioengine

    @property
    def log(self):
        try:
            assert self.__log
        except AssertionError:
            self.__log = Raven()
        except:
            raise
        return self.__log
    
    @property
    def promises(self):
        try:
            assert self.__promises
        except AssertionError:
            self.__promises = []
        except:
            raise
        return self.__promises
   
    @property
    def uuid(self):
        try:
            assert self.__uuid
        except AssertionError:
            self.__uuid = self.ioengine.uuid4
        except:
            raise
        return self.__uuid

    def __promise_consume__(self,_=None):
        try:
            _.next().set_result(self)
        except AttributeError:
            self.ioengine.loop.add_callback(self.__promise_consume__,iter(self.promises))
        except StopIteration:
            return True
        except:
            raise
        else:
            self.ioengine.loop.add_callback(self.__promise_consume__,_)
        return None
        
