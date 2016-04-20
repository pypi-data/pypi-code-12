__author__ = 'sunquan'

import inspect
import random, json
from huivo.thrift.client.ZkRegistry import watch_method
from huivo.thrift.client.ZkRegistry import ZkRegistry
from huivo.thrift.client.ReadWriteLock import ReadWriteLock
from huivo.thrift.client.ConnectionPool import ConnectionPool
from thrift.Thrift import TApplicationException
from huivo.thrift.common.ttypes import ThriftException




class Client(object):
    def __init__(self, zk_address, zk_path, java_class, iface_class, client_class):
        self._read_write_lock = ReadWriteLock()
        self._iface_class = iface_class
        self._client_class = client_class
        self._provider_path = zk_path + java_class + "/providers"
        self._zk_path = zk_path
        self._zk_registry = ZkRegistry(zk_address, self.zk_connection_watcher)

        self._providers = []
        self._connection_pool_map = {}

        for m in inspect.getmembers(self._iface_class, predicate=inspect.ismethod):
            setattr(self, m[0], self.__create_thrift_proxy__(m[0]))

        self.lookup_providers()

    def zk_connection_watcher(self, h, type, state, path):

        self.lookup_providers()

    def lookup_providers(self):
        print "lookup providers"
        @watch_method
        def watcher():
            self.lookup_providers()
        _list = self._zk_registry.get_children(self._provider_path, watcher)
        print "lookup providers"
        self.reset_providers(_list)

    def get_connection_pool(self):
        self._read_write_lock.acquire_read()
        try:
            if len(self._providers) <= 0:
                raise
            print len(self._providers)
            index = random.randint(0, len(self._providers) - 1)
            provider = self._providers[index]
            if(self._connection_pool_map.has_key(provider)):
                return self._connection_pool_map.get(provider)
            provider_data = json.loads(provider)
            connection_pool = ConnectionPool(provider_data["host"], provider_data["port"], self._client_class)
            self._connection_pool_map[provider] = connection_pool
            return connection_pool
        finally:
            self._read_write_lock.release_read();


    def reset_providers(self, new_providers):
        self._read_write_lock.acquire_write()
        try:
            for provider in self._connection_pool_map.keys():
                active = False
                for new_provider in new_providers:
                    if provider == new_provider:
                        active = True
                        break
                if not active:
                    self._connection_pool_map.get(provider).close()
                    self._connection_pool_map.pop(provider)
            self._providers = new_providers
        finally:
            self._read_write_lock.release_write();


    def __create_thrift_proxy__(self, methodName):
        def __thrift_proxy(*args):
            return self.__thrift_call__(methodName, *args)
        return __thrift_proxy

    def __thrift_call__(self, method, *args):
        connection_pool = self.get_connection_pool()
        conn = connection_pool.get_connection()
        try:
            result = getattr(conn, method)(*args)
            return result
        except TApplicationException as e:
            if e.type.type == TApplicationException.MISSING_RESULT:
                return None
            raise e
        except ThriftException as e:
            if e.code == 1:
                return None
            raise e
        except Exception as e:
            raise e
        finally:
            connection_pool.return_connection(conn)