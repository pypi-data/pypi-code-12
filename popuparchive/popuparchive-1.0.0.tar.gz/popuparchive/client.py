"""
Pop Up Archive API Client
Copyright 2015 Pop Up Archive
"""

import requests
import logging
from base64 import b64encode
import pprint
import os
import json

class Client(object):

    version = '1.0.0'

    def __init__(self, oauth_key, oauth_secret, oauth_host='https://www.popuparchive.com'):
        if not oauth_key:
            raise "OAuth key required"
        if not oauth_secret:
            raise "OAuth secret required"
        
        self.key = oauth_key
        self.secret = oauth_secret
        self.host = oauth_host

        # turn on debugging via PUA_DEBUG env var
        if os.environ.get('PUA_DEBUG'):
            # These two lines enable debugging at httplib level (requests->urllib3->http.client)
            # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
            # The only thing missing will be the response.body which is not logged.
            try:
                import http.client as http_client
            except ImportError:
                # Python 2
                import httplib as http_client
            http_client.HTTPConnection.debuglevel = 1

            # You must initialize logging, otherwise you'll not see debug output.
            logging.basicConfig() 
            logging.getLogger().setLevel(logging.DEBUG)
            requests_log = logging.getLogger("requests.packages.urllib3")
            requests_log.setLevel(logging.DEBUG)
            requests_log.propagate = True

        # get oauth token
        params = {'grant_type':'client_credentials'}
        unencoded_sig = "{}:{}".format(self.key, self.secret)
        signature = b64encode(unencoded_sig)
        headers = {'Authorization': "Basic {}".format(signature),
                   'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(self.host+'/oauth/token', params=params, headers=headers)
        result = response.json()
        #pprint.pprint(result)
        self.access_token = result.get('access_token', None)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def get(self, path, params={}):
        headers = {'Authorization': "Bearer " + self.access_token}
        resp = requests.get(self.host+'/api'+path, params=params, headers=headers)
        return resp.json()

    def post(self, path, payload):
        headers = {'Authorization': "Bearer " + self.access_token}
        #pprint.pprint(payload)
        resp = requests.post(self.host+'/api'+path, json=payload, headers=headers)
        return resp.json()

    def search(self, params):
        #pprint.pprint(params)
        return self.get('/search/', params)

    def get_collections(self):
        return self.get('/collections')['collections']

    def get_collection(self, coll_id):
        return self.get('/collections/'+str(coll_id))

    def get_item(self, coll_id, item_id):
        return self.get('/collections/'+str(coll_id)+'/items/'+str(item_id))

    def create_item(self, coll_id, payload):
        return self.post('/collections/'+str(coll_id)+'/items', payload)

    def create_audio_file(self, item_id, payload):
        return self.post('/items/'+str(item_id)+'/audio_files', { 'audio_file': payload } )


