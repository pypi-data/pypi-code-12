from rask.base import Base

__all__ = ['Riak']

class Riak(Base):
    def __init__(self,rmq):
        self.rmq = rmq

    @property
    def __channel__(self):
        try:
            assert self.__channel
        except (AssertionError,AttributeError):
            self.__channel = {}
        except:
            raise
        return True

    @property
    def __settings__(self):
        try:
            assert self.__settings
        except (AssertionError,AttributeError):
            self.__settings = {}
        except:
            raise
        return self.__settings
    
    def __services__(self):
        def on_get(_):
            return True

        self.rmq.channel('riak_get',self.ioengine.future(on_get))
        return True
    
    def get(self,cluster,bucket,key):
        self.rmq.channel('riak-get',self.ioengine.future(on_channel))
        return True
