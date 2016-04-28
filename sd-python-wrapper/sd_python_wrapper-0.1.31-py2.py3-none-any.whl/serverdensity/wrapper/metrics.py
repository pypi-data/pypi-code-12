import json

from serverdensity.wrapper.jsonobject import JsonObject
from serverdensity import Response


class Metrics(JsonObject):

    PATHS = {
        'available': '/metrics/definitions/{}',
        'get': '/metrics/graphs/{}'
    }

    def _validation(self, value):
        """Not needed"""
        pass

    def available(self, _id, start, end, **kwargs):
        kwargs.setdefault('params', {})['start'] = start.isoformat()
        kwargs['params']['end'] = end.isoformat()
        result = self.api.get(url=self.PATHS['available'].format(_id), **kwargs)
        return [Response(item) for item in result]

    def get(self, _id, start, end, filtering, **kwargs):
        kwargs.setdefault('params', {})['start'] = start.isoformat()
        kwargs['params']['end'] = end.isoformat()
        kwargs['params']['filter'] = json.dumps(filtering)
        result = self.api.get(url=self.PATHS['get'].format(_id), **kwargs)
        return [Response(item) for item in result]
