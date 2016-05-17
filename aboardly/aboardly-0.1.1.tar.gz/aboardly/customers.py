import requests

class Customers(object):

    def __init__(self, auth, base_url):
        self.auth = auth
        self.base_url = base_url

    def upsert(self, customer_id, data={}):
        url = self.base_url + "/customers/" + customer_id
        return requests.put(url, data=data, auth=self.auth)
