"""
Audiosear.ch Client
Copyright 2015 Pop Up Archive
"""

import requests
from base64 import b64encode
import pprint
import re

class Client(object):

    version = '1.0.2'

    def __init__(self, oauth_key, oauth_secret, oauth_host='https://www.audiosear.ch'):
        if not oauth_key:
            raise Exception( "OAuth key required" )
        if not oauth_secret:
            raise Exception( "OAuth secret required" )
        
        self.key = oauth_key
        self.secret = oauth_secret
        self.host = oauth_host

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
        if not self.access_token:
            raise Exception("Failed to get Authentication token: " + pprint.pformat( result ))

    def __str__(self):
        return unicode(self).encode('utf-8')

    def get(self, path, params={}):
        headers = {'Authorization': "Bearer " + self.access_token}
        url = path
        abs_url = re.compile('^https?:')
        if not abs_url.match(url):
            url = self.host+'/api'+path

        resp = requests.get(url, params=params, headers=headers)
        return resp.json()

    def search(self, params, type='episodes'):
        #pprint.pprint(params)
        return self.get('/search/'+type, params)

    def get_show(self, show_id):
        return self.get('/shows/'+str(show_id))

    def get_episode(self, ep_id):
        return self.get('/episodes/'+str(ep_id))

    def get_trending(self):
        return self.get('/trending/')
    
    def get_related(self, id, params={}):
        type = params['type'] if ('type' in params) else 'episodes'
        return self.get('/'+type+'/'+str(id)+'/related/', params)
    
    def get_tastemakers(self, num_results=5):
        return self.get('/tastemakers/episodes/'+str(num_results))

    def get_person(p_id):
        return self.get('/people/'+str(p_id))

