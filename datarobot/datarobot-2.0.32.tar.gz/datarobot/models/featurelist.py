import six
import trafaret as t
from datarobot.client import get_client
from datarobot.utils import SetupFieldsMetaclass, from_api


class Featurelist(six.with_metaclass(SetupFieldsMetaclass, object)):
    _client = None
    _fields = frozenset(['id',
                         'name',
                         'features'])
    _path = 'projects/{}/featurelists/'

    def __repr__(self):
        return 'Featurelist({})'.format(self.name)

    def __init__(self, data):
        self.id = None
        self.name = None
        self.features = None
        self.project = None
        self._data = data

        if isinstance(data, dict):
            self._set_up(data)
        else:
            raise ValueError

    def _set_up(self, data):
        from datarobot.models import Project

        data = from_api(data)

        self.project = Project(data.get('project_id'))

        converter = t.Dict({
            t.Key('id', optional=True) >> 'id': t.String(allow_blank=True),
            t.Key('name', optional=True) >> 'name': t.String,
            t.Key('features', optional=True) >> 'features': t.List(t.String),
        }).allow_extra("*")

        for k, v in six.iteritems(converter.check(data)):
            if k in self._fields:
                setattr(self, k, v)

        self._path = self._path.format(data.get('project_id'))

    @classmethod
    def get(cls, project, featurelist_id):
        """Retrieve a known feature list

        Parameters
        ----------
        project : Project instance or str
            The project the featurelist is associated with, specified either
            with an instance of Project or the project id
        featurelist_id : str
            The ID of the featurelist to retrieve

        Returns
        -------
        featurelist : Featurelist
            The queried instance
        """
        from datarobot import Project

        if isinstance(project, Project):
            project_id = project.id
        elif isinstance(project, six.string_types):
            project_id = project
        else:
            raise ValueError('Project arg must be Project instance or str')

        url = cls._path.format(project_id) + featurelist_id + '/'
        client = cls._client or get_client()
        resp_data = client.get(url).json()
        return cls(resp_data)
