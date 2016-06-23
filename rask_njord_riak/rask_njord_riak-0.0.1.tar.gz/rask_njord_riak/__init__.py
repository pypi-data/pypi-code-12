from rask.base import Base

__all__ = ['Riak']

class Riak(Base):
    def __init__(self,rmq):
        self.rmq = rmq

    def draft(self):
        pass
