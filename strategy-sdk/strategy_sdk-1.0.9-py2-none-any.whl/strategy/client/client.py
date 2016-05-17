# encoding: utf-8
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import unittest

from communication.client import connection
from communication.server import protocol
from communication.server.protocol.protocol import ProtocolMessage
from exception.exception import ConnectionBrokenException, RequestTimeoutException
from strategy.client.interface import AbstractStrategyClient, AbstractAsyncMessageHandler
from strategy.request import RequestInfo, ResponseInfo
from sd import utils


__author__ = 'Yonka'


class StrategyClient(AbstractStrategyClient):
    MAX_TRIES = 3
    RECONNECT_INTERNAL = 5

    def __init__(
            self,
            host: str=None,
            port: int=0,
            read_timeout: int=0,
            conn_timeout: int=0,
            async_message_handler: AbstractAsyncMessageHandler=None
    ):
        self.host = host
        self.port = port
        self.readTimeout = read_timeout
        self.connTimeout = conn_timeout
        self.asyncMessageHandler = async_message_handler
        self.open = False
        self.closing = False

        self._lock = threading.Lock()

        self.baseConn = None
        self.ioReaderWorkers = None
        self.bussWorkers = None
        self.heartbeatMonitor = None
        self.timeoutMonitor = None

        self.requestCache = {}
        self.responseCache = {}

    def _build_base_conn(self) -> bool:
        for i in range(self.MAX_TRIES):
            try:
                self.baseConn = connection.new_conn(self.host, self.port, self.readTimeout, self.connTimeout)
                return True
            except Exception as e:
                logging.exception("unable to build connection to server, e is %s", e)
                try:
                    time.sleep(self.RECONNECT_INTERNAL)
                except InterruptedError as e1:
                    logging.exception("unable to build connection to server, due to thread interrupt, e is %s", e1)
        return False

    def _write(self, protocol_message: ProtocolMessage):
        if self.open:
            logging.info("Send message:%s", protocol_message)
            result = self.baseConn.write(protocol_message)
            if not result:
                self.open = False
                raise ConnectionBrokenException("connection broken")

    def _do_heartbeat(self):
        try:
            # self._write(protocol.new_strategy_hb_msg())
            self._write(protocol.new_strategy_hb_msg())
        except Exception as e:
            logging.exception("%s", e)

    def _check_timeout(self):
        request_cache = dict(self.requestCache)  # 作为client可以
        for req_id, req in request_cache.items():
            if req is None or req_id in self.responseCache:
                continue  # req should not be None
            if req.is_timeout():
                resp = ResponseInfo()
                resp.timedOut = True
                self.responseCache[req_id] = resp
                req.notify_all()

    def _read_conn(self):
        while True:
            try:
                if not self.open:
                    # 这里如果conn被关闭也不重连的话，会一直while循环吃大量CPU
                    time.sleep(1)
                    continue
                protocol_msg = self.baseConn.read()  # type: ProtocolMessage
                if protocol_msg is None:
                    self.open = False
                    continue
                logging.info("Received message:%s", protocol_msg)

                if protocol_msg.is_hb_message():
                    self._write(protocol.new_strategy_hb_ack_msg())
                    # self._write(protocol.new_strategy_hb_msg())
                else:
                    req = self.requestCache.pop(protocol_msg.reqId, None)  # type: RequestInfo
                    if req is None:
                        self.bussWorkers.submit(
                            lambda async_message: self.asyncMessageHandler.handle_async_message(async_message),
                            protocol_msg
                        )
                    else:
                        self.responseCache[protocol_msg.reqId] = ResponseInfo(protocol_msg)
                        req.notify_all()
            except Exception as e:
                logging.exception("_read_conn met exception: %s", e)

    def sync_rpc(self, request_info: RequestInfo) -> ResponseInfo:
        """
        may raise RequestTimeoutException or ConnectionBrokenException
        """
        if not self.is_open():
            raise ConnectionBrokenException("socket broken")
        self.requestCache[request_info.reqId] = request_info
        self._write(request_info.protocolMessage)
        request_info.wait()
        resp = self.responseCache.pop(request_info.reqId, None)  # type: ResponseInfo
        if resp is None:
            raise ConnectionBrokenException("socket broken")  # should not
        if request_info.is_timeout() or resp.timedOut:
            raise RequestTimeoutException("request %d timed out, reqTime: %d, curTime: %d, timeout: %d, req is %s" % (
                request_info.reqId, request_info.createTime, utils.timestamp(), request_info.timeout, request_info))
        return resp

    def close(self) -> bool:
        with self._lock:
            self.closing = True
            self.open = False

            for req in self.requestCache.values():
                req.notify_all()

            if self.baseConn is not None and self.baseConn.is_open():
                self.baseConn.close()
                self.baseConn = None

            if self.ioReaderWorkers is not None:
                self.ioReaderWorkers.shutdown()
            if self.timeoutMonitor is not None:
                self.timeoutMonitor.shutdown()
            if self.heartbeatMonitor is not None:
                self.heartbeatMonitor.shutdown()

            self.requestCache = {}
            self.responseCache = {}

        self.closing = False
        return True

    def connect(self) -> bool:
        self.ioReaderWorkers = ThreadPoolExecutor(1)
        self.bussWorkers = ThreadPoolExecutor(1)
        if not self._build_base_conn():
            logging.info("Socket connection timeout")
            self.open = False
            raise TimeoutError("Socket connection timeout")  # XXX use ConnectionBrokenException ?
        else:
            logging.info("Socket connection open")
            self.open = True

        self.heartbeatMonitor = ThreadPoolExecutor(1)
        self.heartbeatMonitor.submit(utils.schedule_task(self._do_heartbeat, 10, 20, 0))

        self.timeoutMonitor = ThreadPoolExecutor(1)
        self.timeoutMonitor.submit(utils.schedule_task(self._check_timeout, 1, 1, 0))

        self.ioReaderWorkers.submit(self._read_conn)

        return True

    def is_open(self) -> bool:
        return self.open and not self.closing

    def async_rpc(self, request_info: RequestInfo) -> bool:
        if not self.is_open():
            raise ConnectionBrokenException("socket broken")
        self._write(request_info.protocolMessage)
        return True


class TestClient(unittest.TestCase):
    def test_client(self):
        logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
        c = StrategyClient("101.200.228.73", 8080)
        # c = StrategyClient("101.200.228.73", 3333)
        # c = StrategyClient("localhost", 8080)
        c.connect()
        time.sleep(10000)
