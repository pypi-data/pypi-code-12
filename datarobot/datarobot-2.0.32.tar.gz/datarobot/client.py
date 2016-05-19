import os
import logging

from datarobot.utils import get_creds_from_file, get_config_file
from .rest import RESTClientObject

logger = logging.getLogger(__package__)

__all__ = ('Client', 'get_client', 'set_client')

_global_client = None


def Client(username=None, password=None, token=None, endpoint=None):
    global _global_client
    if not (username and password) and not token:
        username, password, token = get_credentials_from_out()
        if not (username and password) and not token:
            raise ValueError('Credentials were improperly configured')
    if username and password:
        _global_client = RESTClientObject(auth=(username, password),
                                          endpoint=endpoint)
    else:
        _global_client = RESTClientObject(auth=token, endpoint=endpoint)
    return _global_client


def get_client():
    global _global_client
    if not _global_client:
        return Client()
    return _global_client


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
    elif get_config_file():
        config_file = get_config_file()
        username, password, token = get_creds_from_file(config_file)
    return username, password, token
