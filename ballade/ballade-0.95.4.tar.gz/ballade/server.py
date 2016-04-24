import os
import base64
import re
import struct
import socket
import logging
from urllib.parse import urlparse, urlunparse
from collections import OrderedDict

import tornado.options
import tornado.ioloop
import tornado.tcpserver
import tornado.iostream
import tornado.web

from .utils import *


class Connector:

    scheme = None

    def __init__(self, netloc=None, path=None):
        self.netloc = netloc
        self.path = path

    @classmethod
    def accept(cls, scheme):
        return scheme == cls.scheme

    def connect(self, host, port, callback):
        raise NotImplementedError()

    @classmethod
    def get(cls, url, ipv6_accessible):
        parts = urlparse(url)
        for sub_cls in subclasses(cls):
            if sub_cls.accept(parts.scheme):
                if parts.scheme == 'direct':
                    return sub_cls(parts.netloc, parts.path, ipv6_accessible)
                else:
                    return sub_cls(parts.netloc, parts.path)
        raise NotImplementedError('Unsupported scheme', parts.scheme)

    def __str__(self):
        return self.__class__.scheme + '://' + self.netloc


class RejectConnector(Connector):

    scheme = 'reject'

    def __init__(self, netloc, path=None):
        Connector.__init__(self, netloc, path)

    def connect(self, host, port, callback):
        callback(RejectConnector)

    @classmethod
    def write(cls, _):
        pass

    @classmethod
    def read_until_close(cls, req_callback, _):
        req_callback(b'HTTP/1.1 410 Gone\r\n\r\n')
        req_callback(b'')


class DirectConnector(Connector):

    scheme = 'direct'

    def __init__(self, netloc, path=None, ipv6_accessible=None):
        Connector.__init__(self, netloc, path)
        self.scheme = 'direct'
        self.ipv6_accessible = ipv6_accessible

    def connect(self, host, port, callback):
        def on_close():
            callback(None)

        def on_connected():
            stream.set_close_callback(None)
            callback(stream)

        if has_ipv6_address(host) and self.ipv6_accessible:
            s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        stream = tornado.iostream.IOStream(s)
        stream.set_close_callback(on_close)
        stream.connect((host, port), on_connected)


class Socks5Connector(Connector):

    scheme = 'socks5'

    def __init__(self, netloc, path=None):
        Connector.__init__(self, netloc, path)
        self.socks5_server, self.socks5_port = hostport_parser(netloc, 1080)

    def connect(self, host, port, callback):

        def socks5_close():
            callback(None)

        def socks5_response(data):
            # Response OK
            if data[3] == 0x00:
                callback(stream)
            else:
                callback(None)

        def socks5_connected():
            try:
                # Connect: 1 method no auth
                stream.write(b'\x05\x01\x00')
                # Request: remote resolve
                stream.write(b'\x05' + b'\x01' + b'\x00' + b'\x03' + chr(len(host)).encode() +
                             host + struct.pack(">H", port))
                # 2 bytes for auth response, 10 bytes for request response
                stream.read_bytes(2+10, socks5_response)
            except tornado.iostream.StreamClosedError:
                socks5_close()

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        stream = tornado.iostream.IOStream(s)
        stream.set_close_callback(socks5_close)
        stream.connect((self.socks5_server, self.socks5_port), socks5_connected)


class HttpConnector(Connector):

    scheme = 'http'

    def __init__(self, netloc, path=None):
        Connector.__init__(self, netloc, path)
        auth, host = netloc_parser(netloc)
        self.auth = base64.encodebytes(auth.encode()).strip() if auth else None
        self.http_server, self.http_port = hostport_parser(host, 3128)

    def connect(self, host, port, callback):

        def http_close():
            callback(None)

        def http_response(data):
            stream.set_close_callback(None)
            code = int(data.split()[1])
            if code == 200:
                callback(stream)
            else:
                callback(None)

        def http_connected():
            try:
                stream.write(b'CONNECT ' + host + b':' + str(port).encode() + b' HTTP/1.1\r\n')
                stream.write(b'Host: ' + host + b':' + str(port).encode() + b'\r\n')
                if self.auth:
                    stream.write(
                        b'Proxy-Authorization: Basic ' + self.auth + b'\r\n')
                stream.write(b'Proxy-Connection: Keep-Alive\r\n')
                stream.write(b'\r\n')
                stream.read_until(b'\r\n\r\n', http_response)
            except tornado.iostream.StreamClosedError:
                http_close()

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        stream = tornado.iostream.IOStream(s)
        stream.set_close_callback(http_close)
        stream.connect((self.http_server, self.http_port), http_connected)


