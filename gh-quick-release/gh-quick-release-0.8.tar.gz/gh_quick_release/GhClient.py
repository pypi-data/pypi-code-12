import requests
import simplejson as json
from .Errors import CliError


class GhClient:
    _gh_url = 'https://api.github.com/'

    def __init__(self, user, pw):
        self.user = user
        self.pw = pw

    def _return(self, res):
        try:
            res.raise_for_status()
        except Exception, e:
            raise CliError('Github response: ' + res.json()['message'])

        return res.json()

    def get(self, path):
        res = requests.get(self._gh_url, auth=(self.user, self.pw))
        return self._return(res)

    def post(self, path, payload):
        encoded = json.dumps(payload)
        res = requests.post(
                self._gh_url + path,
                auth=(self.user, self.pw),
                data=encoded)
        return self._return(res)
