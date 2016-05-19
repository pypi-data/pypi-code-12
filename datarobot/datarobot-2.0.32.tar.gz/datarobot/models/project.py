import time
import webbrowser

import six
import trafaret as t

from datarobot.errors import (AppPlatformError, AsyncTimeoutError,
                              AsyncFailureError, AsyncProcessUnsuccessfulError,
                              DuplicateFeaturesError, )
from datarobot.client import get_client
from datarobot.helpers.partitioning_methods import BasePartitioningMethod
from datarobot.helpers import (RecommenderSettings,
                               AdvancedOptions)

from datarobot.utils import (SetupFieldsMetaclass, from_api,
                             enum, parse_time, get_id_from_response,
                             get_duplicate_features, camelize,
                             deprecated, deprecation_warning,
                             is_urlsource, recognize_sourcedata)


import warnings

warnings.simplefilter('default', DeprecationWarning)


QUEUE_STATUS = enum(QUEUE='queue',
                    INPROGRESS='inprogress',
                    ERROR='error')

AUTOPILOT_MODE = enum(FULL_AUTO=0,
                      SEMI_AUTO=1,
                      MANUAL=2)

PROJECT_STAGE = enum(EMPTY='empty',
                     EDA='eda',
                     AIM='aim',
                     MODELING='modeling')

ASYNC_PROCESS_STATUS = enum(INITIALIZED='INITIALIZED',
                            RUNNING='RUNNING',
                            COMPLETED='COMPLETED',
                            ERROR='ERROR',
                            ABORTED='ABORTED', )

LEADERBOARD_SORT_KEY = enum(FINISH_TIME='finishTime',
                            PROJECT_METRIC='metric',
                            SAMPLE_PCT='samplePct',
                            START_TIME='startTime')


def _get_target_name(target_obj):
    if isinstance(target_obj, dict):
        return target_obj.get('target_name')
    elif isinstance(target_obj, six.string_types):
        return target_obj


