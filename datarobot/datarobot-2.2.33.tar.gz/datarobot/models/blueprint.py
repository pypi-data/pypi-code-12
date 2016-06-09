import six
from ..utils import SetupFieldsMetaclass, from_api


class Blueprint(six.with_metaclass(SetupFieldsMetaclass, object)):
    _fields = frozenset(['id', 'processes', 'model_type',
                         'project_id'])

    def __init__(self, data):
        self.id = None
        self.processes = None
        self.model_type = None
        self.project_id = None

        self._data = data
        if isinstance(data, dict):
            self._set_up(from_api(data))
        else:
            raise ValueError

    def __repr__(self):
        return 'Blueprint({})'.format(self.model_type)  # pragma:no cover

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id

    def _set_up(self, data):
        for k, v in six.iteritems(data):
            if k in self._fields:
                setattr(self, k, v)
