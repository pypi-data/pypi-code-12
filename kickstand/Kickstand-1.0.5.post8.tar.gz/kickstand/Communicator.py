#!/usr/bin/python
"""Module for communicating with the Kickstand server."""

import requests

class Communicator(object):

  def __init__(self, api_url):
    self.api_url = api_url

    self.default_headers = {}

    self.client_user_agent       = 'Kickstand-Client'
    self.client_version          = '1.0.0'
    self.client_content_language = 'en'
    self.client_content_type     = 'application/json'

    self.default_headers['User-Agent'] = '%s:%s' % (self.client_user_agent, self.client_version)
    self.default_headers['Content-Language'] = self.client_content_language

  def request(self, method, uri, **kwargs):
    headers = self.default_headers
    if( 'headers' in kwargs ):
      headers.update(kwargs['headers'])

    url = '%s/%s' % (self.api_url.rstrip('/'), uri.lstrip('/'))

    # TODO Wrap request to catch errors and rethrow as necessary
    # TODO Wrap request to return data directly with headers
    # TODO Wrap request to analyze returned error codes and throw errors accordingly
    response = requests.request(method, url, **kwargs)

    return response

  def get(self, uri, **kwargs):
    return self.request('GET', uri, **kwargs)

  def put(self, uri, **kwargs):
    return self.request('PUT', uri, **kwargs)

  def post(self, uri, **kwargs):
    return self.request('POST', uri, **kwargs)

  def head(self, uri, **kwargs):
    return self.request('HEAD', uri, **kwargs)

  def patch(self, uri, **kwargs):
    return self.request('PATCH', uri, **kwargs)

  def delete(self, uri, **kwargs):
    return self.request('DELETE', uri, **kwargs)
