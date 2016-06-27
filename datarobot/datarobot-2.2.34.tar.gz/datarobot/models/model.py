import webbrowser

import six
import trafaret as t

from ..client import get_client, staticproperty
from ..utils import SetupFieldsMetaclass, from_api, get_id_from_response


class Model(six.with_metaclass(SetupFieldsMetaclass, object)):
    _client = staticproperty(get_client)
    _path = 'projects/{}/models/'
    _fields = frozenset(['id', 'project', 'processes', 'blueprint_id',
                         'model_type', 'model_category', 'featurelist_id',
                         'sample_pct', 'metrics'])
    _converter = t.Dict({
        t.Key('id', optional=True): t.String,
        t.Key('processes', optional=True): t.List(t.Or(t.String, t.Null)),
        t.Key('featurelist_name', optional=True): t.String,
        t.Key('featurelist_id', optional=True): t.String,
        t.Key('project_id', optional=True): t.String,
        t.Key('sample_pct', optional=True): t.Float,
        t.Key('model_type', optional=True): t.String,
        t.Key('model_category', optional=True): t.String,
        t.Key('blueprint_id', optional=True): t.String,
        t.Key('metrics', optional=True): t.Dict().allow_extra("*"),
    })

    def __init__(self, data, project=None):
        self._data = data
        self.project = project
        self.blueprint = None
        self.featurelist = None
        if isinstance(data, dict):
            self._set_up(data)
        elif isinstance(data, tuple):
            self.id = data[1]
            from . import Project
            self.project = Project(data[0])
        else:
            raise ValueError
        self.project_id = self.project.id
        self._fix_path()

    def __repr__(self):
        return 'Model({})'.format(self.model_type or self.id)  # pragma:no cover

    def _fix_path(self):
        self._path = self._path.format(self.project.id)

    def _set_up(self, data):
        from . import Project, Blueprint, Featurelist
        data = self._converter.check(from_api(data, do_recursive=False))
        # Construction Project
        if not self.project:
            self.project = Project(data.get('project_id'))

        # Construction Blueprint
        bp_data = {'id': data.get('blueprint_id'),
                   'processes': data.get('processes'),
                   'model_type': data.get('model_type'),
                   'project_id': data.get('project_id')}
        self.blueprint = Blueprint(bp_data)

        # Construction FeatureList
        ft_list_data = {'id': data.get('featurelist_id'),
                        'name': data.get('featurelist_name')}
        self.featurelist = Featurelist(ft_list_data)

        for k, v in six.iteritems(data):
            if k in self._fields:
                setattr(self, k, v)

    @classmethod
    def get(cls, project, model_id):
        """
        Retrieve a specific model.

        Parameters
        ----------
        project : Project instance or str.
            You can provide a project instance or project id to identify
            which project the model is associated with.
        model_id : str
            The ``model_id`` of the leaderboard item to retrieve.

        Returns
        -------
        model : Model
            The queried instance.

        Raises
        ------
        ValueError
            passed ``project`` parameter value is of not supported type
        """
        from . import Project
        project_instance = False
        if isinstance(project, Project):
            project_id = project.id
            project_instance = True
        elif isinstance(project, six.string_types):
            project_id = project
        else:
            raise ValueError('Project arg can be Project instance or str')
        url = cls._path.format(project_id) + model_id + '/'
        resp_data = cls.fetch_resource_data(url)
        return cls(resp_data, project=project if project_instance else None)

    @classmethod
    def fetch_resource_data(cls, url, join_endpoint=True):
        """
        Used to acquire model data directly from its url.

        Consider using `get` instead, as this is a convenience function
        used for development of datarobot

        Parameters
        ----------
        url : string
            The resource we are acquiring
        join_endpoint : boolean, optional
            Whether the client's endpoint should be joined to the URL before
            sending the request. Location headers are returned as absolute
            locations, so will _not_ need the endpoint

        Returns
        -------
        model_data : dict
            The queried model's data
        """
        return cls._client.get(url, join_endpoint=join_endpoint).json()

    def get_features_used(self):
        """Query the server to determine which features were used.

        Note that the data returned by this method is possibly different
        than the names of the features in the featurelist used by this model.
        This method will return the raw features that must be supplied in order
        for predictions to be generated on a new set of data. The featurelist,
        in contrast, would also include the names of derived features.

        Returns
        -------
        features : list of str
            The names of the features used in the model.
        """
        url = '{}{}/features/'.format(self._path, self.id)
        resp_data = self._client.get(url).json()
        return resp_data['featureNames']

    def delete(self):
        """
        Delete a model from the project's leaderboard.
        """
        url = '{}{}/'.format(self._path, self.id)
        self._client.delete(url)

    def get_leaderboard_ui_permalink(self):
        """
        Returns
        -------
        url : str
            Permanent static hyperlink to this model at leaderboard.
        """
        return '{}/{}{}'.format(self._client.domain, self._path, self.id)

    def open_model_browser(self):
        """
        Opens model at project leaderboard in web browser.

        Note:
        If text-mode browsers are used, the calling process will block
        until the user exits the browser.
        """

        url = self.get_leaderboard_ui_permalink()
        return webbrowser.open(url)

    def train(self, sample_pct=None, featurelist_id=None, scoring_type=None):
        """
        Train this model on `sample_pct` percents.
        This method creates a new training job for worker and appends it to
        the end of the queue for this project.
        After the job has finished you can get this model by retrieving
        it from the project leaderboard.

        Parameters
        ----------
        sample_pct : float, optional
            The amount of data to use for training. Defaults to the maximum
            amount available based on the project configuration.
        featurelist_id : str, optional
            The identifier of the featurelist to use. If not defined, the
            featurelist of this model is used.
        scoring_type : str, optional
            Either ``SCORING_TYPE.validation`` or
            ``SCORING_TYPE.cross_validation``. ``SCORING_TYPE.validation``
            is available for every partitioning type, and indicates that
            the default model validation should be used for the project.
            If the project uses a form of cross-validation partitioning,
            ``SCORING_TYPE.cross_validation`` can also be used to indicate
            that all of the available training/validation combinations
            should be used to evaluate the model.

        Returns
        -------
        model_job_id : str
            id of created job, can be used as parameter to ``ModelJob.get``
            method or ``wait_for_async_model_creation`` function

        Examples
        --------
        .. code-block:: python

            model = Model.get('p-id', 'l-id')
            model_job_id = model.train()
        """
        url = self._path
        payload = {
            'blueprint_id': self.blueprint_id,
        }
        if sample_pct is not None:
            payload['sample_pct'] = sample_pct
        if scoring_type is not None:
            payload['scoring_type'] = scoring_type
        if featurelist_id is not None:
            payload['featurelist_id'] = featurelist_id
        else:
            payload['featurelist_id'] = self.featurelist_id
        response = self._client.post(url, data=payload)
        return get_id_from_response(response)
