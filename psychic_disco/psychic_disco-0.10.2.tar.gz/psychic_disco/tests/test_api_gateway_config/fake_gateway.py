import os
import json


class FakeApiGatewayConsole(object):
    def __init__(self):
        self.apis = dict()
        self.basepath = os.path.dirname(os.path.abspath(__file__))

    def _open_json(self, filename):
        path = os.path.join(self.basepath, filename)
        with open(path) as f:
            return json.loads(f.read())

    def get_rest_apis(self):
        return self._open_json("get_rest_apis.json")

    def get_resources(self, **kwargs):
        return self._open_json("get-resources.json")

    def get_resource(self, **kwargs):
        return self._open_json("get-resource.json")

    def get_method(self, **kwargs):
        return self._open_json("get-method.json")
