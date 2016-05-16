# coding: utf-8

import contextlib
import logging
import threading
from collections import deque

from kazoo.client import KazooClient
from thriftpy.protocol import TBinaryProtocolFactory
from thriftpy.transport import (
    TBufferedTransportFactory,
    TSocket,
)

from ctec_tclient import CtecTClient
from error import CTECThriftClientError

logging.basicConfig()


class ClientPool:
    def __init__(self, service, server_hosts=None, zk_path=None, zk_hosts=None, max_renew_times=3):
        """
        对每个RPC服务提供实例进行连接池管理。
        :param server_hosts: 服务提供者地址，数组类型，['ip:port','ip:port']
        :param zk_path: 服务提供者在zookeeper中的路径
        :param zk_hosts: zookeeper的host地址，多个请用逗号隔开
        :param service: Thrift的Service名称
        :param max_renew_times: 最大重连次数
        :return:
        """
        # 负载均衡队列
        self.load_balance_queue = deque()
        # 保存IP与CLIENT对象关系
        # {ip:client}
        self.ip_dict = dict()
        self.service = service
        self.lock = threading.RLock()
        self.max_renew_times = max_renew_times

        if zk_hosts:
            self.kazoo_client = KazooClient(hosts=zk_hosts)
            self.kazoo_client.start()
            self.zk_path = zk_path
            self.zk_hosts = zk_hosts
            # 定义Watcher
            self.kazoo_client.ChildrenWatch(path=self.zk_path,
                                            func=self.watcher)
            # 刷新连接池中的连接对象
            self.__refresh_thrift_connections(self.kazoo_client.get_children(self.zk_path))
        elif server_hosts:
            self.server_hosts = server_hosts
            # 复制新的IP地址到负载均衡队列中
            self.load_balance_queue.extendleft(self.server_hosts)
        else:
            raise CTECThriftClientError('没有指定服务器获取方式！')

    def get_client(self, socket_timeout=3000):
        """
        轮询在每个ip:port的连接池中获取连接（线程安全）
        从当前队列右侧取出ip:port信息，从ip_dict变量中获取client
        将连接池对象放回到当前队列的左侧
        :param socket_timeout: 请求或连接超时时间，默认3秒
        :return:
        """
        client = None
        with self.lock:
            try:
                ip = self.load_balance_queue.pop()
            except IndexError:
                raise CTECThriftClientError('没有可用的服务提供者列表！')
            if ip:
                self.load_balance_queue.appendleft(ip)
                client = self.ip_dict.get(ip)
                if client is None:
                    # 创建新的thrift client
                    socket = TSocket(ip.split(':')[0], int(ip.split(':')[1]), socket_timeout=socket_timeout)
                    proto_factory = TBinaryProtocolFactory()
                    trans_factory = TBufferedTransportFactory()
                    transport = trans_factory.get_transport(socket)
                    protocol = proto_factory.get_protocol(transport)
                    transport.open()
                    client = CtecTClient(self, ip, self.service, protocol, socket_timeout,
                                         max_renew_times=self.max_renew_times)

                    # 加入到ip与client对应的字典中
                    self.ip_dict[ip] = client
        return client

    def close(self):
        """
        关闭所有连接池和zk客户端
        :return:
        """
        if getattr(self, 'kazoo_client', None):
            self.kazoo_client.stop()

    def watcher(self, children):
        """
        zk的watcher方法，负责检测zk的变化，刷新当前双端队列中的连接池
        :param children: 子节点，即服务提供方的列表
        :return:
        """
        self.__refresh_thrift_connections(children)

    def __refresh_thrift_connections(self, children):
        """
        刷新服务提供者在当前队列中的连接池信息（线程安全），主要用于zk刷新
        :param children:
        :return:
        """
        with self.lock:
            # 清空负载均衡队列
            self.load_balance_queue.clear()
            # 清空ip_dict
            self.ip_dict.clear()
            # 复制新的IP地址到负载均衡队列中
            self.load_balance_queue.extendleft(children)

    def renew_broken_client(self, client, socket_timeout):
        """
        刷新已经断开的连接
        :param socket_timeout:
        :param client:
        :return:
        """
        with self.lock:
            if not client.is_recover:
                # 创建新的thrift protocol
                socket = TSocket(client.ip.split(':')[0], int(client.ip.split(':')[1]), socket_timeout=socket_timeout)
                proto_factory = TBinaryProtocolFactory()
                trans_factory = TBufferedTransportFactory()
                transport = trans_factory.get_transport(socket)
                protocol = proto_factory.get_protocol(transport)
                transport.open()
                client._iprot = client._oprot = protocol
                client.is_recover = True
            client.wait_thread_nums -= 1
            if client.is_recover and client.wait_thread_nums == 0:
                client.is_recover = False


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
