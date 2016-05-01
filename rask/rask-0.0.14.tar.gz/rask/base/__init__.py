from rask.ioengine import IOEngine

__all__ = ['Base']

class Base(object):
    __ioengine = None
    __uuid = None

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
    def uuid(self):
        try:
            assert self.__uuid
        except AssertionError:
            self.__uuid = self.ioengine.uuid4
        except:
            raise
        return self.__uuid
