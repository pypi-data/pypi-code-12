#coding=utf-8
'''
Created on 2016年3月3日
'''
from zmqf.core.base import ZmqfHandler, ZmqfApplication, ZmqfServer, ZmqfPattern
__author__ = 'chenjian'

class MainHanlder(ZmqfHandler):
    '''
    '''
    
    def __init__(self, *args, **kwargs):
        ZmqfHandler.__init__(self, *args, **kwargs)
        
    def handle(self):
        print self.request.uri, self.request.headers, self.request.body


class App(ZmqfApplication):
    '''
    '''
    
    def __init__(self):
        
        
        ZmqfApplication.__init__(self, 
                             handlers = [
                                         (r'/', MainHanlder),
                                         (r'/v1/', MainHanlder)
                                         ]
                             )
        
def main(broker='tcp://127.0.0.1:5556'):
    ZmqfServer(App(), broker, pattern=ZmqfPattern.MPUP).start()

if __name__ == '__main__':
    main()
    