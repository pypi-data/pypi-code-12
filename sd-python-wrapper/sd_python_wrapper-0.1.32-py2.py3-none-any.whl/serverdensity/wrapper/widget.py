from serverdensity.wrapper.jsonobject import JsonObject
from serverdensity.wrapper.crud import CRUD


class Widget(JsonObject, CRUD):

    _schemapath = '/schema/widgets.json'

    PATHS = {
        'create': '/users/widgets',
        'delete': '/users/widgets/{}',
        'list': '/users/widgets',
        'update': '/users/widgets/{}',
        'view': '/users/widgets/{}',
        'duplicate': '/users/widgets/duplicate/{}'
    }

    def duplicate(self, _id=None, **kwargs):
        if not _id:
            _id = self._id
        return self.__class__(self.api.post(url=self.PATHS['duplicate'].format(_id)))