class RulesConnector(Connector):

    scheme = 'rules'

    def __init__(self, netloc=None, path=None, config=None):
        Connector.__init__(self, netloc, path)
        self.ipv6_accessible = is_ipv6_accessible(config)
        logging.info("IPv6 direct" + "enabled" if self.ipv6_accessible else "disabled")
        self.rules = None
        self._connectors = {}
        self.load_rules()
        #self._modify_time = None
        #self.check_update()
        #tornado.ioloop.PeriodicCallback(self.check_update, 1000).start()

    def load_rules(self):
        self.rules = []
        with open(self.path) as f:
            for l in f:
                l = l.strip()
                if not l or l.startswith('#'):
                    continue
                try:
                    rule_pattern, upstream = l.split()
                    Connector.get(upstream, self.ipv6_accessible)
                    rule_pattern = re.compile(rule_pattern, re.I)
                except Exception as e:
                    logging.error('Invalid rule: %s', l)
                    logging.error(e)
                    continue
                self.rules.append([rule_pattern, upstream])
        self.rules.append(['.*', 'direct://'])

    def check_update(self):
        modified = os.stat(self.path).st_mtime
        if modified != self._modify_time:
            logging.info('Loading %s', self.path)
            self._modify_time = modified
            self.load_rules()

    @classmethod
    def accept(cls, scheme):
        return scheme == 'rules'

    def connect(self, host, port, callback):
        s = host.decode() + ':' + str(port)
        for rule, upstream in self.rules:
            if re.match(rule, s):
                if upstream not in self._connectors:
                    self._connectors[upstream] = Connector.get(upstream, self.ipv6_accessible)
                logging.info("Use " + self._connectors[upstream].__str__() + " to connect")
                self._connectors[upstream].connect(host, port, callback)
                break
        else:
            raise RuntimeError('no available rule for %s' % s)


class ProxyHandler:

    def __init__(self, stream, address, connector):
        self.connector = connector

        self.incoming = stream
        self.incoming.read_until(b'\r\n', self.on_method)

        self.method = None
        self.url = None
        self.ver = None
        self.headers = None
        self.outgoing = None

        self.request_ip, self.request_port = address[0], address[1]

    def on_method(self, method):
        try:
            self.method, self.url, self.ver = method.strip().split()
        except ValueError:
            logging.error("This method is not supported.")
        self.incoming.read_until(b'\r\n\r\n', self.on_headers)
        logging.debug(method.strip().decode())

    def on_connected(self, outgoing):
        if outgoing:
            try:
                path = urlunparse((b'', b'') + urlparse(self.url)[2:])
                outgoing.write(b' '.join((self.method, path, self.ver)) + b'\r\n')
                for k, v in self.headers.items():
                    outgoing.write(k + b': ' + v + b'\r\n')
                outgoing.write(b'\r\n')
                writer_in = write_to(self.incoming)
                if b'Content-Length' in self.headers:
                    self.incoming.read_bytes(
                        int(self.headers[b'Content-Length']), outgoing.write, outgoing.write)
                outgoing.read_until_close(writer_in, writer_in)
            except tornado.iostream.StreamClosedError:
                self.incoming.close()
                outgoing.close()
        else:
            self.incoming.close()

    def on_connect_connected(self, outgoing):
        if outgoing:
            try:
                self.incoming.write(b'HTTP/1.1 200 Connection Established\r\n\r\n')
            except tornado.iostream.StreamClosedError:
                self.incoming.close()
                outgoing.close()
            pipe(self.incoming, outgoing)
        else:
            self.incoming.close()

    def on_headers(self, headers_buffer):
        self.headers = OrderedDict(header_parser(headers_buffer))
        logging.info(self.request_ip + ':' + str(self.request_port) + ' -> ' +
                     ' '.join([self.method.decode(),
                               self.url.decode(),
                               self.ver.decode()]))
        if self.method == b'CONNECT':
            host, port = hostport_parser(self.url, 443)
            self.outgoing = self.connector.connect(
                host, port, self.on_connect_connected)
        else:
            if b'Proxy-Connection' in self.headers:
                del self.headers[b'Proxy-Connection']
            # self.headers[b'Connection'] = b'close'
            if b'Host' in self.headers:
                host, port = hostport_parser(self.headers[b'Host'], 80)
                self.outgoing = self.connector.connect(
                    host, port, self.on_connected)
            else:
                self.incoming.close()


class ProxyServer(tornado.tcpserver.TCPServer):

    def __init__(self, connector=None):
        tornado.tcpserver.TCPServer.__init__(self)
        self.connector = connector or DirectConnector()

    def handle_stream(self, stream, address):
        ProxyHandler(stream, address, self.connector)
