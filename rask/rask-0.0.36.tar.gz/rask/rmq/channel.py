from rask.base import Base
from rask.options import options

__all__ = ['Channel']

class Channel(Base):
    __channel = False

    @property
    def channel(self):
        return self.__channel

    @channel.setter
    def channel(self,_):
        try:
            assert _
        except AssertionError:
            self.__channel = False
        except:
            raise
        else:
            self.__channel = _
            self.active = True

    def __init__(self,connection,future=None,prefetch=None):
        try:
            assert future
        except AssertionError:
            pass
        except:
            raise
        else:
            self.promises.append(future)
        finally:
            self.ioengine.loop.add_callback(
                self.open,
                connection=connection,
                prefetch=prefetch
            )
            
    def open(self,connection,prefetch=None):
        def on_open(result):
            try:
                assert result
            except AssertionError:
                future.set_result(False)
            except:
                raise
            else:
                self.channel = result
                self.ioengine.loop.add_callback(self.qos_set,prefetch=prefetch)
            return True

        connection.channel(on_open)
        return True

    def qos_set(self,prefetch=None):
        def on_qos(_):
            return True
        
        try:
            assert prefetch
        except AssertionError:
            prefetch = options.rask['rmq']['channel']['prefetch']
        except:
            raise

        self.channel.basic_qos(callback=on_qos,prefetch_count=prefetch)
        return True
