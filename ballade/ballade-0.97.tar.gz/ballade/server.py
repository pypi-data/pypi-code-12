import os
import base64
import re
import struct
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

    def __init__(self, netloc=None, config=None):
        self.netloc = netloc
        self.config = config

    @classmethod
    def accept(cls, scheme):
        return scheme == cls.scheme

    def connect(self, host, port, callback):
        raise NotImplementedError()

    @classmethod
    def get(cls, url, config):
        parts = urlparse(url)
        for sub_cls in subclasses(cls):
            if sub_cls.accept(parts.scheme):
                return sub_cls(parts.netloc, config)
        raise NotImplementedError('Unsupported scheme', parts.scheme)

    def __str__(self):
        return self.__class__.scheme + '://' + netloc_parser(self.netloc)[1]


class RejectConnector(Connector):

    scheme = 'reject'

    def __init__(self, netloc, config=None):
        Connector.__init__(self, netloc, config)

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

    def __init__(self, netloc, config=None):
        Connector.__init__(self, netloc, config)
        self.is_ipv6_accessible = config.is_ipv6_accessible

    def connect(self, host, port, callback):
        def on_close():
            callback(None)

        def on_connected():
            stream.set_close_callback(None)
            callback(stream)

        if has_ipv6_address(host) and self.is_ipv6_accessible:
            s = get_socket(ipv6=True)
        else:
            s = get_socket(ipv6=False)
        stream = tornado.iostream.IOStream(s)
        stream.set_close_callback(on_close)
        stream.connect((host, port), on_connected)


class FilterConnector(DirectConnector):

    scheme = 'filter'

    def __init__(self, netloc, config=None):
        DirectConnector.__init__(self, netloc, config)
        self._connectors = {}

    def connect(self, host, port, callback):
        if has_ipv6_address(host) and self.is_ipv6_accessible:
            logging.debug("It's a ipv6 host, use direct")
            upstream = 'direct://'
        elif is_host_match_ip_list(host, ['10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16', '100.64.0.0/10']):
            logging.debug("It's a private host, use direct")
            upstream = 'direct://'
        elif is_host_match_ip_list(host, self.config.china_ip_list):
            logging.debug("It's a chinese host, use direct")
            upstream = 'direct://'
        else:
            upstream = self.config.filter_upstream
            logging.debug("It's a foreign host, use filter profile")
        self._connectors[upstream] = Connector.get(upstream, self.config)
        self._connectors[upstream].connect(host, port, callback)


class Socks5Connector(Connector):

    scheme = 'socks5'

    def __init__(self, netloc, config=None):
        Connector.__init__(self, netloc, config)
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

    def __init__(self, netloc, config=None):
        Connector.__init__(self, netloc, config)
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
                stream.write(b'host: ' + host + b':' + str(port).encode() + b'\r\n')
                if self.auth:
                    stream.write(
                        b'proxy-authorization: Basic ' + self.auth + b'\r\n')
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

    def __init__(self, netloc=None, config=None):
        Connector.__init__(self, netloc, config)
        self.regex_path = config.regex_path
        self.ipv6_accessible = config.is_ipv6_accessible
        logging.info("IPv6 direct " + ("enabled" if self.ipv6_accessible else "disabled"))
        logging.info("HTTP proxy authentication " + ("enabled" if config.proxy_auth else "disabled"))
        self.rules = None
        self._connectors = {}
        self.load_rules()
        #self._modify_time = None
        #self.check_update()
        #tornado.ioloop.PeriodicCallback(self.check_update, 1000).start()

    def load_rules(self):
        self.rules = []
        with open(self.regex_path) as f:
            for l in f:
                l = l.strip()
                if not l or l.startswith('#'):
                    continue
                try:
                    rule_pattern, upstream = l.split()
                    Connector.get(upstream, self.config)
                    rule_pattern = re.compile(rule_pattern, re.I)
                except Exception as e:
                    logging.error('Invalid rule: %s', l)
                    logging.error(e)
                    continue
                self.rules.append([rule_pattern, upstream])
        self.rules.append(['.*', 'direct://'])

    def check_update(self):
        modified = os.stat(self.regex_path).st_mtime
        if modified != self._modify_time:
            logging.info('Loading %s', self.regex_path)
            self._modify_time = modified
            self.load_rules()

    def connect(self, host, port, callback):
        s = host.decode() + ':' + str(port)
        for rule, upstream in self.rules:
            if re.match(rule, s):
                if upstream not in self._connectors:
                    self._connectors[upstream] = Connector.get(upstream, self.config)
                logging.info("Use " + self._connectors[upstream].__str__() + " to connect " + s)
                self._connectors[upstream].connect(host, port, callback)
                break
        else:
            raise RuntimeError('No available rule for %s' % s)


