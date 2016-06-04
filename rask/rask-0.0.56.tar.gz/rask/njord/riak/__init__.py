from msg_pb2 import KDelPayload
from rask.base import Base
from rask.parser.pb import encode

__all__ = ['Riak']

class Riak(Base):
    channel = None
    __channel_name = 'njord_riak_client'
    options = {
        'exchange':'njord_riak'
    }
    
    def __init__(self,rmq):
        self.ioengine.loop.add_callback(self.start,rmq)

    def kdel(self,cluster,bucket,key):
        try:
            assert self.active
        except AssertionError:
            self.log.debug('kdel - not active, promise added')
            self.promises.append(
                self.kdel,
                cluster=cluster,
                bucket=bucket,
                key=key
            )
        except:
            raise
        else:
            self.channel.basic_publish(
                exchange=self.options['exchange'],
                routing_key='',
                body=encode(KDelPayload(
                    cluster=cluster,
                    bucket=bucket,
                    key=key
                ))
            )
        return True
        
    def start(self,rmq):
        def on_channel(result):
            self.channel = result.result()
            self.active = True
            return True
        
        rmq.channel(self.__channel_name,future=self.ioengine.future(on_channel))
        return True
        
    def stop(self):
        self.channel.close()
        self.active = False
        return True
