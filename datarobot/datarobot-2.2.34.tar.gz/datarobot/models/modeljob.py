import six
import trafaret as t

from .. import errors
from ..client import get_client, staticproperty
from ..enums import JOB_TYPE, MODEL_JOB_STATUS
from .job import Job
from ..utils import SetupFieldsMetaclass, from_api, retry


def wait_for_async_model_creation(project_id, model_job_id, max_wait=600):
    """
    Given a Project id and ModelJob id poll for status of process
    responsible for model creation until model is created.

    Parameters
    ----------
    project_id : str
        The identifier of the project

    model_job_id : str
        The identifier of the ModelJob

    max_wait : int, optional
        Time in seconds after which model creation is considered
        unsuccessful

    Returns
    -------
    model : Model
        Newly created model

    Raises
    ------
    AsyncModelCreationError
        Raised if status of fetched ModelJob object is ``error``
    AsyncTimeoutError
        Model wasn't created in time, specified by ``max_wait`` parameter
    """
    for _ in retry.wait(max_wait):
        try:
            model_job = ModelJob.get(project_id, model_job_id)
        except errors.PendingJobFinished:
            return ModelJob.get_model(project_id, model_job_id)
        if model_job.status == MODEL_JOB_STATUS.ERROR:
            e_msg = 'Model creation unsuccessful'
            raise errors.AsyncModelCreationError(e_msg)

    timeout_msg = 'Model creation timed out in {} seconds'.format(max_wait)
    raise errors.AsyncTimeoutError(timeout_msg)


class ModelJob(six.with_metaclass(SetupFieldsMetaclass, object), Job):
    _client = staticproperty(get_client)
    _fields = frozenset(['id',
                         'status',
                         'sample_pct',
                         'model_type',
                         'processes'])

    _path = 'projects/{}/modelJobs/{}/'

    def __repr__(self):
        return 'ModelJob({}, status={})'.format(self.model_type,
                                                self.status)  # pragma:no cover

    def __init__(self, data):
        self.id = None
        self.blueprint = None
        self.project = None
        self.processes = None
        self.job_type = JOB_TYPE.MODEL
        self.model_type = None
        self.status = None
        self.sample_pct = None
        self.featurelist_id = None

        self._data = data
        if isinstance(data, dict):
            self._set_up(data)
        else:
            raise ValueError

    def _set_up(self, data):
        from . import Project, Blueprint

        data = from_api(data)
        # Construction Project
        self.project = Project(data.get('project_id'))

        # Construction Blueprint
        bp_data = {'id': data.get('blueprint_id'),
                   'processes': data.get('processes'),
                   'model_type': data.get('model_type'),
                   'project_id': data.get('project_id')}
        self.blueprint = Blueprint(bp_data)

        converter = t.Dict({
            t.Key('id', optional=True) >> 'id': t.Int,
            t.Key('status', optional=True) >> 'status': t.String,
            t.Key('sample_pct', optional=True) >> 'sample_pct': t.Float,
            t.Key('model_type', optional=True) >> 'model_type': t.String,
            t.Key('processes', optional=True) >> 'processes': t.List(t.String),
            t.Key('featurelistId', optional=True) >> 'featurelist_id': t.List(t.String),
        }).allow_extra("*")

        for k, v in six.iteritems(converter.check(data)):
            if k in self._fields:
                setattr(self, k, v)

        self._path = self._path.format(data.get('project_id'), data.get('id'))

    @classmethod
    def from_job(cls, job):
        """ Transforms a generic Job into a ModelJob

        Parameters
        ----------
        job: Job
            A generic job representing a ModelJob

        Returns
        -------
        model_job: ModelJob
            A fully populated ModelJob with all the details of the job

        Raises
        ------
        ValueError:
            If the generic Job was not a model job, e.g. job_type != JOB_TYPE.MODEL
        """
        if not job.job_type == JOB_TYPE.MODEL:
            raise ValueError('wrong job_type: {}'.format(job.job_type))
        data = job._get_full_details()
        return ModelJob(data)

    @classmethod
    def get(cls, project_id, model_job_id):
        """
        Fetches one ModelJob. If the job finished, raises PendingJobFinished
        exception.

        Parameters
        ----------
        project_id : str
            The identifier of the project the model belongs to
        model_job_id : str
            The identifier of the model_job

        Returns
        -------
        model_job : ModelJob
            The pending ModelJob

        Raises
        ------
        PendingJobFinished
            If the job being queried already finished, and the server is
            re-routing to the finished model.
        AsyncFailureError
            Querying this resource gave a status code other than 200 or 303
        """
        url = cls._path.format(project_id, model_job_id)
        response = cls._client.get(url, allow_redirects=False)
        if response.status_code == 200:
            data = response.json()
            return cls(data)
        elif response.status_code == 303:
            raise errors.PendingJobFinished
        else:
            e_msg = 'Server unexpectedly returned status code {}'
            raise errors.AsyncFailureError(
                e_msg.format(response.status_code))

    @classmethod
    def get_model(cls, project_id, model_job_id):
        """
        Fetches a finished model from the job used to create it.

        Parameters
        ----------
        project_id : str
            The identifier of the project the model belongs to
        model_job_id : str
            The identifier of the model_job

        Returns
        -------
        model : Model
            The finished model

        Raises
        ------
        JobNotFinished
            If the job has not finished yet
        AsyncFailureError
            Querying the model_job in question gave a status code other than 200 or
            303
        """
        from . import Model

        url = cls._path.format(project_id, model_job_id)
        response = cls._client.get(url, allow_redirects=False)
        if response.status_code == 200:
            data = response.json()
            raise errors.JobNotFinished('Pending job status is {}'.format(data['status']))
        elif response.status_code == 303:
            location = response.headers['Location']
            model_data = Model.fetch_resource_data(location, join_endpoint=False)
            return Model(data=model_data)
        else:
            e_msg = 'Server unexpectedly returned status code {}'
            raise errors.AsyncFailureError(
                e_msg.format(response.status_code))

    def cancel(self):
        """
        Cancel this job. If this job has not finished running, it will be
        removed and canceled.
        """
        self._client.delete(self._path)
