import json
from serverdensity.wrapper.jsonobject import JsonObject
from serverdensity.wrapper.crud import CRUD


class Device(JsonObject, CRUD):

    _schemapath = '/schema/devices.json'

    PATHS = {
        'create': '/inventory/devices',
        'delete': '/inventory/devices/{}',
        'list': '/inventory/devices',
        'search': '/inventory/resources',
        'update': '/inventory/devices/{}',
        'view_by_agent': '/inventory/devices/{}/byagentkey',
        'view': '/inventory/devices/{}'
    }

    def search(self, filtering, **kwargs):
        kwargs.setdefault('params', {})['filter'] = json.dumps(filtering)
        result = self.api.get(url=self.PATHS['search'], **kwargs)
        return [self.__class__(item) for item in result]

    def view_by_agent(self, agentkey, **kwargs):
        return self.__class__(self.api.get(url=self.PATHS['view_by_agent'].format(agentkey), **kwargs))
