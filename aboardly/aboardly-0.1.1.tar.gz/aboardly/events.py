import requests

class Events(object):

    def __init__(self, auth, base_url):
        self.auth = auth
        self.base_url = base_url

    def create(self, customer_id, event_name, properties={}):
        url = self.base_url + "/customers/" + customer_id + "/events/" + event_name
        return requests.post(url, auth=self.auth, json=properties)
