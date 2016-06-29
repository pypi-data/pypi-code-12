#coding=utf-8
'''
Created on 2016年6月28日
'''
from zmqf.core.base import ZmqfPattern
from zmqf.utils import zmqf_utils
__author__ = 'chenjian'

#coding=utf-8
'''
Created on 2016年3月3日
'''
import zmq
import time
import json as _json
import logging
__author__ = 'chenjian'

def request(url, data=None, json=None, headers=None, pattern=ZmqfPattern.MPUP):
    '''
    '''
    
    protocol, host, port, uri = zmqf_utils.parse_url(url)
    
    client = ZmqfClient('%s://%s:%s'% (protocol, host, port), pattern)
    
    res = client.request(uri, data, json, headers)
    
    client.close()
    
    return res
    
    
class ZmqfClient(object):
    
    def __init__(self, url, pattern=ZmqfPattern.MPUP):
        '''
        '''
        
        protocol, host, port, uri = zmqf_utils.parse_url(url)
        
        self.context   = zmq.Context()
        self.pattern = pattern
        
        if self.pattern == ZmqfPattern.MPBS:
            self.publisher = self.context.socket(zmq.PUB)  # @UndefinedVariable
            self.publisher.connect('%s://%s:%s'% (protocol, host, port))
            time.sleep(0.25)
        elif self.pattern == ZmqfPattern.MPUP:
            self.publisher = self.context.socket(zmq.PUSH)  # @UndefinedVariable
            self.publisher.connect('%s://%s:%s'% (protocol, host, port))
        
    def request(self, uri, data=None, json=None, headers=None):
        '''
        :param uri: like /a/b/
        '''
        
        _uri = '/' + uri.strip('/') + '/'
        if _uri == '//': _uri = '/'
        
        _headers = {
                # only for fun for now
               "Content-Type" : "text/html",
               }
    
        if headers:
            _headers.update(headers)
        
        if not data:
            data = ''
        
        if json:
            _body = _json.dumps(json)
        else:
            _body = data
    
        self.publisher.send_multipart([bytes(_uri), bytes(_json.dumps(_headers)), bytes(_body)])
        
        return None
    
    def close(self):
        try:
            self.publisher.close()
            self.context.term()
        except Exception, e:
            logging.warn(e)
    
    def __del__(self):
        try:
            self.publisher.close()
            self.context.term()
        except:
            pass
        
# request('tcp://127.0.0.1:5557/b/c', 'aaa', headers={'a':1}, pattern=ZmqfPattern.MPUP)