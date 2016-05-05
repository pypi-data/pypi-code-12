import os

class Config:
    def __init__(self, path=None):
        self._host = 'api.postageapp.com'
        self._proto = 'http'
        self._port = None
        self._api_key = None
        self._environment = None
        self._framework = 'Python'

        if ('POSTAGEAPP_API_KEY' in os.environ):
            self._api_key = os.environ['POSTAGEAPP_API_KEY']

        if (path == None and 'POSTAGEAPP_INI_PATH' in os.environ):
            path = os.environ['POSTAGEAPP_INI_PATH']

        if (path):
            self.read_from_file(path)

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        self._host = value
        return self._host

    @property
    def proto(self):
        return self._proto

    @proto.setter
    def proto(self, value):
        self._proto = value
        return self._proto

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = value
        return self._port

    @property
    def api_key(self):
        return self._api_key

    @api_key.setter
    def api_key(self, value):
        self._api_key = value
        return self._api_key

    @property
    def environment(self):
        return self._environment

    @environment.setter
    def environment(self, value):
        self._environment = value
        return self._environment

    @property
    def framework(self):
        return self._framework

    @framework.setter
    def framework(self, value):
        self._framework = value
        return self._framework

    def read_from_file(path):
        # ...
        return
