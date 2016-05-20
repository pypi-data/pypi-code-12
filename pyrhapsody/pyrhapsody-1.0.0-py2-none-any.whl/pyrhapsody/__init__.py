# -*- coding: utf-8 -*-

import json
import requests
from urllib import urlencode


"""
Rhapsody Python Client

Resources:
https://developer.rhapsody.com/api

TODO:
    * Error handling
    * Tokens refreshing
"""


class RhapsodyClient(object):
    def __init__(self, application_key, secret_key, base_url, base_auth_url, redirect_uri):
        # required at init
        self.application_key = application_key
        self.secret_key = secret_key
        self.base_url = base_url
        self.base_auth_url = base_auth_url
        self.redirect_uri = redirect_uri

        # not required
        self.access_token = None
        self.headers = {}

    def _request_method(self, method):
        return {
            'GET': requests.get,
            'POST': requests.post,
            'PUT': requests.put,
        }.get(method)

    def _make_request(self, method, base_url, endpoint, params={}, payload={}):
        """TODO: Token must be passed as a Header of type "Bearer" (wat?) field"""
        if base_url == self.base_url:
            bearer_string = "Bearer %s" % self.access_token
            self.headers = {"Accept-Version": "2.0.0"}
            self.headers["Authorization"] = bearer_string
            self.headers["Content-Type"] = "application/json"
        else:
            self.headers = {}
        url = base_url + "%s" % endpoint
        request_method = self._request_method(method)
        result = request_method(url, params=params, headers=self.headers, data=json.dumps(payload))
        result.raise_for_status()
        try:
            return result.json()
        except:
            return result

    """Auth flow
       https://developer.rhapsody.com/api#authentication
    """
    def get_authorize_url(self, state=None):
        params = {}
        params['client_id'] = self.application_key
        params['redirect_uri'] = self.redirect_uri
        params['response_type'] = 'code'
        endpoint = '/authorize'
        return self.base_auth_url + "%s?%s" % (endpoint, urlencode(params))

    def get_access_token(self, code):
        params = {}
        params['client_id'] = self.application_key
        params['client_secret'] = self.secret_key
        params['redirect_uri'] = self.redirect_uri
        params['response_type'] = 'code'
        params['grant_type'] = 'authorization_code'
        params['code'] = code
        return self._make_request(
            method='POST',
            base_url=self.base_auth_url,
            endpoint='/access_token',
            params=params,
        )

    def refresh_access_token(self, refresh_token):
        params = {}
        params['client_id'] = self.application_key
        params['client_secret'] = self.secret_key
        params['refresh_token'] = refresh_token
        params['response_type'] = 'code'
        params['grant_type'] = 'refresh_token'
        return self._make_request(
            method='POST',
            base_url=self.base_auth_url,
            endpoint='/access_token',
            params=params
        )


    # """api endpoints"""

    def me(self):
        return self._make_request(
            method='GET',
            base_url=self.base_url,
            endpoint='/me',
        )

    def search(self, query, limit=None, search_type='track'):
        """TODO: doc
        /search?limit=1&q=say+it+aint+so&type=track
        """
        if not query:
            return
        params = {'q':query}
        if limit:
            params['limit'] = limit
        if search_type:
            params['type'] = search_type
        return self._make_request(
            method='GET',
            base_url=self.base_url,
            endpoint='/search',
            params=params,
        ).get('data')

    def playlist_create(self, name, tracks=None, public=True):
        """Returns created (ts), id (str), modified (ts), name (str)

        Request parameters
        `privacy`: 'public' or 'private'
        `tracks`: array of {"id": "tra.id"} dicts
        """
        if not name:
            return
        payload = {"playlists": {"name": name}}
        if public:
            payload["playlists"]["privacy"] = "public"
        if tracks:
            json_tracks = []
            for track in tracks:
                json_tracks += {"id": track}
            payload["playlists"]["tracks"] = json_tracks
        return self._make_request(
            method='POST',
            base_url=self.base_url,
            endpoint='/me/library/playlists',
            payload=payload,
        )

    def playlist_info(self, playlist_id):
        """curl -v -H "Authorization: Bearer {access_token}" "https://api.rhapsody.com/v1/me/playlists/mp.152031586"
        """
        endpoint = '/me/library/playlists/%s' % playlist_id
        return self._make_request(
            method='GET',
            base_url=self.base_url,
            endpoint=endpoint,
        )

    def playlist_replace_songs(self, playlist_id, track_ids):
        """curl -v -X POST -H "Authorization: Bearer {access_token}" -d "id=tra.5156528" "https://api.rhapsody.com/v1/me/playlists/mp.152031586/tracks"
        """
        if not track_ids:
            return
        track_ids = [{"id": track_id} for track_id in track_ids]
        payload = {"tracks": track_ids}
        endpoint = '/me/library/playlists/%s/tracks' % playlist_id
        return self._make_request(
            method='PUT',
            base_url=self.base_url,
            endpoint=endpoint,
            payload=payload,
        )
