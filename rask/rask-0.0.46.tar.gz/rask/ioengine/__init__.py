from tornado.concurrent import Future
from tornado.ioloop import IOLoop
from uuid import uuid4

__all__ = ['IOEngine']

class IOEngine(object):
    __loop = None
    
    @property
    def loop(self):
        try:
            assert self.__loop
        except AssertionError:
            self.__loop = IOLoop.instance()
        except:
            raise
        return self.__loop

    @property
    def uuid4(self):
        return uuid4().hex
   
    def future(self,_):
        f = Future()
        self.loop.add_future(f,_)
        return f

    def start(self):
        return self.loop.start()

    def stop(self):
        return self.loop.stop()
