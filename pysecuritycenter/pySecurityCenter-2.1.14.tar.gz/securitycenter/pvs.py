from .base import BaseAPI, APIError, logging


class PVS(BaseAPI):
    def __init__(self, host, port=8835, ssl_verify=False, scheme='https', log=False):
        BaseAPI.__init__(self, host, port, ssl_verify, scheme, log)

    def _builder(self, **kwargs):
        kwargs = BaseAPI._builder(self, **kwargs)
        kwargs['headers'] = None
        #kwargs['headers']['Accept'] = 'application/json, text/javascript, */*; q=0.01'
        #kwargs['headers']['Content-Type'] = 'application/x-www-form-urlencoded'
        return kwargs

    def login(self, username, password):
        resp = self.post('login', data={
                'username': username,
                'password': password,
                'json': 1,
                #'nocookie': 1,
        })
        if resp.status_code == 200:
            self._token = resp.json()['reply']['contents']['token']
        else:
            try:
                raise APIError(resp.status_code, resp.json())
            except:
                print resp.content
