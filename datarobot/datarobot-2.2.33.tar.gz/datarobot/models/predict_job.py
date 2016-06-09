import six
import trafaret as t

from .. import errors
from ..client import get_client, staticproperty
from ..enums import JOB_TYPE, PREDICT_JOB_STATUS
from .job import Job
from ..utils import (
    raw_prediction_response_to_dataframe,
    recognize_sourcedata,
    get_id_from_response,
    SetupFieldsMetaclass,
    from_api,
    retry,
)


def wait_for_async_predictions(project_id, predict_job_id, max_wait=600):
    """
    Given a Project id and PredictJob id poll for status of process
    responsible for predictions generation until it's finished

    Parameters
    ----------
    project_id : str
        The identifier of the project
    predict_job_id : str
        The identifier of the PredictJob
    max_wait : int, optional
        Time in seconds after which predictions creation is considered
        unsuccessful

    Returns
    -------
    predictions : pandas.DataFrame
        Generated predictions.

    Raises
    ------
    AsyncPredictionsGenerationError
        Raised if status of fetched PredictJob object is ``error``
    AsyncTimeoutError
        Predictions weren't generated in time, specified by ``max_wait``
        parameter
    """
    for index in retry.wait(max_wait):
        try:
            predict_job = PredictJob.get(project_id, predict_job_id)
        except errors.PendingJobFinished:
            return PredictJob.get_predictions(project_id, predict_job_id)
        if predict_job.status in (PREDICT_JOB_STATUS.ERROR, PREDICT_JOB_STATUS.ABORTED):
            e_msg = 'Predictions generation unsuccessful'
            raise errors.AsyncPredictionsGenerationError(e_msg)

    timeout_msg = 'Predictions generation timed out in {} seconds'.format(
        max_wait)
    raise errors.AsyncTimeoutError(timeout_msg)


class PredictJob(six.with_metaclass(SetupFieldsMetaclass, object), Job):
    _client = staticproperty(get_client)
    _fields = frozenset(['id',
                         'status',
                         'message'])
    _path = 'projects/{}/predictJobs/{}/'

    def __init__(self, data):
        self.id = None
        self.job_type = JOB_TYPE.PREDICT
        self.model = None
        self.project = None
        self.status = None
        self.message = None

        self._data = data
        if isinstance(data, dict):
            self._set_up(data)
        else:
            raise ValueError

    def _set_up(self, data):
        from . import Project, Model
        data = from_api(data)

        self.model = Model((data.get('project_id'), data.get('model_id')))
        self.project = Project(data.get('project_id'))

        converter = t.Dict({
            t.Key('id', optional=True) >> 'id': t.Int,
            t.Key('status', optional=True) >> 'status': t.String,
            t.Key('message', optional=True, default='') >> 'message': t.String(allow_blank=True),
        }).allow_extra('*')

        for k, v in six.iteritems(converter.check(data)):
            if k in self._fields:
                setattr(self, k, v)

        self._path = self._path.format(data.get('project_id'), data.get('id'))

    def __repr__(self):
        return 'PredictJob({}, status={})'.format(self.model,
                                                  self.status)  # pragma:no cover

    @classmethod
    def from_job(cls, job):
        """ Transforms a generic Job into a PredictJob

        Parameters
        ----------
        job: Job
            A generic job representing a PredictJob

        Returns
        -------
        predict_job: PredictJob
            A fully populated PredictJob with all the details of the job

        Raises
        ------
        ValueError:
            If the generic Job was not a predict job, e.g. job_type != JOB_TYPE.PREDICT
        """
        if not job.job_type == JOB_TYPE.PREDICT:
            raise ValueError('wrong job_type: {}'.format(job.job_type))
        data = job._get_full_details()
        return PredictJob(data)

    @classmethod
    def create(cls, model, sourcedata):
        """
        Starts predictions generation for provided data
        using previously created model.

        Parameters
        ----------
        model : Model
            Model to use for predictions generation
        sourcedata : str, file or pandas.DataFrame
            Data to be used for predictions.
            If str can be either a path to a local file or raw file content.

        Returns
        -------
        predict_job_id : str
            id of created job, can be used as parameter to ``PredictJob.get``
            or ``PredictJob.get_predictions`` methods or
            ``wait_for_async_predictions`` function

        Raises
        ------
        InputNotUnderstoodError
            If the parameter for sourcedata didn't resolve into known data types

        Examples
        --------
        .. code-block:: python

            model = Model.get('p-id', 'l-id')
            predict_job = PredictJob.create(model, './data_to_predict.csv')
        """
        url = 'projects/{}/predictions/'.format(model.project.id)
        form_data = {'model_id': model.id}
        default_fname = 'predict.csv'
        filesource_kwargs = recognize_sourcedata(sourcedata, default_fname)

        response = cls._client.build_request_with_file(
            url=url,
            form_data=form_data,
            method='post',
            **filesource_kwargs)
        return get_id_from_response(response)

    @classmethod
    def get(cls, project_id, predict_job_id):
        """
        Fetches one PredictJob. If the job finished, raises PendingJobFinished
        exception.

        Parameters
        ----------
        project_id : str
            The identifier of the project the model on which prediction
            was started belongs to
        predict_job_id : str
            The identifier of the predict_job

        Returns
        -------
        predict_job : PredictJob
            The pending PredictJob

        Raises
        ------
        PendingJobFinished
            If the job being queried already finished, and the server is
            re-routing to the finished predictions.
        AsyncFailureError
            Querying this resource gave a status code other than 200 or 303
        """
        url = cls._path.format(project_id, predict_job_id)
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
    def get_predictions(cls, project_id, predict_job_id):
        """
        Fetches finished predictions from the job used to generate them.

        Parameters
        ----------
        project_id : str
            The identifier of the project to which belongs the model used
            for predictions generation
        predict_job_id : str
            The identifier of the predict_job

        Returns
        -------
        predictions : pandas.DataFrame
            Generated predictions

        Raises
        ------
        JobNotFinished
            If the job has not finished yet
        AsyncFailureError
            Querying the predict_job in question gave a status code other than 200 or
            303
        """
        url = cls._path.format(project_id, predict_job_id)
        response = cls._client.get(url, allow_redirects=False)
        if response.status_code == 200:
            data = response.json()
            raise errors.JobNotFinished('Pending job status is {}'.format(data['status']))
        elif response.status_code == 303:
            location = response.headers['Location']
            response = cls._client.get(location, join_endpoint=False)
            return raw_prediction_response_to_dataframe(response.json())
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
