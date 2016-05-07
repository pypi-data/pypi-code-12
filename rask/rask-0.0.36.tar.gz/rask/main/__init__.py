from rask.base import Base
from rask.options import define

__all__ = ['Main']

class Main(Base):
    def __init__(self):
        self.setup()
        self.before()
        self.ioengine.loop.add_callback(self.after)
        self.ioengine.start()

    def after(self):
        pass
        
    def before(self):
        pass

    def setup(self):
        define('rask',default={
            'rmq':{
                'channel':{
                    'prefetch':10
                }
            }
        })
        return True