class Project(six.with_metaclass(SetupFieldsMetaclass, object)):

    _client = None
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
        self._client = get_client()  # pragma:no cover
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
            raise AppPlatformError('method object should inherit'
                                   ' from BasePartitioningMethod')
        payload.update(method.collect_payload())

    @staticmethod
    def _load_recommender_settings(settings, payload):
        if not isinstance(settings, RecommenderSettings):
            raise AppPlatformError('settings object should inherit'
                                   ' from RecommenderSettings')
        payload.update(settings.collect_payload())

    @staticmethod
    def _load_advanced_options(opts, payload):
        if not isinstance(opts, AdvancedOptions):
            raise AppPlatformError('advanced options object should inherit'
                                   ' from AdvancedOptions')
        payload.update(opts.collect_payload())

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               self.project_name or self.id)

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
        client = cls._client or get_client()
        url = '{}{}/'.format(cls._path, project_id)
        data = client.get(url).json()
        return data

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

            from datarobot import Project
            p = Project.get(project_id='54e639a18bd88f08078ca831')
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
        project_name : str, optional
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
        AppPlatformError
            Raised if `sourcedata` isn't one of supported types.
        AsyncFailureError
            Polling for status of async process resulted in response
            with unsupported status code
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
        client = cls._client or get_client()
        form_data = {"project_name": project_name}

        default_fname = '{}.csv'.format(project_name)
        filesource_kwargs = recognize_sourcedata(sourcedata, default_fname)
        if filesource_kwargs:
            initial_project_post_response = client.build_request_with_file(
                url=cls._path,
                form_data=form_data,
                method='post',
                **filesource_kwargs)
        elif is_urlsource(sourcedata):
            form_data["url"] = sourcedata
            initial_project_post_response = client.post(cls._path, data=form_data)
        else:
            err_msg = ('sourcedata parameter not understood. Use pandas '
                       'DataFrame, file object or string that is either a '
                       'path to local file, url to publicly available file '
                       'or raw file content to specify data '
                       'to upload')
            raise AppPlatformError(err_msg)

        r_data = cls._wait_for_async_status_service(
            initial_project_post_response,
            max_wait=max_wait,
        )

        project_id = get_id_from_response(r_data)
        return cls({'id': project_id, 'project_name': project_name})

    @classmethod
    def _wait_for_async_status_service(cls, response, max_wait=600):
        """Given a temporary async status location poll for no more than max_wait seconds
        until it turns into a 303, which means that async process (project creation
        or target setting, for example) finished successfully.
        """
        wait_time_for_check = .1
        async_location = response.headers['Location']
        start = time.time()
        now = start
        client = cls._client or get_client()
        while now < start + max_wait:
            r = client.get(async_location, join_endpoint=False,
                           allow_redirects=False)
            if r.status_code == 303:
                return r
            if r.status_code != 200:
                e_msg = 'Status service check failed {}: {}'
                raise AsyncFailureError(e_msg.format(r.status_code, r.text))
            response_data = r.json()
            status = response_data.get('status')
            if status == ASYNC_PROCESS_STATUS.ERROR or \
                    status == ASYNC_PROCESS_STATUS.ABORTED:
                e_msg = 'Async process unsuccessful: {}'
                raise AsyncProcessUnsuccessfulError(
                    e_msg.format(response_data.get('message')))
            time.sleep(wait_time_for_check)
            now = time.time()
            wait_time_for_check = min(wait_time_for_check * 2, 1)

        timeout_msg = (
            'Status did not reach 303 - it timed out in {} seconds; '
            'last status was {}: {}'
        ).format(max_wait, r.status_code, r.text)
        raise AsyncTimeoutError(timeout_msg)

    @classmethod
    def start(cls, sourcedata,
              target,
              project_name='Untitled Project',
              worker_count=None,
              metric=None,
              autopilot_on=True,
              recommender_settings=None,
              recommendation_settings=None,
              blueprint_threshold=None,
              response_cap=None,
              partitioning_method=None,
              positive_class=None
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
        recommendation_settings : RecommenderSettings, optional
            Deprecated, please use `recommender_settings` instead
            If both `recommendation_settings` and `recommender_settings`
            parameters are provided the latter would be used
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

        if recommendation_settings is not None:
            deprecation_warning(
                'recommendation_settings parameter',
                deprecated_since_version='v0.2',
                will_remove_version='v2.2',
                message='Please use `recommender_settings` instead.')

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
            recommender_settings=recommender_settings or recommendation_settings,
            advanced_options=advanced_options,
            partitioning_method=partitioning_method,
            positive_class=positive_class)
        return project

    @classmethod
    def list(cls, search_params=None, order_by=None):
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
        if order_by is not None:
            msg = 'Deprecation is in order to facilitate pending improvements to Project.list.'
            deprecation_warning(
                'order_by parameter',
                deprecated_since_version='v2.0',
                will_remove_version='v2.2',
                message=msg)

        client = cls._client or get_client()
        get_params = {}
        if order_by is not None:
            if isinstance(order_by, str):
                get_params.update({'order_by': order_by})
            elif isinstance(order_by, list):
                get_params.update({'order_by': ','.join(order_by)})
            else:
                raise AppPlatformError(
                    'Provided order_by argument is invalid')
        if search_params is not None:
            if isinstance(search_params, dict):
                get_params.update(search_params)
            else:
                raise AppPlatformError(
                    'Provided search_params argument is invalid')
        r_data = client.get(cls._path, params=get_params).json()
        return [cls(item) for item in r_data]

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

        client = self._client or get_client()
        url = '{}{}/'.format(self._path, self.id)
        client.patch(url, data=data)
        self._set_up(data)
        return self

    def delete(self):
        """Removes this project from your account.
        """

        client = self._client or get_client()
        url = '{}{}/'.format(self._path, self.id)
        client.delete(url)
        return None

    def set_target(self, target,
                   mode=AUTOPILOT_MODE.FULL_AUTO,
                   metric=None,
                   quickrun=None,
                   worker_count=None,
                   positive_class=None,
                   recommender_settings=None,
                   partitioning_method=None,
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
            Specifies a level of the target column that should be used for
            binary classification. Can be used to specify any of the available
            levels as the binary target - all other levels will be treated
            as a single negative class.
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
        if partitioning_method:
            self._load_partitioning_method(partitioning_method, aim_payload)
        client = self._client or get_client()
        url = '{}{}/aim/'.format(self._path, self.id)
        response = client.patch(url, data=aim_payload)
        self._wait_for_async_status_service(response, max_wait=max_wait)

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
            * ``start_time``
            * ``finish_time``

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
            * ``start_time``
            * ``finish_time``

        with_metric : str, optional.
            If not `None`, the returned models will only have scores for this
            metric. Otherwise all the metrics are returned.

        Returns
        -------
        models : a list of Model instances.
            All of the models that have been trained in this project.

        Raises
        ------
        AppPlatformError
            Raised if ``order_by`` or ``search_params`` parameter is provided,
            but is not of supported type.

        Examples
        --------

        .. code-block:: python

            Project('pid').get_models(order_by=['-finish_time',
                                                'sample_pct',
                                                'metric'])

            # Getting models that contain "Ridge" in name
            # created within the last day and with sample_pct more than 64
            import datetime
            day_before = datetime.datetime.now() - datetime.timedelta(days=1)
            Project('pid').get_models(
                search_params={
                    'sample_pct__gt': 64,
                    'start_time__gte': day_before,
                    'name': "Ridge"
                })
        """
        from datarobot.models import Model

        client = self._client or get_client()
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
                raise AppPlatformError(
                    'Provided search_params argument is invalid')
        if with_metric is not None:
            get_params.update({'with_metric': with_metric})
        resp_data = client.get(url, params=get_params).json()
        return [Model(item, project=self) for item in resp_data]

    def _canonize_order_by(self, order_by):
        legal_keys = [LEADERBOARD_SORT_KEY.FINISH_TIME, LEADERBOARD_SORT_KEY.PROJECT_METRIC,
                      LEADERBOARD_SORT_KEY.SAMPLE_PCT, LEADERBOARD_SORT_KEY.START_TIME]
        processed_keys = []
        if order_by is None:
            return order_by
        if isinstance(order_by, str):
            order_by = order_by.split(',')
        if not isinstance(order_by, list):
            msg = 'Provided order_by attribute {} is of an unsupported type'.format(order_by)
            raise AppPlatformError(msg)
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
                    raise AppPlatformError(msg)
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
        from datarobot.models import Blueprint

        client = self._client or get_client()
        url = '{}{}/blueprints/'.format(self._path, self.id)
        resp_data = client.get(url).json()
        return [Blueprint(item) for item in resp_data]

    def get_featurelists(self):
        """
        List all featurelists created for this project

        Returns
        -------
        list of Featurelist
            all featurelists created for this project
        """
        from datarobot import Featurelist

        client = self._client or get_client()
        url = '{}{}/featurelists/'.format(self._path, self.id)
        resp_data = client.get(url).json()
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
        from datarobot import Featurelist

        client = self._client or get_client()
        url = '{}{}/featurelists/'.format(self._path, self.id)

        duplicate_features = get_duplicate_features(features)
        if duplicate_features:
            err_msg = "Can't create featurelist with duplicate " \
                      "features - {}".format(duplicate_features)
            raise DuplicateFeaturesError(err_msg)

        payload = {
            'name': name,
            'features': features,
        }
        response = client.post(url, data=payload)
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
        client = self._client or get_client()
        params = {
            'feature_name': feature_name
        }
        return from_api(client.get(url,
                                   params=params).json())

    @deprecated(deprecated_since_version='v0.2',
                will_remove_version='v2.2',
                message='Please use `get_status` instead.')
    def status(self):
        """Query the server for project status.

        Deprecated - please see ``get_status``

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

            {"autopilotDone": False,
             "stage": "modeling",
             "stageDescription": "Ready for modeling"}
        """
        url = '{}{}/status/'.format(self._path, self.id)
        client = self._client or get_client()
        return client.get(url).json()

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
        client = self._client or get_client()
        return from_api(client.get(url).json())

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
        client = self._client or get_client()
        client.post(url, data=payload)

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
        client = self._client or get_client()
        client.post(url, data=payload)
        return True

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
        scoring_type : str
             Either SCORING_TYPE.validation or SCORING_TYPE.cross_validation.
             Validation is available for every partitioning type, and indicates
             that the default model validation should be used for the project.
             If the project uses a form of cross-validation partitioning,
             ``cross_validation`` can also be used to indicate that all of the
             available training/validation combinations should be used to
             evaluate the model.

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
        client = self._client or get_client()
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
        response = client.post(url, data=payload)
        return get_id_from_response(response)

    def get_jobs(self, status=None):
        """Get a list of jobs

        In future versions this will be deprecated in favor of `get_model_jobs`.

        Parameters
        ----------
        status : QUEUE_STATUS enum, optional
            If called with QUEUE_STATUS.INPROGRESS, will return the jobs
            that are currently running.
            If called with QUEUE_STATUS.QUEUE, will return the jobs that
            are waiting to be run.
            If called with QUEUE_STATUS.ERROR, will return the jobs that
            have errored
            If no value is provided, then all the jobs will be returned

        Returns
        -------
        jobs : list
            Each is an instance of datarobot.models.ModelJob
        """
        return self.get_model_jobs(status)

    def get_model_jobs(self, status=None):
        """Get a list of jobs

        Parameters
        ----------
        status : QUEUE_STATUS enum, optional
            If called with QUEUE_STATUS.INPROGRESS, will return the jobs
            that are currently running.
            If called with QUEUE_STATUS.QUEUE, will return the jobs that
            are waiting to be run.
            If called with QUEUE_STATUS.ERROR, will return the jobs that
            have errored
            If no value is provided, then all the jobs will be returned

        Returns
        -------
        jobs : list
            Each is an instance of datarobot.models.ModelJob
        """
        from datarobot.models import ModelJob

        client = self._client or get_client()
        url = '{}{}/modelJobs/'.format(self._path, self.id)
        params = {'status': status}
        res = client.get(url, params=params).json()
        return [ModelJob(item) for item in res]

    def unlock_holdout(self):
        """Unlock the holdout for this project.

        This will cause subsequent queries of the models of this project to
        contain the metric values for the holdout set, if it exists.

        Take care, as this cannot be undone. Remember that best practice is to
        select a model before analyzing the model performance on the holdout set
        """
        return self.update(holdout_unlocked=True)

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
        payload = {'worker_count': worker_count}
        return self.update(**payload)

    @deprecated(deprecated_since_version='v0.2',
                will_remove_version='v2.2')
    def wait_for_aim_stage(self):
        """
        Blocking call.

        Suspends execution of the current thread until stage of project
        instance is ``aim``. At that time it is safe to set the target or query
        which metrics are recommended for a feature.

        It should be used when uploading large files into a project, as
        DataRobot may take some time to process the data, and will error if
        you try to set the target before that processing completes.

        .. code-block:: python

            from datarobot import Project
            p = Project.create('atleast200mb.csv',
                               project_name='project_with_big_file')
            p.wait_for_aim_stage()
            p.set_target('my_target')

        """
        for i in range(10):
            if self.get_status()['stage'] == PROJECT_STAGE.AIM:
                break
            time.sleep(1.5)

    def get_leaderboard_ui_permalink(self):
        """
        Returns
        -------
        url : str
            Permanent static hyperlink to a project leaderboard.
        """
        client = self._client or get_client()
        url = '{domain}/{path}{id}/models'.format(domain=client.domain,
                                                  path=self._path,
                                                  id=self.id)
        return url

    def open_leaderboard_browser(self):
        """
        Opens project leaderboard in web browser.

        Note:
        If text-mode browsers are used, the calling process will block
        until the user exits the browser.
        """

        url = self.get_leaderboard_ui_permalink()
        return webbrowser.open(url)
