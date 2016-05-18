# encoding: utf-8
from __future__ import absolute_import
import logging
import socket
import threading
import time
from ctypes import c_int64

from sd.communication.server import protocol
from sd.communication.client.connection import BaseConn

__author__ = u'Yonka'


class HeartBeatServer(object):
    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self.ss = None

    def start(self):
        ss = socket.socket()
        ss.bind((self.addr, self.port))
        ss.listen(5)
        self.ss = ss
        while True:
            s, c_addr = ss.accept()
            logging.info(u"accept conn from: %s", c_addr)
            self.handle_socket(s, c_addr, True)

    def handle_socket(self, s, addr, async=False):
        if async:
            threading.Thread(target=self.handle_socket, args=(s, addr, False)).start()
            return
        base_conn = BaseConn(s)
        last_hb_time = c_int64(int(time.time()))
        self.monitor_conn(base_conn, addr, last_hb_time)
        while True:
            msg = base_conn.read()
            if msg is None:
                logging.info(u"get None msg from base_conn %s, close it", addr)
                base_conn.close()
                break
            if msg.is_hb_message():
                logging.info(u"get hb msg from base_conn %s", addr)
                last_hb_time.value = int(time.time())
            elif msg.is_ack_message():
                logging.info(u"get ack msg from base_conn %s", addr)
                last_hb_time.value = int(time.time())
            else:
                logging.info(u"get non-hb-or-ack msg from base_conn %s: %s", addr, msg)

    def monitor_conn(
            self, conn, addr, last_hb_time,
            monitor_interval=10, hb_send_interval=5, hb_check_interval=1, async=True):
        if async:
            threading.Thread(
                target=self.monitor_conn,
                args=(conn, addr, last_hb_time, monitor_interval, hb_send_interval, hb_check_interval, False)).start()
            return
        while True:
            if time.time() - last_hb_time.value > monitor_interval:
                logging.info(u"send hb to base_conn %s", addr)
                if not conn.write(protocol.new_strategy_hb_msg()):
                    logging.info(u"write hb to base_conn %s failed, close it", addr)
                    conn.close()
                    break
                last_hb_time.value = int(time.time())
                time.sleep(hb_send_interval)
                continue
            time.sleep(hb_check_interval)


if __name__ == u"__main__":
    logging.basicConfig(format=u'%(asctime)s %(message)s', datefmt=u'%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
    HeartBeatServer(u"localhost", 8080).start()
