import collections
import webbrowser

import six
import trafaret as t


from .. import errors
from ..client import get_client, staticproperty
from ..enums import (ASYNC_PROCESS_STATUS, LEADERBOARD_SORT_KEY,
                     AUTOPILOT_MODE, VERBOSITY_LEVEL, QUEUE_STATUS,)
from .job import Job
from .modeljob import ModelJob
from .predict_job import PredictJob
from ..helpers import RecommenderSettings, AdvancedOptions
from ..helpers.partitioning_methods import BasePartitioningMethod
from ..utils import (SetupFieldsMetaclass, from_api,
                     parse_time, get_id_from_response,
                     get_duplicate_features, camelize,
                     deprecated,
                     is_urlsource, recognize_sourcedata, retry, logger, encode_utf8_if_py2)
from .feature import Feature

logger = logger.get_logger(__name__)


def _get_target_name(target_obj):
    if isinstance(target_obj, dict):
        return target_obj.get('target_name')
    elif isinstance(target_obj, six.string_types):
        return target_obj


class Project(six.with_metaclass(SetupFieldsMetaclass, object)):
    _client = staticproperty(get_client)
    _path = 'projects/'
    _fields = frozenset(['id', 'project_name', 'mode', 'target',
                         'target_type', 'holdout_unlocked', 'partition',
                         'metric', 'stage', 'created', 'advanced_options',
                         'recommender', 'positive_class', 'max_train_pct'])

    _converter = t.Dict({
        t.Key('_id', optional=True) >> 'id': t.String(allow_blank=True),
        t.Key('id', optional=True) >> 'id': t.String(allow_blank=True),
        t.Key('project_name', optional=True) >> 'project_name': t.String(
            allow_blank=True),
        t.Key('autopilot_mode', optional=True) >> 'mode': t.Int,
        t.Key('target', optional=True) >> 'target': _get_target_name,
        t.Key('target_type', optional=True): t.String(allow_blank=True),
        t.Key('holdout_unlocked', optional=True): t.Bool(),
        t.Key('metric', optional=True) >> 'metric': t.String(allow_blank=True),
        t.Key('stage', optional=True) >> 'stage': t.String(allow_blank=True),
        t.Key('partition', optional=True): t.Dict().allow_extra('*'),
        t.Key('positive_class', optional=True): t.Or(t.Int(), t.String()),
        t.Key('created', optional=True): parse_time,
        t.Key('advanced_options', optional=True): t.Dict().allow_extra('*'),
        t.Key('recommender', optional=True): t.Dict().allow_extra('*'),
        t.Key('max_train_pct', optional=True): t.Float()
    }).allow_extra('*')

    def __init__(self, data):
        self._data = data
        if isinstance(data, dict):
            self._set_up(data)
        elif isinstance(data, six.string_types):
            self.id = data

    def _set_up(self, data):
        data = self._converter.check(from_api(data))
        for k, v in six.iteritems(data):
            if k in self._fields:
                setattr(self, k, v)

    @staticmethod
    def _load_partitioning_method(method, payload):
        if not isinstance(method, BasePartitioningMethod):
            raise TypeError('method should inherit from BasePartitioningMethod')
        payload.update(method.collect_payload())

    @staticmethod
    def _load_recommender_settings(settings, payload):
        if not isinstance(settings, RecommenderSettings):
            raise TypeError('settings should be a RecommenderSettings')
        payload.update(settings.collect_payload())

    @staticmethod
    def _load_advanced_options(opts, payload):
        if not isinstance(opts, AdvancedOptions):
            raise TypeError('opts should inherit from AdvancedOptions')
        payload.update(opts.collect_payload())

    def __repr__(self):
        return encode_utf8_if_py2(u'{}({})'.format(self.__class__.__name__,
                                                   self.project_name or self.id))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id

    @classmethod
    def _get_data(cls, project_id):
        """
        Fetch information about a project.

        Used internally when fetching project information to either fetch
        a Project object directly, or update a project with new information
        from the server

        Parameters
        ----------
        project_id : str
            The identifier of the project you want to load.

        Returns
        -------
        project_data : dict
            The queried project's information
        """
        url = '{}{}/'.format(cls._path, project_id)
        return cls._client.get(url).json()

    @classmethod
    def get(cls, project_id):
        """
        Gets information about a project.

        Parameters
        ----------
        project_id : str
            The identifier of the project you want to load.

        Returns
        -------
        project : Project
            The queried project

        Examples
        --------
        .. code-block:: python

            import datarobot as dr
            p = dr.Project.get(project_id='54e639a18bd88f08078ca831')
            p.id
            >>>'54e639a18bd88f08078ca831'
            p.project_name
            >>>'Some project name'
        """
        data = cls._get_data(project_id)
        return cls(data)

    @classmethod
    def create(cls, sourcedata, project_name="Untitled Project", max_wait=600):
        """
        Creates a project with provided data.

        Project creation is asynchronous process, which means that after
        initial request we will keep polling status of async process
        that is responsible for project creation until it's finished.
        For SDK users this only means that this method might raise
        exceptions related to it's async nature.

        Parameters
        ----------
        sourcedata : str, file or pandas.DataFrame
            Data to be used for predictions.
            If str can be either a path to a local file, url to publicly
            available file or raw file content.
        project_name : str, unicode, optional
            The name to assign to the empty project.
        max_wait : int, optional
            Time in seconds after which project creation is considered
            unsuccessful

        Returns
        -------
        project : Project
            Instance with initialized data.

        Raises
        ------
        InputNotUnderstoodError
            Raised if `sourcedata` isn't one of supported types.
        AsyncFailureError
            Polling for status of async process resulted in response
            with unsupported status code. Beginning in version 2.1, this
            will be ProjectAsyncFailureError, a subclass of AsyncFailureError
        AsyncProcessUnsuccessfulError
            Raised if project creation was unsuccessful
        AsyncTimeoutError
            Raised if project creation took more time, than specified
            by ``max_wait`` parameter

        Examples
        --------
        .. code-block:: python

            p = Project.create('/home/datasets/somedataset.csv',
                               project_name="New API project")
            p.id
            >>> '5921731dkqshda8yd28h'
            p.project_name
            >>> 'New API project'
        """
        form_data = {"project_name": project_name}

        default_fname = "data.csv"
        if is_urlsource(sourcedata):
            form_data["url"] = sourcedata
            initial_project_post_response = cls._client.post(cls._path, data=form_data)
        else:
            filesource_kwargs = recognize_sourcedata(sourcedata, default_fname)
            initial_project_post_response = cls._client.build_request_with_file(
                url=cls._path,
                form_data=form_data,
                method='post',
                **filesource_kwargs)

        async_location = initial_project_post_response.headers['Location']
        return cls.from_async(async_location, max_wait)

    @classmethod
    def from_async(cls, async_location, max_wait=600):
        """
        Given a temporary async status location poll for no more than max_wait seconds
        until the async process (project creation or setting the target, for example)
        finishes successfully, then return the ready project

        Parameters
        ----------
        async_location : str
            The URL for the temporary async status resource. This is returned
            as a header in the response to a request that initiates an
            async process
        max_wait : int
            The maximum number of seconds to wait before giving up.

        Returns
        -------
        project : Project
            The project, now ready

        Raises
        ------
        ProjectAsyncFailureError
            If the server returned an unexpected response while polling for the
            asynchronous operation to resolve
        AsyncProcessUnsuccessfulError
            If the final result of the asynchronous operation was a failure
        AsyncTimeoutError
            If the asynchronous operation did not resolve within the time
            specified
        """
        try:
            for _ in retry.wait(max_wait):
                r = cls._client.get(async_location, join_endpoint=False, allow_redirects=False)
                if r.status_code == 303:
                    project_id = get_id_from_response(r)
                    return cls.get(project_id)
                response_data = r.json()
                status = response_data.get('status')
                if status == ASYNC_PROCESS_STATUS.ERROR or \
                        status == ASYNC_PROCESS_STATUS.ABORTED:
                    e_msg = 'Async process unsuccessful: {}'
                    raise errors.AsyncProcessUnsuccessfulError(
                        e_msg.format(response_data.get('message')))

            timeout_msg = (
                'Status did not reach 303 - it timed out in {} seconds; '
                'last status was {}: {}'
            ).format(max_wait, r.status_code, r.text)
            raise errors.AsyncTimeoutError(timeout_msg)

        except errors.AppPlatformError as e:
            raise errors.ProjectAsyncFailureError(repr(e), e.status_code, async_location)

    @classmethod
    def start(cls, sourcedata,
              target,
              project_name='Untitled Project',
              worker_count=None,
              metric=None,
              autopilot_on=True,
              recommender_settings=None,
              blueprint_threshold=None,
              response_cap=None,
              partitioning_method=None,
              positive_class=None,
              ):
        """
        Chain together project creation, file upload, and target selection.

        Parameters
        ----------
        sourcedata : str or pandas.DataFrame
            The path to the file to upload. Can be either a path to a
            local file or a publicly accessible URL.
            If the source is a DataFrame, it will be serialized to a
            temporary buffer.
        target : str
            The name of the target column in the uploaded file.
        project_name : str
            The project name.

        Other Parameters
        ----------------
        worker_count : int, optional
            The number of workers that you want to allocate to this project.
        metric : str, optional
            The name of metric to use.
        autopilot_on : boolean, default ``True``
            Whether or not to begin modeling automatically.
        recommender_settings : RecommenderSettings, optional
            Columns specified in this object tell the
            system how to set up the recommender system
        blueprint_threshold : int, optional
            Number of hours the model is permitted to run.
            Minimum 1
        response_cap : float, optional
            Quantile of the response distribution to use for response capping
            Must be in range 0.5 .. 1.0
        partitioning_method : PartitioningMethod object, optional
            It should be one of PartitioningMethod object.
        positive_class : str, float, or int; optional
            Specifies a level of the target column that should be used for
            binary classification. Can be used to specify any of the available
            levels as the binary target - all other levels will be treated
            as a single negative class.

        Returns
        -------
        project : Project
            The newly created and initialized project.

        Raises
        ------
        AsyncFailureError
            Polling for status of async process resulted in response
            with unsupported status code
        AsyncProcessUnsuccessfulError
            Raised if project creation or target setting was unsuccessful
        AsyncTimeoutError
            Raised if project creation or target setting timed out

        Examples
        --------

        .. code-block:: python

            Project.start("./tests/fixtures/file.csv",
                          "a_target",
                          project_name="test_name",
                          worker_count=4,
                          metric="a_metric")
        """

        # Create project part
        create_data = {'project_name': project_name, 'sourcedata': sourcedata}
        project = cls.create(**create_data)

        # Set target
        if autopilot_on:
            mode = AUTOPILOT_MODE.FULL_AUTO
        else:
            mode = AUTOPILOT_MODE.MANUAL

        advanced_options = AdvancedOptions(
            blueprint_threshold=blueprint_threshold,
            response_cap=response_cap
        )

        project.set_target(
            target, metric=metric, mode=mode,
            worker_count=worker_count,
            recommender_settings=recommender_settings,
            advanced_options=advanced_options,
            partitioning_method=partitioning_method,
            positive_class=positive_class)
        return project

    @classmethod
    def list(cls, search_params=None):
        """
        Returns the projects associated with this account.

        Parameters
        ----------
        search_params : dict, optional.
            If not `None`, the returned projects are filtered by lookup.
            Currently you can query projects by:

            * ``project_name``

        Returns
        -------
        projects : list of Project instances
            Contains a list of projects associated with this user
            account.

        Raises
        ------
        ValueError
            Raised if ``search_params`` parameter is provided,
            but is not of supported type.

        Examples
        --------
        List all projects
        .. code-block:: python

            p_list = Project.list()
            p_list
            >>> [Project('Project One'), Project('Two')]

        Search for projects by name
        .. code-block:: python

            Project.list(search_params={'project_name': 'red'})
            >>> [Project('Predtime'), Project('Fred Project')]

        """
        get_params = {}
        if search_params is not None:
            if isinstance(search_params, dict):
                get_params.update(search_params)
            else:
                raise TypeError(
                    'Provided search_params argument {} is invalid type {}'.format(
                        search_params, type(search_params)
                    ))
        r_data = cls._client.get(cls._path, params=get_params).json()
        return [cls(item) for item in r_data]

    @deprecated(deprecated_since_version='v2.2',
                will_remove_version='v2.4',
                message='Please use `rename`, `unlock_holdout`, or `set_worker_count` instead.')
    def update(self, **data):
        """
        Change the project properties.

        Other Parameters
        ----------------
        project_name : str, optional
            The name to assign to this project.

        holdout_unlocked : bool, optional
            Can only have value of `True`. If
            passed, unlocks holdout for project.

        worker_count : int, optional
            Sets number or workers

        Returns
        -------
        project : Project
            Instance with fields updated.
        """
        return self._update(**data)

    def _update(self, **data):
        """
        Change the project properties.

        In the future, DataRobot API will provide endpoints to directly
        update the attributes currently handled by this one endpoint.

        Other Parameters
        ----------------
        project_name : str, optional
            The name to assign to this project.

        holdout_unlocked : bool, optional
            Can only have value of `True`. If
            passed, unlocks holdout for project.

        worker_count : int, optional
            Sets number or workers

        Returns
        -------
        project : Project
            Instance with fields updated.
        """
        for key in (set(data) - {'project_name', 'holdout_unlocked', 'worker_count'}):
            raise TypeError("update() got an unexpected keyword argument '{}'".format(key))
        url = '{}{}/'.format(self._path, self.id)
        self._client.patch(url, data=data)
        self._set_up(data)
        return self

    def delete(self):
        """Removes this project from your account.
        """
        url = '{}{}/'.format(self._path, self.id)
        self._client.delete(url)

    def set_target(self, target,
                   mode=AUTOPILOT_MODE.FULL_AUTO,
                   metric=None,
                   quickrun=None,
                   worker_count=None,
                   positive_class=None,
                   recommender_settings=None,
                   partitioning_method=None,
                   featurelist_id=None,
                   advanced_options=None,
                   max_wait=600,
                   ):
        """
        Set target variable of an existing project that has a file uploaded
        to it.

        Target setting is asynchronous process, which means that after
        initial request we will keep polling status of async process
        that is responsible for target setting until it's finished.
        For SDK users this only means that this method might raise
        exceptions related to it's async nature.

        Parameters
        ----------
        target : str
            Name of variable.
        mode : int, optional
            You can use ``AUTOPILOT_MODE`` enum to choose between

            * ``AUTOPILOT_MODE.FULL_AUTO``
            * ``AUTOPILOT_MODE.SEMI_AUTO``
            * ``AUTOPILOT_MODE.MANUAL``

            If unspecified, ``FULL_AUTO`` is used
        metric : str, optional
            Name of the metric to use for evaluating models. You can query
            the metrics available for the target by way of
            ``Project.get_metrics``. If none is specified, then the default
            recommended by DataRobot is used.
        quickrun : bool, optional
            Sets whether project should be run in ``quick run`` mode. This
            setting causes DataRobot to recommend a more limited set of models
            in order to get a base set of models and insights more quickly.
        worker_count : int, optional
            The number of concurrent workers to request for this project. If
            `None`, then the default is used
        recommender_settings : RecommenderSettings, optional
            if not `None`, then the columns specified in this object tell the
            system how to set up the recommender system
        partitioning_method : PartitioningMethod object, optional
            It should be one of PartitioningMethod object.
        positive_class : str, float, or int; optional
            Specifies a level of the target column that treated as the
            positive class for binary classification.  May only be specified
            for binary classification targets.
        featurelist_id : str, optional
            Specifies which feature list to use.
        advanced_options : AdvancedOptions, optional
            Used to set advanced options of project creation.
        max_wait : int, optional
            Time in seconds after which target setting is considered
            unsuccessful.

        Returns
        -------
        project : Project
            The instance with updated attributes.

        Raises
        ------
        AsyncFailureError
            Polling for status of async process resulted in response
            with unsupported status code
        AsyncProcessUnsuccessfulError
            Raised if target setting was unsuccessful
        AsyncTimeoutError
            Raised if target setting took more time, than specified
            by ``max_wait`` parameter

        See Also
        --------
        Project.start : combines project creation, file upload, and target
            selection
        """
        if worker_count is not None:
            self.set_worker_count(worker_count)

        aim_payload = {
            'target': target,
            'mode': mode,
            'metric': metric,
        }
        if recommender_settings:
            self._load_recommender_settings(
                recommender_settings, aim_payload)
        if advanced_options is not None:
            self._load_advanced_options(
                advanced_options, aim_payload)
        if positive_class is not None:
            aim_payload['positive_class'] = positive_class
        if quickrun is not None:
            aim_payload['quickrun'] = quickrun
        if featurelist_id is not None:
            aim_payload['featurelist_id'] = featurelist_id
        if partitioning_method:
            self._load_partitioning_method(partitioning_method, aim_payload)
        url = '{}{}/aim/'.format(self._path, self.id)
        response = self._client.patch(url, data=aim_payload)
        async_location = response.headers['Location']

        # Waits for project to be ready for modeling, but ignores the return value
        self.from_async(async_location, max_wait=max_wait)

        proj_data = self._get_data(self.id)
        self._set_up(proj_data)
        return self

    def get_models(self, order_by=None, search_params=None, with_metric=None):
        """
        List all completed, successful models in the leaderboard for the given project.

        Parameters
        ----------
        order_by : str or list of strings, optional
            If not `None`, the returned models are ordered by this
            attribute. If `None`, the default return is the order of
            default project metric.

            Allowed attributes to sort by are:

            * ``metric``
            * ``sample_pct``

            If the sort attribute is preceded by a hyphen, models will be sorted in descending
            order, otherwise in ascending order.

            Multiple sort attributes can be included as a comma-delimited string or in a list
            e.g. order_by=`sample_pct,-metric` or order_by=[`sample_pct`, `-metric`]

            Using `metric` to sort by will result in models being sorted according to their
            validation score by how well they did according to the project metric.
        search_params : dict, optional.
            If not `None`, the returned models are filtered by lookup.
            Currently you can query models by:

            * ``name``
            * ``sample_pct``

        with_metric : str, optional.
            If not `None`, the returned models will only have scores for this
            metric. Otherwise all the metrics are returned.

        Returns
        -------
        models : a list of Model instances.
            All of the models that have been trained in this project.

        Raises
        ------
        ValueError
            Raised if ``order_by`` or ``search_params`` parameter is provided,
            but is not of supported type.

        Examples
        --------

        .. code-block:: python

            Project('pid').get_models(order_by=['-sample_pct',
                                                'metric'])

            # Getting models that contain "Ridge" in name
            # and with sample_pct more than 64
            Project('pid').get_models(
                search_params={
                    'sample_pct__gt': 64,
                    'name': "Ridge"
                })
        """
        from . import Model

        url = '{}{}/models/'.format(self._path, self.id)
        get_params = {}
        if order_by is not None:
            order_by = self._canonize_order_by(order_by)
            get_params.update({'order_by': order_by})
        else:
            get_params.update({'order_by': '-metric'})
        if search_params is not None:
            if isinstance(search_params, dict):
                get_params.update(search_params)
            else:
                raise TypeError(
                    'Provided search_params argument is invalid')
        if with_metric is not None:
            get_params.update({'with_metric': with_metric})
        resp_data = self._client.get(url, params=get_params).json()
        return [Model(item, project=self) for item in resp_data]

    def _canonize_order_by(self, order_by):
        legal_keys = [
            LEADERBOARD_SORT_KEY.SAMPLE_PCT,
            LEADERBOARD_SORT_KEY.PROJECT_METRIC,
        ]
        processed_keys = []
        if order_by is None:
            return order_by
        if isinstance(order_by, str):
            order_by = order_by.split(',')
        if not isinstance(order_by, list):
            msg = 'Provided order_by attribute {} is of an unsupported type'.format(order_by)
            raise TypeError(msg)
        for key in order_by:
            key = key.strip()
            if key.startswith('-'):
                prefix = '-'
                key = key[1:]
            else:
                prefix = ''
            if key not in legal_keys:
                camel_key = camelize(key)
                if camel_key not in legal_keys:
                    msg = 'Provided order_by attribute {}{} is invalid'.format(prefix, key)
                    raise ValueError(msg)
                key = camel_key
            processed_keys.append('{}{}'.format(prefix, key))
        return ','.join(processed_keys)

    def get_blueprints(self):
        """
        List all blueprints recommended for a project.

        Returns
        -------
        menu : list of Blueprint instances
            All the blueprints recommended by DataRobot for a project
        """
        from . import Blueprint

        url = '{}{}/blueprints/'.format(self._path, self.id)
        resp_data = self._client.get(url).json()
        return [Blueprint(item) for item in resp_data]

    def get_features(self):
        """
        List all features for this project

        Returns
        -------
        list of Features
            all feature for this project
        """
        url = '{}{}/features/'.format(self._path, self.id)
        resp_data = self._client.get(url).json()
        return [Feature(item) for item in resp_data]

    def get_featurelists(self):
        """
        List all featurelists created for this project

        Returns
        -------
        list of Featurelist
            all featurelists created for this project
        """
        from . import Featurelist

        url = '{}{}/featurelists/'.format(self._path, self.id)
        resp_data = self._client.get(url).json()
        return [Featurelist(item) for item in resp_data]

    def create_featurelist(self, name, features):
        """
        Creates a new featurelist

        Parameters
        ----------
        name : str
            The name to give to this new featurelist. Names must be unique, so
            an error will be returned from the server if this name has already
            been used in this project.
        features : list of str
            The names of the features. Each feature must exist in the project
            already.

        Returns
        -------
        Featurelist
            newly created featurelist

        Raises
        ------
        DuplicateFeaturesError
            Raised if `features` variable contains duplicate features

        Examples
        --------
        .. code-block:: python

            project = Project('5223deadbeefdeadbeef0101')
            flists = project.get_featurelists()

            # Create a new featurelist using a subset of features from an
            # existing featurelist
            flist = flists[0]
            features = flist.features[::2]  # Half of the features

            new_flist = project.create_featurelist(name='Feature Subset',
                                                   features=features)
        """
        from . import Featurelist

        url = '{}{}/featurelists/'.format(self._path, self.id)

        duplicate_features = get_duplicate_features(features)
        if duplicate_features:
            err_msg = "Can't create featurelist with duplicate " \
                      "features - {}".format(duplicate_features)
            raise errors.DuplicateFeaturesError(err_msg)

        payload = {
            'name': name,
            'features': features,
        }
        response = self._client.post(url, data=payload)
        new_id = get_id_from_response(response)
        flist_data = {'name': name,
                      'id': new_id,
                      'features': features,
                      'project_id': self.id}
        return Featurelist(flist_data)

    def get_metrics(self, feature_name):
        """Get the metrics recommended for modeling on the given feature.

        Parameters
        ----------
        feature_name : str
            The name of the feature to query regarding which metrics are
            recommended for modeling.

        Returns
        -------
        names : list of str
            The names of the recommended metrics.
        """
        url = '{}{}/features/metrics/'.format(self._path, self.id)
        params = {
            'feature_name': feature_name
        }
        return from_api(self._client.get(url, params=params).json())

    def get_status(self):
        """Query the server for project status.

        Returns
        -------
        status : dict
            Contains:

            * ``autopilot_done`` : a boolean.
            * ``stage`` : a short string indicating which stage the project
              is in.
            * ``stage_description`` : a description of what ``stage`` means.

        Examples
        --------

        .. code-block:: python

            {"autopilot_done": False,
             "stage": "modeling",
             "stage_description": "Ready for modeling"}
        """
        url = '{}{}/status/'.format(self._path, self.id)
        return from_api(self._client.get(url).json())

    def pause_autopilot(self):
        """
        Pause autopilot, which stops processing the next jobs in the queue.

        Returns
        -------
        paused : boolean
            Whether the command was acknowledged
        """
        url = '{}{}/autopilot/'.format(self._path, self.id)
        payload = {
            'command': 'stop'
        }
        self._client.post(url, data=payload)

        return True

    def unpause_autopilot(self):
        """
        Unpause autopilot, which restarts processing the next jobs in the queue.

        Returns
        -------
        unpaused : boolean
            Whether the command was acknowledged.
        """
        url = '{}{}/autopilot/'.format(self._path, self.id)
        payload = {
            'command': 'start',
        }
        self._client.post(url, data=payload)
        return True

    def start_autopilot(self, featurelist_id, mode=AUTOPILOT_MODE.FULL_AUTO):
        """Starts autopilot on provided featurelist.

        Only one autopilot can be running at the time.
        That's why any ongoing autopilot on a different featurelist will
        be halted - modeling jobs in queue would not
        be affected but new jobs would not be added to queue by
        the halted autopilot.

        Parameters
        ----------
        featurelist_id : str
            Identifier of featurelist that should be used for autopilot
        mode : str, optional
            Mode in which to run autopilot. You can use ``AUTOPILOT_MODE``
            enum to choose between

            * ``AUTOPILOT_MODE.FULL_AUTO``
            * ``AUTOPILOT_MODE.SEMI_AUTO``

            If unspecified, ``AUTOPILOT_MODE.FULL_AUTO`` is used

        Raises
        ------
        AppPlatformError
            Raised if autopilot is currently running on or has already
            finished running on the provided featurelist.
            Also raised if project's target was not selected.
        """
        url = '{}{}/autopilots/'.format(self._path, self.id)
        payload = {
            'featurelistId': featurelist_id,
            'mode': mode,
        }
        self._client.post(url, data=payload)

    def train(self, trainable, sample_pct=None, featurelist_id=None,
              source_project_id=None, scoring_type=None):
        """Submit a job to the queue.

        Parameters
        ----------
        trainable : str or Blueprint
            For ``str``, this is assumed to be a blueprint_id. If no
            ``source_project_id`` is provided, the ``project_id`` will be assumed
            to be the project that this instance represents.

            Otherwise, for a ``Blueprint``, it contains the
            blueprint_id and source_project_id that we want
            to use. ``featurelist_id`` will assume the default for this project
            if not provided, and ``sample_pct`` will default to using the maximum
            training value allowed for this project's partition setup.
            ``source_project_id`` will be ignored if a
            ``Blueprint`` instance is used for this parameter
        sample_pct : float, optional
            The amount of training data to use. Defaults to the maximum
            amount available based on the project configuration.
        featurelist_id : str, optional
            The identifier of the featurelist to use. If not defined, the
            default for this project is used.
        source_project_id : str, optional
            Which project created this blueprint_id. If ``None``, it defaults
            to looking in this project. Note that you must have read
            permissions in this project.
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
        Use a ``Blueprint`` instance:

        .. code-block:: python

            blueprint = project.get_blueprints()[0]
            model_job_id = project.train(blueprint, sample_pct=64)

        Use a ``blueprint_id``, which is a string. In the first case, it is
        assumed that the blueprint was created by this project. If you are
        using a blueprint used by another project, you will need to pass the
        id of that other project as well.

        .. code-block:: python

            blueprint_id = 'e1c7fc29ba2e612a72272324b8a842af'
            project.train(blueprint, sample_pct=64)

            another_project.train(blueprint, source_project_id=project.id)

       You can also easily use this interface to train a new model using the data from
       an existing model:

       .. code-block:: python

           model = project.get_models()[0]
           model_job_id = project.train(model.blueprint.id,
                                        sample_pct=100)

        """
        try:
            return self._train(trainable.id,
                               featurelist_id=featurelist_id,
                               source_project_id=trainable.project_id,
                               sample_pct=sample_pct,
                               scoring_type=scoring_type)
        except AttributeError:
            return self._train(trainable,
                               featurelist_id=featurelist_id,
                               source_project_id=source_project_id,
                               sample_pct=sample_pct,
                               scoring_type=scoring_type)

    def _train(self,
               blueprint_id,
               featurelist_id=None,
               source_project_id=None,
               sample_pct=None,
               scoring_type=None):
        """
        Submit a modeling job to the queue. Upon success, the new job will
        be added to the end of the queue.

        Parameters
        ----------
        blueprint_id: str
            The id of the model. See ``Project.get_blueprints`` to get the list
            of all available blueprints for a project.
        featurelist_id: str, optional
            The dataset to use in training. If not specified, the default
            dataset for this project is used.
        source_project_id : str, optional
            Which project created this blueprint_id. If ``None``, it defaults
            to looking in this project. Note that you must have read
            permisisons in this project.
        sample_pct: float, optional
            The amount of training data to use. Defaults to the maximum
            amount available based on the project configuration.

        Returns
        -------
        model_job_id : str
            id of created job, can be used as parameter to ``ModelJob.get``
            method or ``wait_for_async_model_creation`` function
        """
        url = '{}{}/models/'.format(self._path, self.id)
        payload = {'blueprint_id': blueprint_id}
        if featurelist_id is not None:
            payload['featurelist_id'] = featurelist_id
        if source_project_id is not None:
            payload['source_project_id'] = source_project_id
        if sample_pct is not None:
            payload['sample_pct'] = sample_pct
        if scoring_type is not None:
            payload['scoring_type'] = scoring_type
        response = self._client.post(url, data=payload)
        return get_id_from_response(response)

    def get_all_jobs(self, status=None):
        """Get a list of jobs

        Parameters
        ----------
        status : QUEUE_STATUS enum, optional
            If called with QUEUE_STATUS.INPROGRESS, will return the modeling jobs
            that are currently running.

            If called with QUEUE_STATUS.QUEUE, will return the modeling jobs that
            are waiting to be run.

            If called with QUEUE_STATUS.ERROR, will return the modeling jobs that
            have errored.

            If no value is provided, will return all modeling jobs currently running
            or waiting to be run.

        Returns
        -------
        jobs : list
            Each is an instance of Job
        """
        url = '{}{}/jobs/'.format(self._path, self.id)
        params = {'status': status}
        res = self._client.get(url, params=params).json()
        return [Job(item) for item in res['jobs']]

    @deprecated('v2.1', 'v2.3', message='Please use `get_model_jobs` instead.')
    def get_jobs(self, status=None):
        return self.get_model_jobs(status=status)

    def get_model_jobs(self, status=None):
        """Get a list of modeling jobs

        Parameters
        ----------
        status : QUEUE_STATUS enum, optional
            If called with QUEUE_STATUS.INPROGRESS, will return the modeling jobs
            that are currently running.

            If called with QUEUE_STATUS.QUEUE, will return the modeling jobs that
            are waiting to be run.

            If called with QUEUE_STATUS.ERROR, will return the modeling jobs that
            have errored.

            If no value is provided, will return all modeling jobs currently running
            or waiting to be run.

        Returns
        -------
        jobs : list
            Each is an instance of ModelJob
        """
        url = '{}{}/modelJobs/'.format(self._path, self.id)
        params = {'status': status}
        res = self._client.get(url, params=params).json()
        return [ModelJob(item) for item in res]

    def get_predict_jobs(self, status=None):
        """Get a list of prediction jobs

        Parameters
        ----------
        status : QUEUE_STATUS enum, optional
            If called with QUEUE_STATUS.INPROGRESS, will return the prediction jobs
            that are currently running.

            If called with QUEUE_STATUS.QUEUE, will return the prediction jobs that
            are waiting to be run.

            If called with QUEUE_STATUS.ERROR, will return the prediction jobs that
            have errored.

            If called without a status, will return all prediction jobs currently running
            or waiting to be run.

        Returns
        -------
        jobs : list
            Each is an instance of PredictJob
        """
        url = '{}{}/predictJobs/'.format(self._path, self.id)
        params = {'status': status}
        res = self._client.get(url, params=params).json()
        return [PredictJob(item) for item in res]

    def _get_job_status_counts(self):
        jobs = self.get_model_jobs()
        job_counts = collections.Counter(job.status for job in jobs)
        return job_counts[QUEUE_STATUS.INPROGRESS], job_counts[QUEUE_STATUS.QUEUE]

    def wait_for_autopilot(self, check_interval=20.0, timeout=24*60*60, verbosity=1):
        """
        Blocks until autopilot is finished.

        Parameters
        ----------
        check_interval : float or int
            The maximum time (in seconds) to wait between checks for whether autopilot is finished
        timeout : float or int or None
            After this long (in seconds), we give up. If None, never timeout.
        verbosity:
            This should be VERBOSITY_LEVEL.SILENT or VERBOSITY_LEVEL.VERBOSE.
            For VERBOSITY_LEVEL.SILENT, nothing will be displayed about progress.
            For VERBOSITY_LEVEL.VERBOSE, the number of jobs in progress or queued is shown.
            Note that new jobs are added to the queue along the way.
        """
        for _, seconds_waited in retry.wait(timeout, maxdelay=check_interval):
            if verbosity > VERBOSITY_LEVEL.SILENT:
                num_inprogress, num_queued = self._get_job_status_counts()
                logger.info("In progress: {0}, queued: {1} (waited: {2:.0f}s)".
                            format(num_inprogress, num_queued, seconds_waited))
            status = self.get_status()
            if status['autopilot_done']:
                return
        raise errors.AsyncTimeoutError('Autopilot did not finish within timeout period')

    def rename(self, project_name):
        """Update the name of the project.

        Parameters
        ----------
        project_name : str
            The new name
        """
        self._update(project_name=project_name)

    def unlock_holdout(self):
        """Unlock the holdout for this project.

        This will cause subsequent queries of the models of this project to
        contain the metric values for the holdout set, if it exists.

        Take care, as this cannot be undone. Remember that best practice is to
        select a model before analyzing the model performance on the holdout set
        """
        return self._update(holdout_unlocked=True)

    def set_worker_count(self, worker_count):
        """Sets the number of workers allocated to this project.

        Note that this value is limited to the number allowed by your account.
        Lowering the number will not stop currently running jobs, but will
        cause the queue to wait for the appropriate number of jobs to finish
        before attempting to run more jobs.

        Parameters
        ----------
        worker_count : int
            The number of concurrent workers to request from the pool of workers
        """
        return self._update(worker_count=worker_count)

    def get_leaderboard_ui_permalink(self):
        """
        Returns
        -------
        url : str
            Permanent static hyperlink to a project leaderboard.
        """
        return '{}/{}{}/models'.format(self._client.domain, self._path, self.id)

    def open_leaderboard_browser(self):
        """
        Opens project leaderboard in web browser.

        Note:
        If text-mode browsers are used, the calling process will block
        until the user exits the browser.
        """

        url = self.get_leaderboard_ui_permalink()
        return webbrowser.open(url)
