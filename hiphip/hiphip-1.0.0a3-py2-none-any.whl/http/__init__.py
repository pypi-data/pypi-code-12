import requests
from .client import Client
from .response import Response

requests.Response.__repr__ = Response.__repr__
codes = requests.codes
