#coding=utf-8
'''
Created on 2016年3月3日
'''
import zmq
from base import ZmqfPattern
__author__ = 'chenjian'



class ZmqfBroker(object):
    '''
    classdocs
    '''
    

    def __init__(self, frontend, backend, pattern=ZmqfPattern.MPUP):
        '''
        Constructor
        :param frontend_port: 
        :param backend_port: 
        '''
        
        self.frontend = frontend
        self.backend = backend
        self.pattern = pattern
        
        self.pattern_mapping = {
                       ZmqfPattern.MPBS: self._start_mpbs_broker,
                       ZmqfPattern.MPUP: self._start_mpup_broker,
                       ZmqfPattern.MRER: self._start_mrer_broker,
                       }
    
    def start(self):
        '''
        '''
        
        func = self.pattern_mapping[self.pattern]
        
        func()
        
    def _start_mpbs_broker(self):
        '''
        Multi-Publisher-Multi-Subscriber
        '''
        
        context = zmq.Context()
        front = context.socket(zmq.SUB)  # @UndefinedVariable
        front.setsockopt(zmq.SUBSCRIBE, b"")  # @UndefinedVariable
        front.bind(self.frontend)
        
        back = context.socket(zmq.PUB)  # @UndefinedVariable
        back.bind(self.backend)
        
        zmq.proxy(front, back)  # @UndefinedVariable
        
    def _start_mpup_broker(self):
        '''
        Multi-Pusher-Mutli-Puller
        '''
        
        context = zmq.Context()
        front = context.socket(zmq.PULL)  # @UndefinedVariable
        front.bind(self.frontend)
        
        back = context.socket(zmq.PUSH)  # @UndefinedVariable
        back.bind(self.backend)
        
        zmq.proxy(front, back)  # @UndefinedVariable
        
    def _start_mrer_broker(self):
        '''
        Multi-Req-Mutli-Rep
        '''
        
        zc = zmq.Context()

        front = zc.socket(zmq.ROUTER)  # @UndefinedVariable
        front.bind(self.frontend)

        back = zc.socket(zmq.DEALER)  # @UndefinedVariable
        back.bind(self.backend)

        zmq.proxy(front, back)  # @UndefinedVariable

        