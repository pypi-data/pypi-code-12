from sockjs.tornado import conn, session
from sockjs.tornado.transports import base

print '\n\ninvoked multiplex.py\n'



class ChannelSession(session.BaseSession):
    print '\n\nInvoked ChannelSession\n'
    def __init__(self, conn, server, base, name):
        print '\ninside ChannelSession __init__()'
        print 'conn : ',conn
        print 'server : ',server
        print 'base : ',base
        print 'name : ',name
        print "invoking super(ChannelSession,self).__init__(conn,server)"
        super(ChannelSession, self).__init__(conn, server)
        print 'super(ChannelSession,self).__init__(conn,server) invoked successfully'

        self.base = base
        self.name = name
        print 'self.base : ',self.base
        print 'self.name : ',self.name
        print 'returning from ChannelSession __init__()'

    def send_message(self, msg, stats=True, binary=False):
        print '\ninside ChannelSession send_message()'
        # TODO: Handle stats
        print 'self.base : ',self.base
        print 'self.name : ',self.name
        print 'msg : ',msg
        print "invoking self.base.send(msg+self.name,msg)"
        self.base.send('msg,' + self.name + ',' + msg)
        print "self.base.send(msg+self.name,msg) invoked successfully"
        print 'returning form ChannelSession send_message()'

    def on_message(self, msg):
        print '\ninside ChannelSession on_message()'
        print 'self.conn : ',self.conn
        print 'msg : ',msg
        print 'invoking self.conn.on_message(msg)'
        self.conn.on_message(msg)
        # self.base.send_message
        print 'self.base.on_message(msg) invoked successfully'
        print 'returning from ChannelSession on_message()'

    def on_close(self, code=3000, message='Go away!'):
        print '\ninside ChannelSession on_close()'
        print 'self.base : ',self.base
        print 'self.name : ',self.name
        print 'self.conn : ',self.conn
        print 'invoking self.conn.on_close(msg)'
        self.conn.on_close(msg)
        print ''
        print 'invoking self.base.send(uns + self.name)'
        self.base.send('uns,' + self.name)
        print 'self.base.send(uns + self.name) invoked successfully'
        print 'code : ',code
        print 'message : ',message
        print 'invoking self._close(code,message)'
        self._close(code, message)
        print 'self._close(code,message) invoked successfully'
        print 'returning from ChannelSession on_close'

    # Non-API version of the close, without sending the close message
    def _close(self, code=3000, message='Go away!'):
        print '\ninside ChannelSession _close()'
        print 'code : ',code
        print 'message : ',message
        print 'invoking super(ChannelSession,self).close(code,message)'
        super(ChannelSession, self).close(code, message)
        print 'super(ChannelSession,self).close(code,message) invoked successfully'
        print 'returning from ChannelSession _close()'


class DummyHandler(base.BaseTransportMixin):

    print '\n\n invoked DummyHandler\n'
    name = 'multiplex'


    def __init__(self, conn_info):
        print '\ninside DummyHandler __init__()'
        self.conn_info = conn_info
        print 'self.conn_info : ',self.conn_info
        print 'returning from DummyHandler __init__'

    def get_conn_info(self):
        print '\ninside DummyHandler get_conn_info()'
        print "returning self.conn_info : ",self.conn_info
        return self.conn_info


class MultiplexConnection(conn.SockJSConnection):
    print '\n\nInvoked multiplex.MultiplexConnection\n'
    print "current channels : "
    channels = dict()
    print channels

    def on_open(self, info):
        print '\ninside MultiplexConnection on_open'
        self.endpoints = dict()
        print "endpoints : ",self.endpoints
        self.handler = DummyHandler(self.session.conn_info)
        print " self.handler : ",self.handler
        print 'returning from MultiplexConnection on_open'

    def on_message(self, msg):
        
        print "\ninside MultiplexConnection on_message function"
	
    	print " pre parts msg : ",msg
    	parts = msg.split(',', 2)
    	print "post Parts  msg : ",parts
        op, chan = parts[0], parts[1]

        print 'op : ',op
        print 'chan : ',chan

        print "current channels : ",self.channels
        print 'current endpoints : ',self.endpoints

        if chan not in self.channels:
            print ' chan not in self.channels'
            return

        if chan in self.endpoints:
            print 'chan in self.endpoints'
            session = self.endpoints[chan]
            print 'session : ',session

            if op == 'uns':
                print 'op==uns'
                print 'current self.endpoints : ',self.endpoints
                del self.endpoints[chan]
                print 'updates self.endpoints : ',self.endpoints
                print 'invoking session._close()'
                session._close()
                print 'session._close invokes sucsessfully'
            elif op == 'msg':
                print 'op==msg'
                print 'current self.endpoints : ',self.endpoints
                print "current parts : ",parts
                print 'invoking session.on_message(parts[2])'
                session.on_message(parts[2])
                print 'session.on_message(parts[2]) invokes sucsessfully'
        else:
            print 'chan not in self.endpoints'
            if op == 'sub':
                print 'op==sub'
                print 'self.channels[chan] : ',self.channels[chan]
                print 'self.session.server : ',self.session.server
                print 'chan : ',chan
                print 'invokeing session=ChannelSession'
                session = ChannelSession(self.channels[chan],
                                         self.session.server,
                                         self,
                                         chan)
                print 'invoked session=channelSession successfully'
                print 'session : ',session
                print 'setting session.set_handler(self.handler)'
                session.set_handler(self.handler)
                print 'session.set_handler(self.handler) invoked successfully'
                print 'invoking session.verify_state()'
                session.verify_state()
                print 'session.verify_state invoked successfully'

                self.endpoints[chan] = session
        print 'returning from MultiplexConnection on_message'

    def on_close(self):
        print "\ninside MultiplexConnection on_close function"
        print 'current self.endpoints : ',self.endpoints
        print 'starting for loop : for chan in self.endpoints'
        for chan in self.endpoints:
            print 'chan : ',chan
            print 'self.endpoints[chan] : ',self.endpoints[chan]
            print 'invoking self.endpoints[chan]._close()'
            self.endpoints[chan].on_close()
        print 'returning from MultiplexConnection on_close'

    @classmethod
    def get(cls, **kwargs):
        print '\n inside MultiplexConnection @classmethod get()'
        res= type('MultiplexRouter', (MultiplexConnection,), dict(channels=kwargs))
        print 'returning value is : ',res
        return res
