import json
import requests


class Client(object):
    rootEndpoint = 'http://api.instasent.codes/'
    secureChannel = 'http://api.instasent.codes/'
    useSecureChannel = True

    def __init__(self, token, use_secure_channel=True):
        self.token = token
        self.useSecureChannel = use_secure_channel

    def send_sms(self, sender, to, text, client_id=''):
        if self.useSecureChannel:
            url = self.secureChannel + 'sms/'
        else:
            url = self.rootEndpoint + 'sms/'

        http_method = 'POST'

        data = {'from': sender, 'to': to, 'text': text}

        return self.execute_request(url, http_method, data)

    def get_sms_by_id(self, id):
        if self.useSecureChannel:
            url = self.secureChannel + 'sms/' + id
        else:
            url = self.rootEndpoint + 'sms/' + id

        http_method = 'GET'

        return self.execute_request(url, http_method)

    def get_sms(self, page=1, per_page=10):
        if self.useSecureChannel:
            url = self.secureChannel + 'sms/?page=' + page + 'per_page=' + per_page
        else:
            url = self.rootEndpoint + 'sms/?page=' + page + 'per_page=' + per_page

        http_method = 'GET'

        return self.execute_request(url, http_method)

    def execute_request(self, url='', http_method='', data=''):
        headers = {'Authorization': 'Bearer ' + self.token}

        if http_method == 'GET':
            response = requests.get(url, headers=headers)
        elif http_method == 'POST':
            response = requests.post(url, data=json.dumps(data), headers=headers)

        return response.json()
