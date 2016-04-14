from __future__ import unicode_literals
import datetime
try:
  from urlparse import urljoin
except ImportError:
  # python 3:
  from urllib.parse import urljoin

import pyrfc3339
import requests
import six

from handwritingio.version import __version__


def _decode_timestamps(obj):
  """Checks `obj` to see if it looks like a timestamp string, and if so
  decode it into a datetime.datetime object
  """
  for k, v in six.iteritems(obj):
    if isinstance(v, dict):
      # recurse
      obj[k] = _decode_timestamps(v)
    else:
      if isinstance(v, six.string_types) and v.endswith('Z'):
        try:
          obj[k] = pyrfc3339.parse(v, produce_naive=True)
        except ValueError:
          continue
  return obj


class APIError(requests.HTTPError):
  """Base class for errors from the API."""
  def __init__(self, *args, **kwargs):
    super(APIError, self).__init__(*args, **kwargs)
    try:
      json = self.response.json()
    except ValueError:
      self.errors = None
    else:
      self.errors = json.get('errors', [])

class ValidationError(APIError):
  """Indicates a problem with the request parameters."""

class AuthorizationError(APIError):
  """Indicates a problem with the token used for authorization."""

class RateLimitError(APIError):
  """Raised when the API rate limit is exceeded."""


def _message_from_response(response):
  try:
    json = response.json()
  except ValueError:
    return None
  errors = json.get('errors')
  if not errors:
    return None

  # Note: the message will only show the first error.
  msg = errors[0].get('error')
  missing_chars = errors[0].get('missing_characters')
  if missing_chars:
    chars = [c['character'] for c in missing_chars]
    return '%s: %s' % (msg, chars)

  field = errors[0].get('field')
  if field:
    return 'field: %s, %s' % (field, msg)
  return msg


class Client(object):
  """Client object for interacting with the Handwriting.io API.
  """

  def __init__(self, key, secret, base_url='https://api.handwriting.io/'):
    self.session = requests.Session()
    self.session.auth = (key, secret)
    self.base_url = base_url

  def _hit(self, method, url, **kwargs):
    """Send a request to the API. kwargs will be passed to
    `requests.Session.request`. Checks the response for errors, raising an
    exception if any are encountered. If the response is JSON, it will be
    parsed, including timestamps into datetime objects, and returned. If the
    response is an image, the binary content will be returned.
    """
    request_kwargs = {
      'timeout': 10, # Default timeout in seconds
      'headers': {
        'User-Agent': 'handwritingio-python-client/%s' % __version__,
      }
    }
    request_kwargs.update(kwargs)
    url = urljoin(self.base_url, url)
    r = self.session.request(method, url, **request_kwargs)
    if 200 <= r.status_code < 300:
      if r.headers.get('content-type', '').startswith('application/json'):
        return r.json(object_hook=_decode_timestamps)
      else:
        return r.content

    message = _message_from_response(r)
    if r.status_code == 400:
      raise ValidationError(message, response=r)
    elif r.status_code == 401:
      raise AuthorizationError(message, response=r)
    elif r.status_code == 429:
      raise RateLimitError(message, response=r)
    raise APIError(message, response=r)

  def __enter__(self):
    return self

  def __exit__(self, *args):
    self.close()

  def close(self):
    self.session.close()

  def list_handwritings(self, params=None, **kwargs):
    """Gets a list of handwritings. Returns a `list` parsed from the JSON
    response.
    """
    return self._hit("GET", "/handwritings", params=params, **kwargs)

  def get_handwriting(self, handwriting_id, **kwargs):
    """Gets a single handwriting by id. Returns a `dict` parsed from the JSON
    response.
    """
    return self._hit("GET", "/handwritings/%s" % handwriting_id, **kwargs)

  def render_png(self, params, **kwargs):
    """Get a handwritten PNG image. Returns the image file bytes.
    """
    return self._hit("GET", "/render/png", params=params, **kwargs)

  def render_pdf(self, params, **kwargs):
    """Get a handwritten PDF image. Returns the PDF file bytes.
    """
    return self._hit("GET", "/render/pdf", params=params, **kwargs)
