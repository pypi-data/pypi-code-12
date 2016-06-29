import requests


class RequestsUtil:

    def __init__(self, max_retries=10, header=None):
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=max_retries)
        self.session.mount('https://', adapter)
        self.header = header

    def get(self, url, timeout=60):
        return self.session.get(url, headers=self.header, timeout=timeout)
