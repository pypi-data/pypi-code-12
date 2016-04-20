__author__ = 'sunquan'

from huivo.thrift.client.Client import Client
from huivo.thrift.client.Configurator import  Configurator

class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance


class ClientFactory(Singleton):
    _client_map = {}

    def get_client(self, iface_cls):
        if self._client_map.has_key(iface_cls):
            return self._client_map[iface_cls]

        configurator = Configurator()
        service_setting = configurator.get_setting(iface_cls)
        client = Client(configurator.zookeeper_address, configurator.zookeeper_root_path,
                        service_setting.java_cls, service_setting.iface_cls, service_setting.client_cls)
        self._client_map[iface_cls] = client
        return client

