# coding: utf-8

import functools

from thriftpy.thrift import TClient
from thriftpy.transport import TTransportException


class CtecTClient(TClient):
    def __init__(self, client_pool, ip, service, iprot, socket_timeout, oprot=None, max_renew_times=3):
        """
        初始化client
        :param client_pool: 关联的client pool
        :param ip: IP地址信息
        :param service:
        :param iprot:
        :param socket_timeout: 超时时间
        :param oprot:
        :param max_renew_times: 最大重连次数
        :return:
        """
        TClient.__init__(self, service, iprot, oprot)
        self.socket_timeout = socket_timeout
        self.ip = ip
        self.client_pool = client_pool
        self.wait_thread_nums = 0
        # 连接是否恢复
        self.is_recover = False
        self.max_renew_times = max_renew_times

    def __getattr__(self, item):
        return functools.partial(self._real_call, TClient.__getattr__(self, item))

    def _real_call(self, func, *args, **kwargs):
        if func:
            res = None
            for _ in xrange(self.max_renew_times):
                try:
                    res = func(*args, **kwargs)
                except TTransportException:
                    self.wait_thread_nums += 1
                    self.client_pool.renew_broken_client(self, self.socket_timeout)
            return res
