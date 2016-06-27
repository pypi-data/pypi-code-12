from .msg import KDelPayload,KGetPayload,KSetPayload
from rask.base import Base
from uuid import uuid4

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

    @property
    def active(self):
        try:
            assert self.__active
        except (AttributeError,AssertionError):
            self.__active = False
        except:
            raise
        return self.__active
    
    @active.setter
    def active(self,_):
        try:
            assert _
            assert 'delete' in self.channel
            assert 'get' in self.channel
            assert 'set' in self.channel
        except AssertionError:
            self.__active = False
        except:
            raise
        else:
            self.__active = True
            self.ioengine.loop.add_callback(self.__promise_consume__)
    
    @property
    def etag(self):
        return sha1('%s:%s' % (self.uuid,uuid4().hex)).hexdigest()
        
    def __services__(self):
        def on_delete(_):
            self.log.info('channel del')
            self.channel['delete'] = _.result().channel
            self.active = True
            return True
        
        def on_get(_):
            self.log.info('channel get')
            self.channel['get'] = _.result().channel
            self.active = True
            return True

        def on_set(_):
            self.log.info('channel set')
            self.channel['set'] = _.result().channel
            self.active = True
            return True

        self.rmq.channel('riak_delete_%s' % self.uuid,self.ioengine.future(on_delete))
        self.rmq.channel('riak_get_%s' % self.uuid,self.ioengine.future(on_get))
        self.rmq.channel('riak_set_%s' % self.uuid,self.ioengine.future(on_set))
        return True

    def delete(self,cluster,bucket,key):
        try:
            assert self.active
        except AssertionError:
            def callback(_):
                self.ioengine.loop.add_callback(
                    self.delete,
                    cluster=cluster,
                    bucket=bucket,
                    key=key
                )
                return True
            
            self.promises.append(self.ioengine.future(callback))
            return None
        except:
            raise
        else:
            self.channel['delete'].basic_publish(
                body=encode(KDelPayload(
                    cluster=cluster,
                    bucket=bucket,
                    key=key
                )),
                exchange='',
                properties=BasicProperties(headers={
                    'cluster':cluster,
                    'service':'del'
                }),
                routing_key=''
            )
        return True
    
    def get(self,cluster,bucket,key,future):
        etag = self.etag
        
        try:
            payload = encode(KGetPayload(
                cluster=cluster,
                bucket=bucket,
                key=key,
                etag=etag
            ))
            assert payload
        except AssertionError:
            return False
        except:
            raise
        
        def on_get(result):
            future.set_result(result.result())
            return True

        def on_channel(_):
            _.result().channel.basic_publish(
                body=payload,
                exchange=options.rask_njord_riak['exchange']['topic'],
                properties=BasicProperties(headers={
                    'cluster':cluster,
                    'service':'kget'
                }),
                routing_key=''
            )
            return True
        
        self.rmq.channel('riak-get',self.ioengine.future(on_channel))
        return True

    def set(self,cluster,bucket,key,value):
        try:
            self.active
        except AssertionError:
            pass
        except:
            raise
        return True
