'''A simple implementation for BatchCompute service SDK.
'''
__version__ = '2.0.6a12'
__all__ = [
    "Client", "ClientError", "FieldError", "ValidationError", "JsonError",
    "ConfigError", "CN_QINGDAO", "CN_HANGZHOU"
]
__author__ = 'crisish <helei.hl@alibaba-inc.com>'

from .client import Client
from .core import ClientError, FieldError, ValidationError, JsonError
from .utils import CN_QINGDAO, CN_HANGZHOU, ConfigError
