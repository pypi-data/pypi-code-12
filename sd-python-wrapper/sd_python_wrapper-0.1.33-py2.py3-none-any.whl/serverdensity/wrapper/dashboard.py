from serverdensity.wrapper.crud import CRUD
from serverdensity.wrapper.jsonobject import JsonObject


class Dashboard(JsonObject, CRUD):

    _schemapath = '/schema/dashboards.json'

    PATHS = {
        'create': '/users/dashboards',
        'delete': '/users/dashboards/{}',
        'list': '/users/dashboards',
        'update': '/users/dashboards/{}',
        'view': '/users/dashboards/{}'
    }
