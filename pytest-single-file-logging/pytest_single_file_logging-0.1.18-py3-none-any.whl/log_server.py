import struct
import pickle
import logging
import json
import socket
from logging.config import dictConfig
from gevent.server import StreamServer
from logging.handlers import SocketHandler, DEFAULT_TCP_LOGGING_PORT


DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_CONFIG_FILE = 'testing.log'


class LogServer(StreamServer):
    def __init__(self, listener, handle=None, backlog=None, spawn='default', file_name='log.config', **ssl_args):
        self.log_info = self._get_log_info(file_name)
        self.logger = self.configure_logging()
        super().__init__(listener, handle, backlog, spawn, **ssl_args)

    def _get_log_info(self, file_name):
        try:
            with open(file_name) as f:
                _log_info = f.read()
        except FileNotFoundError:
            _log_info = None
        return _log_info

    def configure_logging(self):
        if self.log_info:
            try:
                info = json.loads(self.log_info)
                dictConfig(info)
            except (ValueError, TypeError, AttributeError, ImportError) as e:
                print(e)
                logging.basicConfig(filename=DEFAULT_CONFIG_FILE, level=DEFAULT_LOG_LEVEL)

        else:
            logging.basicConfig(filename=DEFAULT_CONFIG_FILE, level=DEFAULT_LOG_LEVEL)
        return logging.getLogger()

    def handle(self, socket, addr):
        while True:
            chunk = socket.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack('>L', chunk)[0]
            if slen == 0:
                self.stop()
                break
            chunk = socket.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + socket.recv(slen - len(chunk))
            obj = pickle.loads(chunk)
            record = logging.makeLogRecord(obj)
            self.logger.handle(record)


def start_server(file_name):
    server = LogServer(('127.0.0.1', DEFAULT_TCP_LOGGING_PORT), file_name=file_name)
    server.serve_forever()


def stop_server():
    end = bytes.fromhex('0000 0000')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(('localhost', DEFAULT_TCP_LOGGING_PORT))
        s.send(end)
        s.close()
    except ConnectionRefusedError:
        # looks like the server is already stopped.
        pass


def configure_client_logger(server_ip, logger_name):
    socket_logger = logging.getLogger(logger_name)
    socket_logger.setLevel(10)
    socket_handler = SocketHandler(server_ip, DEFAULT_TCP_LOGGING_PORT)
    socket_logger.addHandler(socket_handler)
    return socket_logger


if __name__ == '__main__':
    from multiprocessing import Process
    p = Process(target=start_server, args=('/Users/railesax/dev/pytest-single_file_logging/tests/log.config',))
    p.start()
    p.join()
