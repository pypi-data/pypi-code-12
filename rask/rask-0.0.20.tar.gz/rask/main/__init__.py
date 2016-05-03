from rask.base import Base

__all__ = ['Main']

class Main(Base):
    def __init__(self):
        self.before()
        self.ioengine.loop.add_callback(self.after)
        self.ioengine.start()

    def after(self):
        pass
        
    def before(self):
        pass
