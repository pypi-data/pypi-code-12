import requests
from requests.auth import HTTPBasicAuth

from .customers import Customers
from .events import Events

BASE_URL = 'https://www.aboardly.com/api/v1'

class Aboardly(object):

    def __init__(self, username, password, base_url=BASE_URL):
        auth = HTTPBasicAuth(username, password)
        self.customers = Customers(auth, base_url)
        self.events = Events(auth, base_url)
