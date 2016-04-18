import os

from .compat import json
from .endpoint import ApiEndpoint
from .objects import (
  ApiObject,
  Client,
  Experiment,
  Observation,
  Pagination,
  Plan,
  Suggestion,
)
from .requestor import Requestor, DEFAULT_API_URL
from .resource import ApiResource
from .version import VERSION

class Connection(object):
  def __init__(self, client_token=None):
    self.api_url = DEFAULT_API_URL
    client_token = client_token or os.environ.get('SIGOPT_API_TOKEN')

    if not client_token:
      raise ValueError('Must provide client_token or set environment variable SIGOPT_API_TOKEN')

    self.client_token = client_token
    default_headers = {
      'Content-Type': 'application/json',
      'User-Agent': 'sigopt-python/{0}'.format(VERSION),
    }
    self.requestor = Requestor(self.client_token, '', default_headers)

    suggestions = ApiResource(
      self,
      'suggestions',
      endpoints=[
        ApiEndpoint(None, Suggestion, 'POST', 'create'),
        ApiEndpoint(None, object_or_paginated_objects(Suggestion), 'GET', 'fetch'),
        ApiEndpoint(None, Suggestion, 'PUT', 'update'),
        ApiEndpoint(None, Suggestion, 'DELETE', 'delete'),
      ]
    )

    observations = ApiResource(
      self,
      'observations',
      endpoints=[
        ApiEndpoint(None, Observation, 'POST', 'create'),
        ApiEndpoint(None, object_or_paginated_objects(Observation), 'GET', 'fetch'),
        ApiEndpoint(None, Observation, 'PUT', 'update'),
        ApiEndpoint(None, Observation, 'DELETE', 'delete'),
      ]
    )

    plan = ApiResource(
      self,
      'plan',
      endpoints=[
        ApiEndpoint(None, Plan, 'GET', 'fetch'),
      ],
    )

    self._experiments = ApiResource(
      self,
      'experiments',
      endpoints=[
        ApiEndpoint(None, Experiment, 'POST', 'create'),
        ApiEndpoint(None, object_or_paginated_objects(Experiment), 'GET', 'fetch'),
        ApiEndpoint(None, Experiment, 'PUT', 'update'),
        ApiEndpoint(None, Experiment, 'DELETE', 'delete'),
      ],
      resources=[
        suggestions,
        observations,
      ]
    )

    self._clients = ApiResource(
      self,
      'clients',
      endpoints=[
        ApiEndpoint(None, Client, 'GET', 'fetch'),
      ],
      resources=[
        plan,
      ],
    )

  def set_api_url(self, api_url):
    self.api_url = api_url

  @property
  def clients(self):
    return self._clients

  @property
  def experiments(self):
    return self._experiments

  def _get(self, url, params=None):
    request_params = self._request_params(params)
    return self.requestor.get(
      url,
      params=request_params,
    )

  def _post(self, url, params=None):
    request_params = self._to_api_value(params)
    return self.requestor.post(
      url,
      json=request_params,
    )

  def _put(self, url, params=None):
    request_params = self._to_api_value(params)
    return self.requestor.put(
      url,
      json=request_params,
    )

  def _delete(self, url, params=None):
    request_params = self._to_api_value(params)
    return self.requestor.delete(
      url,
      params=request_params,
    )

  def _request_params(self, params):
    req_params = params or {}

    def serialize(value):
      if isinstance(value, dict) or isinstance(value, list):
        return json.dumps(value)
      return str(value)

    return dict((
      (key, serialize(self._to_api_value(value)))
      for key, value
      in req_params.items()
      if value is not None
    ))

  def _to_api_value(self, obj):
    if isinstance(obj, ApiObject):
      return obj.to_json()
    elif isinstance(obj, dict):
      c = {}
      for key in obj:
        c[key] = self._to_api_value(obj[key])
      return c
    elif isinstance(obj, list):
      return [self._to_api_value(c) for c in obj]
    else:
      return obj


# Allows response to be a single object of class some_class or a paginated
# response of objects that come from class some_class
def object_or_paginated_objects(api_object):
  def decorator(body):
    if body.get('object') == 'pagination':
      return Pagination(api_object, body)
    else:
      return api_object(body)

  return decorator
