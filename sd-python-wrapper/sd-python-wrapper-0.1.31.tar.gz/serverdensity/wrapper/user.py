from serverdensity.wrapper.crud import CRUD
from serverdensity.wrapper.jsonobject import JsonObject


class User(JsonObject, CRUD):

    _schemapath = '/schema/users.json'

    PATHS = {
        'create': '/users/users',
        'delete': '/users/users/{}',
        'list': '/users/users',
        'update': '/users/users/{}',
        'view': '/users/users/{}'
    }
