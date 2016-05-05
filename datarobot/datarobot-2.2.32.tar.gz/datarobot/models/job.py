import trafaret as t

from ..client import get_client, staticproperty
from ..enums import JOB_TYPE, QUEUE_STATUS
from ..utils import from_api


class Job(object):
    """ Generic representation of a job in the queue
    """
    _client = staticproperty(get_client)

    def __init__(self, data):
        self.id = None
        self.project = None
        self.job_type = None
        self.status = None
        self._path = None

        self._data = data
        if isinstance(data, dict):
            self._set_up(data)
        else:
            raise ValueError('job data must be a dict')

    def _set_up(self, data):
        # Importing here to dodge circular dependency - pattern copied from ModelJob/PredictJob
        from . import Project

        data = from_api(data)
        self.project = Project(data.get('project_id'))

        converter = t.Dict({
            t.Key('id', optional=True) >> 'id': t.Int,
            t.Key('status', optional=True) >> 'status': t.String,
            t.Key('project_id', optional=True) >> 'project_id': t.String,
            t.Key('job_type', optional=True) >> 'job_type': t.String,
            t.Key('url') >> 'url': t.String
        }).allow_extra("*")

        try:
            safe_data = converter.check(data)
        except t.DataError as e:
            raise ValueError('Invalid data: {}'.format(str(e)))

        job_type = safe_data.get('job_type')
        if job_type not in [JOB_TYPE.MODEL, JOB_TYPE.PREDICT]:
            raise ValueError('Invalid job_type: {}'.format(job_type))

        status = safe_data.get('status')
        if status not in [QUEUE_STATUS.QUEUE, QUEUE_STATUS.INPROGRESS, QUEUE_STATUS.ERROR]:
            raise ValueError('Invalid status: {}'.format(job_type))

        self.id = safe_data.get('id')
        self.project = Project(safe_data.get('project_id'))
        self.job_type = job_type
        self.status = status
        self._path = self._client.strip_endpoint(safe_data['url'])

    def __repr__(self):
        return 'Job({}, status={})'.format(self.job_type, self.status)

    def _get_full_details(self):
        response = self._client.get(self._path)
        return response.json()

    def cancel(self):
        """ Cancel a running job
        """
        self._client.delete(self._path)
