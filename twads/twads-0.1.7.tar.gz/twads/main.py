import requests
from requests_oauthlib import OAuth1


class Client:
    def __init__(self, consumer_key, consumer_secret, access_key, access_secret):
        self.auth = OAuth1(
            client_key=consumer_key, client_secret=consumer_secret,
            resource_owner_key=access_key, resource_owner_secret=access_secret
        )

    def get_accounts(self):
        url = 'https://ads-api.twitter.com/0/accounts'
        response = requests.get(url, auth=self.auth)
        try:
            return response.json()['data']
        except KeyError:
            return response.json()['errors']
