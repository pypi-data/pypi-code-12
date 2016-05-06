import json
import logging
import requests
from requests.exceptions import RetryError
from requests.packages.urllib3.util.retry import Retry
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.adapters import HTTPAdapter
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

DEFAULT_ENDPOINT = '10.225.221.210'
DEFAULT_URI_BASE = 'mgmt/tm'

log = logging.getLogger(__name__)


class BaseF5Client(object):

    def __init__(self, username, password, retries=3, endpoint=DEFAULT_ENDPOINT, uri_base=DEFAULT_URI_BASE):
        self._endpoint = 'https://' + endpoint
        self._uri_base = uri_base
        self.session = requests.Session()
        retry = Retry(
            total=retries,
            status_forcelist=[500],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount(self._endpoint, adapter)
        self._username = username
        self._password = password

    def _build_url(self, path):
        return '/'.join([self._endpoint, self._uri_base] + path)

    def _get_auth(self):
        return (self._username, self._password)

    def _call(self, method, url, parameters=None, payload=None):
        headers = {'Content-Type': 'application/json'}
        if payload is not None:
            json_payload = json.dumps(payload)
        else:
            json_payload = None

        #  if method = 'get', it would be calling self.session.get()
        call = getattr(self.session, method)
        try:
            response = call(url,
                            data=json_payload,
                            params=parameters,
                            verify=False,
                            headers=headers,
                            auth=self._get_auth())
        except RetryError as retry_error:
            log.exception(retry_error)
            raise retry_error

        log.debug("Status code {}, Response - {}".format(response.status_code, response.text))
        if not response.ok:
            log.error("Status code {}, Response - {}".format(response.status_code, response.text))
            response.raise_for_status()
        else:
            return response.json()

    def _get(self, url, params=None):
        return self._call('get', url, parameters=params)

    def _post(self, url, payload):
        return self._call('post', url, payload=payload)

    def _put(self, url, payload):
        return self._call('put', url, payload=payload)

    def _set_gtm_wideip(self, name, partition, payload):
        partition_and_name = "~{0}~{1}".format(partition, name)
        path = ['gtm', 'wideip', partition_and_name]
        url = self._build_url(path)
        result = self._put(url, payload)
        return isinstance(result, dict)

    def _get_gtm_wideip(self, name, partition):
        partition_and_name = "~{0}~{1}".format(partition, name)
        path = ['gtm', 'wideip', partition_and_name]
        url = self._build_url(path)
        return self._get(url)

    def _set_self_ip(self, payload):
        path = ['net', 'self']
        url = self._build_url(path)
        result = self._post(url, payload)
        return isinstance(result, dict)

    def _set_vlan(self, payload):
        path = ['net', 'vlan']
        url = self._build_url(path)
        result = self._post(url, payload)
        return isinstance(result, dict)

    def _get_net_self(self):
        path = ['net', 'self']
        url = self._build_url(path)
        return self._get(url)
