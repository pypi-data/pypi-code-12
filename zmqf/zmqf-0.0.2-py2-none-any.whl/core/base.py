#coding=utf-8
'''
Created on 2016年3月3日
'''
import zmq
from exception import UnimplementedException, Zmqf404
import logging
import json
__author__ = 'chenjian'

class ZmqfPattern(object):
    '''
    '''
    
    MPBS = 'MPBS'# Multi Publisher -- Broker -- Multi Subscriber
    MPUP = 'MPUP'# Multi Pusher -- Broker -- Multi Puller
    MRER = 'MRER'# Multi Req -- Broker -- Multi Rep

class ZmqfApplication(object):
    '''
    classdocs
    '''


    def __init__(self, *args, **kwargs):
        '''
        Constructor
        '''
        
        self.handlers = dict()
        for uri, hdr in kwargs['handlers']:
            uri = '/%s/'% uri.strip('/')
            if uri == '//': uri = '/'
            self.handlers[uri] = hdr

class ZmqfServer(object):
    '''
    '''
    
    def __init__(self, application, addr, pattern=ZmqfPattern.MPUP):
        self.application = application
        self.addr = addr
        self.pattern = pattern
        
        
    def start(self):
        '''
        '''
        
        context = zmq.Context()
        
        if self.pattern == ZmqfPattern.MPBS:
            socket_type = zmq.SUB  # @UndefinedVariable
            subscriber = context.socket(socket_type)  # @UndefinedVariable
            subscriber.connect(self.addr)
            subscriber.setsockopt(zmq.SUBSCRIBE, b"")  # @UndefinedVariable
        elif self.pattern == ZmqfPattern.MPUP:
            socket_type = zmq.PULL  # @UndefinedVariable
            subscriber = context.socket(socket_type)  # @UndefinedVariable
            subscriber.connect(self.addr)

        while True:
            try:
                [uri, headers, body] = subscriber.recv_multipart()
                
                uri = '/%s/'% uri.strip('/')
                if uri == '//': uri = '/'
                handler_cls = self.application.handlers[uri]
                
                if not handler_cls:
                    raise Zmqf404()
                
                # request对象
                # TODO: 修改类名
                request = ZmqfRequest(uri=uri, headers=headers, body=body)
                # 实例化handler
                handler = handler_cls(self.application, request)
                # handle
                handler.handle()
            except Exception, e:
                logging.exception(e)
            
class ZmqfRequest(object):
    '''
    '''
    
    def __init__(self, **kwargs):
        '''
        '''
        
        self.uri = kwargs['uri']
        self.headers = json.loads(kwargs['headers'])
        self.body = kwargs['body']
        
class ZmqfHandler(object):
    '''
    '''
    
    def __init__(self, application, request, **kwargs):
        '''
        '''
        
        try:
            super(ZmqfHandler, self).__init__(application, request)
        except:
            try:
                super(ZmqfHandler, self).__init__()
            except:
                pass
        self.application = application
        self.request = request
        
    def handle(self):
        '''
        '''
        
        raise UnimplementedException()
