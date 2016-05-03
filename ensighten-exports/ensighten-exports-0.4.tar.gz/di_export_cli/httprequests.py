import urllib3
import certifi
from requests.packages.urllib3.util import Retry
from httpexecutor import HttpExecutor

class HttpRequest:

    def __init__(self, api_url):
        self.url = api_url
        self.http = urllib3.PoolManager(
                cert_reqs='CERT_REQUIRED', # Force certificate check.
                ca_certs=certifi.where()  # Path to the Certifi bundle.
                )

    def get_auth_token(self, username, password):
        headers = urllib3.util.make_headers(basic_auth=username + ':' + password)
        retries = Retry(3, status_forcelist=[500, 503])
        return HttpExecutor().execute_with_retry(self.http.request, 'GET', self.url + '/api/latest/auth', headers=headers)
