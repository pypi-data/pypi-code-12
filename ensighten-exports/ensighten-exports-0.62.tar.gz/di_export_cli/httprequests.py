import requests
from requests.auth import HTTPBasicAuth
import urllib3.contrib.pyopenssl
from requests.packages.urllib3.util import Retry
from requests.adapters import HTTPAdapter

urllib3.contrib.pyopenssl.inject_into_urllib3()


class HttpRequest:

    def __init__(self, api_url):
        self.url = api_url

    def get_auth_token(self, username, password):
        s = requests.Session()
        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))
        resp = s.get(self.url + '/api/latest/auth', auth=HTTPBasicAuth(username, password))
        resp.raise_for_status()
        return resp