class ProxyHandler:

    def __init__(self, stream, address, connector, auth):
        self.connector = connector

        self.inbound = stream
        self.inbound.read_until(b'\r\n', self.on_request_line)

        self.client_ip, self.client_port = address[0], address[1]

        self.method = None
        self.request_url = None
        self.version = None
        self.header_dict = None
        self.request_line_buffer = None
        self.header_buffer = None
        self.outbound = None

        self.auth = auth

    def on_request_line(self, request_line_buffer):
        self.request_line_buffer = request_line_buffer
        try:
            self.method, self.request_url, self.version = request_line_buffer.strip().split()
        except ValueError:
            logging.warning("This request is not compatible with HTTP protocol.")
            self.inbound.close()
            return
        self.inbound.read_until(b'\r\n\r\n', self.on_header)

    def on_connected(self, outbound):
        if outbound:
            try:
                outbound.write(self.request_line_buffer)
                outbound.write(header_dict_parser(self.header_dict))
                pipe(self.inbound, outbound)
            except tornado.iostream.StreamClosedError:
                self.inbound.close()
                outbound.close()
        else:
            self.inbound.close()

    def on_connect_connected(self, outbound):
        if outbound:
            try:
                self.inbound.write(b'HTTP/1.1 200 Connection Established\r\n\r\n')
                pipe(self.inbound, outbound)
            except tornado.iostream.StreamClosedError:
                self.inbound.close()
                outbound.close()
        else:
            self.inbound.close()

    def on_header(self, header_buffer):
        self.header_buffer = header_buffer
        self.header_dict = OrderedDict(header_parser(header_buffer))
        logging.info(self.client_ip + ':' + str(self.client_port) + ' -> ' +
                     ' '.join([self.method.decode(),
                               self.request_url.decode(),
                               self.version.decode()]))
        if self.auth:
            if b'proxy-authorization' in self.header_dict.keys() and self.auth == self.header_dict[b'proxy-authorization'].split()[1]:
                pass
            else:
                self.inbound.write(self.version + b' 407 Proxy Authorization Required\r\n')
                self.inbound.write(b'proxy-authenticate: Basic realm=\"Ballade HTTP Proxy\"\r\n\r\n')
                return

        if self.method == b'CONNECT':
            host, port = hostport_parser(self.request_url, 443)
            self.outbound = self.connector.connect(host, port, self.on_connect_connected)
        else:
            is_header_connection_close = True if self.version == b'HTTP/1.0' else False
            if (b'proxy-connection' in self.header_dict.keys() and self.header_dict[b'proxy-connection'].lower() == b'close') or (b'connection' in self.header_dict.keys() and self.header_dict[b'connection'].lower() == b'close'):
                is_header_connection_close = True
            else:
                is_header_connection_close = False
            for header in [b'proxy-connection', b'proxy-authenticate', b'connection']:
                if header in self.header_dict.keys():
                    del self.header_dict[header]
            if is_header_connection_close:
                self.header_dict[b'connection'] = b'close'
            else:
                self.header_dict[b'connection'] = b'keep-alive'
            host, port = hostport_parser(self.header_dict[b'host'], 80)
            self.outbound = self.connector.connect(host, port, self.on_connected)



class ProxyServer(tornado.tcpserver.TCPServer):

    def __init__(self, connector=None, config=None):
        tornado.tcpserver.TCPServer.__init__(self)
        self.connector = connector
        self.config = config
        self.auth = self.config.proxy_auth

    def handle_stream(self, stream, address):
        set_socket(stream.socket)
        ProxyHandler(stream, address, self.connector, self.auth)
