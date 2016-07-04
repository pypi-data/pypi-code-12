# coding: utf-8

import functools
import logging
import socket

from thriftpy.thrift import TClient
from thriftpy.transport import TTransportException


class CtecTClient(TClient):
    def __init__(self, client_pool, ip, service, iprot, socket_timeout, oprot=None, max_renew_times=3, use_pool=True):
        """
        初始化client
        :param client_pool: 关联的client pool
        :param ip: IP地址信息
        :param service:
        :param iprot:
        :param socket_timeout: 超时时间
        :param oprot:
        :param max_renew_times: 最大重试次数
        :param use_pool: 是否使用连接池
        :return:
        """
        TClient.__init__(self, service, iprot, oprot)
        self.use_pool = use_pool
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
            for i in xrange(self.max_renew_times):
                # 连接断开最大重连次数
                logging.debug('第%s次循环开始 -->' % i)
                max_retry_times = 0
                while max_retry_times < 3:
                    try:
                        logging.debug('第%s次调用thrift接口 start-->' % max_retry_times)
                        res = func(*args, **kwargs)
                        logging.debug('第%s次调用thrift接口 end<--' % max_retry_times)
                        break
                    except TTransportException, e:
                        logging.exception('捕获传输层错误，TTransportException.type=%s' % e.type)
                        if e.type == TTransportException.END_OF_FILE:
                            self.wait_thread_nums += 1
                            self.client_pool.renew_broken_client(self, self.socket_timeout)
                        else:
                            break
                    except socket.error:
                        logging.exception('捕获socket错误')
                        break
                    finally:
                        max_retry_times += 1
                logging.debug('第%s次循环结束 -->' % i)

                if res:
                    break
            logging.debug('thrift接口调用结果：%s' % res)
            return res

    def close(self):
        if not self.use_pool:
            super(CtecTClient, self).close()