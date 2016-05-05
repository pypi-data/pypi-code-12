import logging
import os
from six.moves import configparser

import yaml
from .utils import deprecated
from .rest import RESTClientObject

logger = logging.getLogger(__package__)

__all__ = ('Client', 'get_client', 'set_client')

_global_client = None


def Client(username=None, password=None, token=None, endpoint=None, config_path=None):
    """Return global `RESTClientObject` with optional configuration.
    Missing configuration will be read from env or config file.

    Parameters
    ----------
    token : str, optional
        API token
    endpoint : str, optional
        Base url of API
    config_path : str, optional
        Alternate location of config file
    """
    global _global_client
    no_username_password = ('Username and password authentication is no longer'
                            ' supported - please use an API token')
    if username or password:
        raise ValueError(no_username_password)
    if config_path:
        if not _file_exists(config_path):
            raise ValueError('Invalid config path - no file at {}'.format(config_path))
    if not token:
        if config_path:
            username, password, token = _get_credentials_from_file(config_path)
        else:
            username, password, token = get_credentials_from_out()
        if not (username and password) and not token:
            raise ValueError('Credentials were improperly configured - could not find token')
    if not endpoint:
        if config_path:
            endpoint = _get_endpoint_from_file(config_path)
        else:
            endpoint = _get_endpoint()
    if username and password:
        raise ValueError(no_username_password)
    else:
        _global_client = RESTClientObject(auth=token, endpoint=endpoint)
    return _global_client


def get_client():
    return _global_client or Client()


class staticproperty(property):
    def __get__(self, instance, owner):
        return self.fget()


def set_client(client):
    """
    Set the global HTTP client for sdk.
    Returns previous client.
    """
    global _global_client
    previous = _global_client
    _global_client = client
    return previous


def get_credentials_from_out():
    username, password, token = [None] * 3
    if 'DATAROBOT_USERNAME' in os.environ:
        username = os.environ.get('DATAROBOT_USERNAME')
        password = os.environ.get('DATAROBOT_PASSWORD')
    elif 'DATAROBOT_API_TOKEN' in os.environ:
        token = os.environ.get('DATAROBOT_API_TOKEN')
    elif _get_config_file():
        config_file = _get_config_file()
        username, password, token = _get_credentials_from_file(config_file)
    return username, password, token


def _get_credentials_from_yaml(config_path):
    with open(config_path, "r") as config_file:
        config = yaml.safe_load(config_file)
    username = config.get("username")
    password = config.get("password")
    token = config.get("token")
    return username, password, token


def _get_credentials_from_ini(config_path):
    cfg_parser = configparser.RawConfigParser()
    cfg_parser.read(config_path)
    username, password, token = None, None, None
    if cfg_parser.has_option('datarobot', 'username'):
        username = cfg_parser.get('datarobot', 'username')
    if cfg_parser.has_option('datarobot', 'password'):
        password = cfg_parser.get('datarobot', 'password')
    if cfg_parser.has_option('datarobot', 'token'):
        token = cfg_parser.get('datarobot', 'token')
    return username, password, token


def path_is_yaml(path):
    _, file_extension = os.path.splitext(path)
    return file_extension == '.yaml'


def _get_credentials_from_file(config_path):
    if path_is_yaml(config_path):
        return _get_credentials_from_yaml(config_path)
    else:
        # put deprecation warning here
        # @deprecated(deprecated_since_version='v2.1', will_remove_version='v2.3',
        #     message='Use a YAML configuration file (default location: '
        #             '~/.config/datarobot/drconfig.yaml) instead.')
        return _get_credentials_from_ini(config_path)


def _get_endpoint_from_yaml(config_path):
    with open(config_path, "r") as config_file:
        config = yaml.safe_load(config_file)
        return config.get('endpoint')


@deprecated(deprecated_since_version='v2.1', will_remove_version='v2.3',
            message='Use a YAML configuration file (default location: '
                    '~/.config/datarobot/drconfig.yaml) instead.')
def _get_endpoint_from_ini(config_path):
    if config_path:
        cfg_parser = configparser.RawConfigParser()
        cfg_parser.read(config_path)
        try:
            return cfg_parser.get('datarobot', 'endpoint')
        except (configparser.NoSectionError,
                configparser.NoOptionError):
            return None
    return None


def _get_endpoint_from_file(config_path):
    if config_path is None:
        return None
    elif path_is_yaml(config_path):
        return _get_endpoint_from_yaml(config_path)
    else:
        return _get_endpoint_from_ini(config_path)


def _get_endpoint():
    endpoint = os.environ.get('DATAROBOT_ENDPOINT')
    if endpoint is not None:
        return endpoint
    endpoint = _get_endpoint_from_file(_get_config_file())
    if endpoint is not None:
        return endpoint
    raise ValueError('Improper Configuration - no endpoint found')


def _get_config_file():
    first_choice_config_path = os.path.expanduser('~/.config/datarobot/drconfig.yaml')
    deprecated_config_path = os.path.join(os.path.expanduser('~'), '.datarobotrc')
    if 'DATAROBOT_CONFIG_FILE' in os.environ:
        config_path = os.environ.get('DATAROBOT_CONFIG_FILE')
        if _file_exists(config_path):
            return config_path
        else:
            raise ValueError('Environment variable DATAROBOT_CONFIG_FILE points to an invalid '
                             'config file')
    elif _file_exists(first_choice_config_path):
        return first_choice_config_path
    elif _file_exists(deprecated_config_path):
        return deprecated_config_path
    else:
        return None


_file_exists = os.path.isfile
