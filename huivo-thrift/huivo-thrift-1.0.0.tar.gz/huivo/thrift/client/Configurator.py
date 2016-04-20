__author__ = 'sunquan'


class ServiceSetting(object):
    def __init__(self, iface_cls, client_cls, java_cls):
        self._iface_cls = iface_cls
        self._client_cls = client_cls
        self._java_cls = java_cls

    @property
    def iface_cls(self):
        return self._iface_cls

    @property
    def client_cls(self):
        return self._client_cls

    @property
    def java_cls(self):
        return self._java_cls



class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance


class Configurator(Singleton):
    _settings = {}
    _zookeeper_address = ""
    _zookeeper_root_path = ""

    @property
    def zookeeper_address(self):
        return self._zookeeper_address

    @zookeeper_address.setter
    def zookeeper_address(self, value):
        self._zookeeper_address = value

    @property
    def zookeeper_root_path(self):
        return self._zookeeper_root_path

    @zookeeper_root_path.setter
    def zookeeper_root_path(self, value):
        self._zookeeper_root_path = value

    def add_setting(self, service_setting):
        self._settings[service_setting.iface_cls] = service_setting
        print self._settings

    def get_setting(self, iface_cls):
        if self._settings.has_key(iface_cls):
            return self._settings[iface_cls]
        raise RuntimeError("")