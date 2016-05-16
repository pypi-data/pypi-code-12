# coding: utf-8
import contextlib
import logging

from ctec_thrift_client.client_pool import ClientPool

logging.warn('[deprecated]请使用client_pool.ClientPool代替！')
ClientPool = ClientPool


@contextlib.contextmanager
def get_client(pool, socket_timeout=3000):
    """
    提供with方法调用
    with get_client(pool) as c:
        c.ping()
    :param socket_timeout: 请求或连接超时时间，默认3秒
    :param pool: 负载连接池对象
    :return:
    """
    yield pool.get_client(socket_timeout)
