import requests
import json
import logging
import bunch

logger = logging.getLogger(__name__)

class BadStatus(Exception): pass

ANNOTATION_TYPES = bunch.Bunch(point = 'point', rectangle = 'rectangle')

class Crunchable(object):
    CRUNCHABLE_ENDPOINT = 'https://api.crunchable.io'

    def __init__(self, token, base_url=CRUNCHABLE_ENDPOINT):
        self.token = token
        self.base_url = base_url
        self.headers = {
            'X-Crunch-API-Key': token, 
            'content-type': 'application/json'
        }
    
    def _get_json(self, url):
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            raise BadStatus(response.status_code)
        return response.json()

    def _post(self, url, data = {}):
        response = requests.post(url, data=json.dumps(data), headers=self.headers)
        if response.status_code != 200:
            raise BadStatus(response.status_code)
        return response.json()


    def get_task(self, task_id, block=0):
        return self._get_json(self.base_url + '/v1/requests/{}?block={}'.format(task_id, block))

    def wait_for_task(self, task_id):
        while True:
            try:
                task = self.get_task(task_id, block=120)
                if task['status'] == 'complete':
                    return task
            except Exception as e:
                logger.warning('Error while waiting for task: {}'.format(e))
                pass

    def get_batches(self):
        return (self._get_json(self.base_url + '/v1/batch'))['batches']

    def get_batch(self, batch_id):
        return (self._get_json(self.base_url + '/v1/batch/' + batch_id))['tasks']

    def abort_task(self, task_id):
        return self._post(self.base_url + '/v1/tasks/abort/' + task_id)

    def archive_task(self, task_id):
        return self._post(self.base_url + '/v1/tasks/archive/' + task_id)

    def request(self, req_type, 
            instruction, 
            attachments_type='text', 
            attachments=[], 
            tags=[],
            hook_url=None,
            **extra):
        task = dict(
            instruction = instruction,
            attachments_type = attachments_type,
            attachments = attachments,
            tags = tags,
            hook_url = hook_url,
            **extra
        )
        return self._post(self.base_url + '/v1/requests/' + req_type, task) 

    def request_multiple_choice(self, choices, choices_type='text', min_answers=None, max_answers=None, **kwargs):
        return self.request('multiple-choice', 
            choices=choices,
            choices_type=choices_type,
            min_answers=min_answers,
            max_answers=max_answers,
            **kwargs) 

    def request_free_text(self, **kwargs):
        return self.request('free-text', 
            **kwargs) 

    def request_annotations(self, annotations_type=ANNOTATION_TYPES.point, min_annotations=None, max_annotations=None, **kwargs):
        if annotations_type not in ANNOTATION_TYPES:
            raise ValueError("annotations_type must be one of {}".format(ANNOTATION_TYPES.keys()))
        return self.request('annotations',
            annotations_type=annotations_type,
            min_annotations=min_annotations,
            max_annotations=max_annotations,
            **kwargs) 
    
    def request_rating(self, rating_min=None, rating_max=None, rating_step=None, label_min=None, label_max=None, **kwargs):
        return self.request('rating',
            rating_min=rating_min,
            rating_max=rating_max,
            rating_step=rating_step,
            label_min=label_min,
            label_max=label_max,
            **kwargs)

