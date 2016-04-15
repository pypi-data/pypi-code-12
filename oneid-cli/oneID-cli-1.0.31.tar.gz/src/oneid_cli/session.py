import requests
import base64
import logging

from oneid import keychain, service, utils

from . import config_file

logger = logging.getLogger(__name__)


DEFAULT_API_ENDPOINT = 'https://api.oneid.com'


def _get_api_endpoint():  # pragma: nocover -- this is a tough one to catch in a test. probably means it's a poor design
    try:
        with config_file.load() as config:
            url = config and config.get('URL') or DEFAULT_API_ENDPOINT
            logger.debug('url=%s', url)
    except:
        url = DEFAULT_API_ENDPOINT

    return url

API_ENDPOINT = _get_api_endpoint()

PROJECTS_ENDPOINT = API_ENDPOINT + '/projects'
PROJECT_ENDPOINT = PROJECTS_ENDPOINT + '/{project_id}'
REVOKE_PROJECT_ENDPOINT = PROJECT_ENDPOINT + '/revoke'

SERVERS_ENDPOINT = PROJECT_ENDPOINT + '/servers'
SERVER_ENDPOINT = SERVERS_ENDPOINT + '/{server_id}'
REVOKE_SERVER_ENDPOINT = SERVER_ENDPOINT + '/revoke'

EDGE_DEVICES_ENDPOINT = PROJECT_ENDPOINT + '/edge_devices'
EDGE_DEVICE_ENDPOINT = EDGE_DEVICES_ENDPOINT + '/{edge_device_id}'
REVOKE_EDGE_DEVICE_ENDPOINT = EDGE_DEVICE_ENDPOINT + '/revoke'


class HTTPException(requests.exceptions.RequestException):
    pass


class CLISession(object):
    """
    Manage the active user's configuration and credentials

    :param project_name: Optional project name for settings
        specific to a project
    """
    def __init__(self, project_id=None):
        self._project_id = project_id
        self._encryption_key = None
        self._keypair = None
        self._return_keypair = None

    @property
    def project(self):
        return self._project_id

    @project.setter
    def project(self, value):
        self._project_id = value

    @property
    def keypair(self):
        return self._keypair or self.get_keypair()

    @property
    def return_keypair(self):
        if self._return_keypair is None:
            self._load_project_admin_settings()

        return self._return_keypair

    @property
    def encryption_key(self):
        if self._encryption_key is None and self._project_id:
            self._load_project_settings()

        return self._encryption_key

    def _load_project_settings(self):
        """
        Given a project id, load settings
        :return:
        """
        with config_file.load(self.project) as project_credentials:
            if project_credentials is None:
                raise ValueError('Could not find any valid credentials for %s project' % self.project)

            self._encryption_key = 'AES' in project_credentials and base64.b64decode(project_credentials['AES'])

    def _load_project_admin_settings(self):
        """
        Load ProjectAdmin settings
        :return:
        """
        with config_file.load() as credentials:
            project_admin_credentials = credentials and credentials.get('PROJECT_ADMIN')
            logger.debug('project_admin_credentials=%s', project_admin_credentials)
            if not project_admin_credentials:
                raise ValueError('Could not find any valid credentials, please run oneid-cli configure')

            if 'SECRET' not in project_admin_credentials:
                raise ValueError('Missing SECRET in credentials, please re-run oneid-cli configure')

            der = base64.b64decode(project_admin_credentials['SECRET'])
            self._keypair = keychain.Keypair.from_secret_der(der)
            self._keypair.identity = project_admin_credentials.get('ID')

            if 'RETURN_KEY' in project_admin_credentials:
                der = base64.b64decode(project_admin_credentials['RETURN_KEY'])
                self._return_keypair = keychain.Keypair.from_public_der(der)

    def get_keypair(self):
        """
        Get the oneID Keypair associated with the current user

        :return: oneid.keychain.Keypair
        """
        if self._keypair is None:
            self._load_project_admin_settings()

        return self._keypair

    def make_api_call(self, endpoint, http_method, **kwargs):
        """
        Make an API HTTP request to oneID

        :param endpoint: URL (all http methods are POST)
        :param kwargs: HTTP method is json, kwargs will be converted to json body
        :return: Response of request
        :raises TypeError: If the kwargs are None, json dumps will fail
        """
        nonce = kwargs.get('jti', utils.make_nonce())
        auth_header_jwt = service.make_jwt({'jti': nonce,
                                            'iss': self.keypair.identity},
                                           self.keypair)

        headers = {
            'Content-Type': 'application/jwt',
            'Authorization': 'Bearer %s' % auth_header_jwt
        }
        data = None

        if http_method in ['POST', 'PUT', 'PATCH']:
            data = service.make_jwt(kwargs, self.keypair)

        try:
            response = requests.request(http_method, endpoint, headers=headers, data=data)
            if response.headers.get('Content-Type') == 'application/jwt; charset=utf-8':
                message = service.verify_jwt(response.text, self.return_keypair)
                if message and message.get('jti') != nonce:
                    logger.warning('Invalid nonce returned with response')
                    raise HTTPException
                elif nonce and not (message and 'jit' not in message):
                    logger.warning('Expected nonce not returned with response')
                    raise HTTPException
                return message
            else:
                return response.json()
        except:
            logger.debug('Error making API request:', exc_info=True)
            raise HTTPException
