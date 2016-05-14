from rask.base import Base
from rask.options import define,options,parse_command_line
from rask.raven import Raven
from tornado.web import Application

__all__ = ['Main']

class Main(Base):
    __http__ = None
    __http_routes__ = []
    __options__ = {
        'http':{
            'port':8088
        },
        'rmq':{
            'channel':{
                'prefetch':10
            }
        }
    }
    __raven = None

    @property
    def log(self):
        try:
            assert self.__raven
        except AssertionError:
            self.__raven = Raven()
        except:
            raise
        return self.__raven
    
    def __init__(self):
        self.setup()
        self.before()
        self.ioengine.loop.add_callback(self.after)
        self.ioengine.loop.add_callback(self.http)
        self.ioengine.start()

    def after(self):
        pass
        
    def before(self):
        pass

    def http(self):
        try:
            assert self.__http_routes__
        except AssertionError:
            return False
        except:
            raise
        else:
            self.__http__ = Application(self.__http_routes__)
            self.ioengine.loop.add_callback(self.__http__.listen,options.rask['http']['port'])
            self.log.info('HTTP Server - %s' % options.rask['http']['port'])
        return True
    
    def setup(self):
        define('rask',default=self.__options__)
        parse_command_line()
        return True
