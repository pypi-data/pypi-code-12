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
            s = get_socket(ipv6=True)
        else:
            s = get_socket(ipv6=False)
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

        s = get_socket()
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

        s = get_socket()
        stream = tornado.iostream.IOStream(s)
        stream.set_close_callback(http_close)
        stream.connect((self.http_server, self.http_port), http_connected)


class RulesConnector(Connector):

    scheme = 'rules'

    def __init__(self, netloc=None, path=None, config=None):
        Connector.__init__(self, netloc, path)
        self.ipv6_accessible = is_ipv6_accessible(config)
        logging.info("IPv6 direct " + "enabled" if self.ipv6_accessible else "disabled")
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

    def connect(self, host, port, callback):
        s = host.decode() + ':' + str(port)
        for rule, upstream in self.rules:
            if re.match(rule, s):
                if upstream not in self._connectors:
                    self._connectors[upstream] = Connector.get(upstream, self.ipv6_accessible)
                logging.info("Use " + self._connectors[upstream].__str__() + " to connect " + s)
                self._connectors[upstream].connect(host, port, callback)
                break
        else:
            raise RuntimeError('No available rule for %s' % s)


class ProxyHandler:

    def __init__(self, stream, address, connector):
        self.connector = connector

        self.inbound = stream
        self.inbound.read_until(b'\r\n', self.on_start_line)

        self.client_ip, self.client_port = address[0], address[1]

        self.method = None
        self.request_url = None
        self.version = None
        self.header_dict = None
        self.outbound = None

    def on_start_line(self, method):
        try:
            self.method, self.request_url, self.version = method.strip().split()
        except ValueError:
            logging.error("This is not HTTP protocol.")
        self.inbound.read_until(b'\r\n\r\n', self.on_header)

    def on_connected(self, outbound):
        if outbound:
            try:
                path = urlunparse((b'', b'') + urlparse(self.request_url)[2:])
                outbound.write(b' '.join((self.method, path, self.version)) + b'\r\n')
                for k, v in self.header_dict.items():
                    outbound.write(k + b': ' + v + b'\r\n')
                outbound.write(b'\r\n')
                writer_in = write_to(self.inbound)
                if b'Content-Length' in self.header_dict:
                    self.inbound.read_bytes(
                        int(self.header_dict[b'Content-Length']), outbound.write, outbound.write)
                outbound.read_until_close(writer_in, writer_in)
            except tornado.iostream.StreamClosedError:
                self.inbound.close()
                outbound.close()
        else:
            self.inbound.close()

    def on_connect_connected(self, outbound):
        if outbound:
            try:
                self.inbound.write(b'HTTP/1.1 200 Connection Established\r\n\r\n')
            except tornado.iostream.StreamClosedError:
                self.inbound.close()
                outbound.close()
            pipe(self.inbound, outbound)
        else:
            self.inbound.close()

    def on_header(self, headers_buffer):
        self.header_dict = OrderedDict(header_parser(headers_buffer))
        logging.info(self.client_ip + ':' + str(self.client_port) + ' -> ' +
                     ' '.join([self.method.decode(),
                               self.request_url.decode(),
                               self.version.decode()]))
        if self.method == b'CONNECT':
            host, port = hostport_parser(self.request_url, 443)
            self.outbound = self.connector.connect(
                host, port, self.on_connect_connected)
        else:
            for header in [b'Proxy-Connection', b'Proxy-Authenticate']:
                if header in self.header_dict.keys():
                    del self.header_dict[header]
                self.header_dict[b'Connection'] = b'Keep-Alive'
            if b'Host' in self.header_dict:
                host, port = hostport_parser(self.header_dict[b'Host'], 80)
                self.outbound = self.connector.connect(
                    host, port, self.on_connected)
            else:
                self.inbound.close()


class ProxyServer(tornado.tcpserver.TCPServer):

    def __init__(self, connector=None):
        tornado.tcpserver.TCPServer.__init__(self)
        self.connector = connector

    def handle_stream(self, stream, address):
        # 采用TCP Socket的keepalive
        set_socket(stream.socket)
        ProxyHandler(stream, address, self.connector)
