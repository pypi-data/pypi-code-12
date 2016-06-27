import trafaret as t
from ..client import get_client
from ..utils import encode_utf8_if_py2


class Feature(object):
    converter = t.Dict({
        'id': t.Int,
        'name': t.String,
        t.Key('featureType') >> 'feature_type': t.String,
        'importance': t.Or(t.Float, t.Null),
        t.Key('lowInformation') >> 'low_information': t.Bool,
        t.Key('uniqueCount') >> 'unique_count': t.Int,
        t.Key('naCount') >> 'na_count': t.Int,
    })

    def __init__(self, data):
        self.__dict__.update(self.converter.check(data))

    def __repr__(self):
        return encode_utf8_if_py2('{}({})'.format(type(self).__name__, self.name))

    @classmethod
    def get(cls, project_id, feature_id):
        """Retrieve a single feature

        Parameters
        ----------
        project_id : str
            The ID of the project the feature is associated with.
        feature_id : str
            The ID of the feature to retrieve

        Returns
        -------
        feature : Feature
            The queried instance
        """
        path = 'projects/{}/features/{}/'.format(project_id, feature_id)
        return Feature(get_client().get(path).json())
