# encoding: utf-8
from socket import socket

__author__ = 'Yonka'

from communication.client.connection.connection import BaseConn


def new_conn(host: str, port: int, read_timeout: int, conn_timeout: int) -> BaseConn:
    s = socket()
    # as python only provides one timeout option which will be used both in connect and read
    if conn_timeout > 0:
        s.settimeout(conn_timeout)  # 以主机名访问时connect需要花费一些时间，与non-blocking冲突（0 timeout）
    s.connect((host, port))
    if read_timeout > 0:
        s.settimeout(read_timeout)  # 0表示非阻塞，模型差异较大
    return BaseConn(s)
