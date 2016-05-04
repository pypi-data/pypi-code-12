from serverdensity.wrapper.crud import CRUD
from serverdensity.wrapper.jsonobject import JsonObject


class Tag(JsonObject, CRUD):

    _schemapath = '/schema/tags.json'

    PATHS = {
        'create': '/inventory/tags',
        'delete': '/inventory/tags/{}',
        'list': '/inventory/tags',
        'update': '/inventory/tags/{}',
        'view': '/inventory/tags/{}'
    }
