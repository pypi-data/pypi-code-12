# -*- coding: utf-8 -*-

import json
from pyrocumulus.converters import get_converter
from pyrocumulus.parsers import get_parser
from pyrocumulus.utils import fqualname, import_class
import tornado
from tornado import gen
import zmq
from zmq.eventloop import zmqstream
from jaobi.cache import get_cache
from jaobi.utils import log


class ZMQBase:

    def __init__(self, url, socket_type):
        self.url = url
        self.context = zmq.Context()
        self.socket = self.context.socket(socket_type)
        self.stream = None
        self.is_connected = False

    def connect(self, bind=False):
        if not self.is_connected:
            if bind:
                self.socket.bind(self.url)
            else:
                self.socket.connect(self.url)

            self.stream = zmqstream.ZMQStream(self.socket)
            self.is_connected = True

    def disconnect(self):
        if self.is_connected:
            self.socket.disconnect(self.url)
            self.is_connected = False


class ZMQServer(ZMQBase):

    def __init__(self, url):
        super().__init__(url, zmq.PULL)

    def connect(self):
        super().connect(bind=True)
        self.stream.on_recv(self.on_recv)

    def disconnect(self):
        self.stream.on_recv(None)
        super().disconnect()

    @gen.coroutine
    def dict2obj(self, mydict, objtype):
        parser = get_parser(objtype)
        parsed = yield parser.parse()
        references = parsed['reference_fields']
        for name, cls in references.items():
            if name in mydict.keys():
                mydict[name] = cls(**mydict[name])

        obj = objtype(**mydict)
        return obj

    def on_recv(self, multipart_message):
        message = ''.join([p.decode() for p in multipart_message])
        mydict = json.loads(message)
        type_fqualname = mydict['type']
        objtype = import_class(type_fqualname)
        body = mydict['body']

        loop = tornado.ioloop.IOLoop.instance()

        def add2cache(future):
            obj = future.result()
            cache = get_cache()
            loop.spawn_callback(cache.add, obj)

        future = self.dict2obj(body, objtype)
        loop.add_future(future, add2cache)
        return future


class ZMQClient(ZMQBase):

    def __init__(self, url):
        super().__init__(url, zmq.PUSH)

    @gen.coroutine
    def obj2dict(self, obj):
        converter = get_converter(obj, max_depth=1)
        mydict = yield converter.to_dict()
        mydict = converter.sanitize_dict(mydict)

        return mydict

    @gen.coroutine
    def send(self, obj):
        objdict = yield self.obj2dict(obj)
        final_dict = {'body': objdict,
                      'type': fqualname(type(obj))}

        self.stream.send_json(final_dict)
