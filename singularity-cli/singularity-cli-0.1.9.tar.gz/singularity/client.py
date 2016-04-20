import json
import requests

def _response(res):
    try:
        return res.json()
    except:
        return {'error': res.text, 'status_code': res.status_code}

class Client(object):

    def __init__(self, host, insecure=False):
        self.host = host
        self.session = requests.Session()
        self.session.headers = {'Content-Type': 'application/json'}
        if insecure:
            requests.packages.urllib3.disable_warnings()
            self.session.verify = False

    # state api
    def get_state(self):
        url = '{0}/api/state'.format(self.host)
        return _response(self.session.get(url))

    def get_state_underprovisioned(self):
        url = '{0}/api/state/requests/under-provisioned'.format(self.host)
        return _response(self.session.get(url))

    def get_state_overprovisioned(self):
        url = '{0}/api/state/requests/over-provisioned'.format(self.host)
        return _response(self.session.get(url))

    # requests api
    def unpause_request(self, request_id, message=""):
        data = {'message': message}
        url = '{0}/api/requests/request/{1}/unpause'.format(self.host, request_id)
        return _response(self.session.post(url, data=json.dumps(data)))

    def run_request(self, request_id):
        url = '{0}/api/requests/request/{1}/run'.format(self.host, request_id)
        return _response(self.session.post(url))

    def pause_request(self, request_id, kill_tasks=False):
        data = {'killTasks': kill_tasks}
        url = '{0}/api/requests/request/{1}/pause'.format(self.host, request_id)
        return _response(self.session.post(url, data=json.dumps(data)))

    def scale_request(self, request_id, instances):
        data = {'id': request_id, 'instances': instances}
        url = '{0}/api/requests/request/{1}/scale'.format(self.host, request_id)
        return _response(self.session.put(url, data=json.dumps(data)))

    def bounce_request(self, request_id):
        url = '{0}/api/requests/request/{1}/bounce'.format(self.host, request_id)
        return _response(self.session.post(url))

    def get_request(self, request_id):
        url = '{0}/api/requests/request/{1}'.format(self.host, request_id)
        return _response(self.session.get(url))

    def delete_request(self, request_id, message="", actionId=""):
        data = {'message': message, 'actionId': actionId}
        url = '{0}/api/requests/request/{1}'.format(self.host, request_id)
        return _response(self.session.delete(url, data=json.dumps(data)))

    def upsert_request(self, request):
        url = '{0}/api/requests'.format(self.host)
        return _response(self.session.post(url, data=json.dumps(request)))

    def get_requests(self, type):
        if type == 'all':
            url = '{0}/api/requests'.format(self.host)
        elif type in ['pending', 'cleanup']:
            url = '{0}/api/requests/queued/{1}'.format(self.host, type)
        else:
            url = '{0}/api/requests/{1}'.format(self.host, type)
        return _response(self.session.get(url))

    # deploys api
    def create_deploy(self, deploy, unpauseOnSuccessfulDeploy=False):
        data = {'deploy': deploy, 'unpauseOnSuccessfulDeploy': unpauseOnSuccessfulDeploy}
        url = '{0}/api/deploys'.format(self.host)
        return _response(self.session.post(url, data=json.dumps(data)))

    # tasks api
    def get_tasks(self, type, slave_id):
        url = '{0}/api/tasks/{1}'.format(self.host, type)
        if type == 'active' and slave_id:
            url = '{0}/slave/{1}'.format(url, slave_id)
        return _response(self.session.get(url))

    def get_active_deploy_tasks(self, request_id, deploy_id):
        url = '{0}/api/history/request/{1}/deploy/{2}/tasks/active'.format(self.host, request_id, deploy_id)
        return _response(self.session.get(url))

