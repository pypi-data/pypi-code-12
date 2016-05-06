import logging
import requests
import xmltodict
from requests.exceptions import RetryError
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

DEFAULT_ENDPOINT = 'https://172.17.76.199'

log = logging.getLogger(__name__)


class BaseNSXClient(object):
    def __init__(self, username, password, retries=3, endpoint=DEFAULT_ENDPOINT, dryrun=False):
        self._endpoint = endpoint
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
        self._dryrun = dryrun

    def _build_url(self, path):
        base_path = ['api', '2.0']
        return '/'.join([self._endpoint] + base_path + path)

    def _get_auth(self):
        return (self._username, self._password)

    def _call(self, method, url, payload=None, rtype='xml', parameters={}):
        # Get our response using the session
        headers = {}
        log.debug(url)

        if rtype:
            headers = {'Content-Type': "application/{0}".format(rtype)}

        if self._dryrun:
            return "{0} {1}".format(method, url)
        call = getattr(self.session, method)
        try:
            response = call(url,
                            params=parameters,
                            verify=False,
                            headers=headers,
                            auth=self._get_auth(),
                            data=payload)
        except RetryError as e:
            logging.exception(e)
            raise e

        response.raise_for_status()  # this will raise on 4xx and 5xxs
        if rtype == 'xml':
            return xmltodict.parse(response.text)
        return response.text

    def _get(self, url, rtype=None, parameters={}):
        return self._call('get', url, rtype=rtype, parameters=parameters)

    def _put(self, url, payload=None, rtype=None, parameters={}):
        return self._call('put', url, payload=payload, rtype=rtype, parameters=parameters)

    def _get_security_groups(self):
        path = ['services', 'securitygroup', 'scope', 'globalroot-0']
        url = self._build_url(path)
        return self._get(url, rtype='xml')

    def _add_member(self, group, member):
        path = ['services', 'securitygroup', group, 'members', member]
        url = self._build_url(path)
        return self._put(url)
