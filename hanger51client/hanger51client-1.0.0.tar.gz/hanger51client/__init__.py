import datetime
import json
import requests
import time

__all__ = (
    'Hanger51Client',
    'Hanger51ClientException',
    'Variation'
    )


class Hanger51ClientException(Exception):
    """
    `Hanger51ClientExceptions` are raised when a call to the API results in a
    non-200 OK response code or a non-success status in the response.
    """

    def __init__(self, reason, issues=None):
        self.reason = reason
        self.issues = issues

    @property
    def _issues_str(self):
        # Return a string representing the issues associated with the exception

        # Check there are issues associated with the exception, if not we're
        # done just return an empty string.
        if not self.issues:
            return ''

        # Return a string starting with a separator and listing each issue on a
        # separate line.
        return '\n---\n' + '\n'.join(
            ['{k}: {v}'.format(k=k, v=v) for k, v in self.issues.items()]
            )

    def __str__(self):
        return '{e.reason}{e._issues_str}'.format(e=self)


class Hanger51Client:
    """
    Client for calling the Hanger51 API.
    """

    def __init__(self, api_key, api_endpoint='https://hanger51.getme.co.uk/'):
        self.api_key = api_key
        self.api_endpoint = api_endpoint

    def call_api(self, api_method, params=None, files=None, http_method='get'):
        """Call a method against the API"""

        # Build the URL to call
        url = '{endpoint}/{method}'.format(
            endpoint=self.api_endpoint,
            method=api_method
            )

        # Build the params
        if not params:
            params = {}

        # Add the API key to the parameters
        params['api_key'] = self.api_key

        # Call the API
        request_func = getattr(requests, http_method.lower())
        response = request_func(url, params=params, files=files)

        # Raise an exception for status codes other than 200 OK
        if response.status_code != 200:
            raise Hanger51ClientException(
                '{r.url}, returned {r.status_code}'.format(r=response)
                )

        # Check the API response
        status = response.json()['status']
        payload = response.json().get('payload')

        # If the status of th response is not `success` raise an exception that
        # includes issues flagged by the API.
        if status != 'success':
            raise Hanger51ClientException(
                payload['reason'],
                payload.get('issues')
                )

        return payload

    def listing(self, q=None, type=None):
        """List assets for the current account"""
        return self.call_api('', params={'q': q, 'type': type})

    def get(self, uid):
        """Get the details of an asset"""
        return self.call_api('get', params={'uid': uid})

    def upload(self, file, name=None):
        """Upload an asset"""
        return self.call_api(
            'upload',
            params={'name': name},
            files= {'asset': file},
            http_method='post'
            )

    def generate_variations(self, uid, variations):
        """
        Generate one of more image variations for an image asset.

        NOTE: Values in the `variations` dictionary can be specified either as
        dictionaries or `Variation` instances (recommended), e.g:

            variations = {
                'large': Variation().fit(100),
                'small': [['fit', [10, 10]]]
            }

        """

        # Make a shallow copy of the variations so we don't modify it directly
        variations = variations.copy()

        # Convert `Variation` instances in the `variations` dictionary to
        # be lists.
        for name, variation in variations.items():
            if isinstance(variation, Variation):
                variations[name] = variation.ops

            # Check all variations are dictionaries
            if not isinstance(variations[name], list):
                raise TypeError(
                    'Variation `{name}` is not a dictionary.'.format(name=name)
                    )

        # Call the API and request the new variations
        return self.call_api(
            'generate-variations',
            params={'uid': uid, 'variations': json.dumps(variations)},
            http_method='post'
            )

    def set_expires(self, uid, expires=None):
        """
        Set the expiry date for an asset, once an asset expires it will be
        removed (along with any variations in the case of images).

        NOTE: `expires` can be a datetime, date or integer value (where
        the integer is the number of seconds since epoch).
        """

        # Attempt to convert the expiry date to seconds since epoch
        if expires and not isinstance(expires, int):
            try:
                expires = time.mktime(expires.timetuple())
            except AttributeError:
                raise TypeError('`expires` must be datetime, date or int.')

        # Add the expiry date to the parameters if specified
        params = {'uid': uid}
        if expires:
            params['expires'] = expires

        # Call the API and request a new expiry date is set
        return self.call_api(
            'set-expires',
            params=params,
            http_method='post'
            )


class Hanger51ClientMock:
    """
    Mocked version of Hanger51Client for use in test environments.

    Usage:

        from hanger51client import Hanger51ClientMock
        from unittest.mock import patch

        @patch(
            'hanger51client.Hanger51Client.upload',
            Hanger51ClientMock.upload
            )
    """

    def upload(self, file, name=None):
        return {}

    def generate_variations(self, uid, variations={}):
        return {}

    def set_expires(self, uid, expires):
        return {}


class Variation:
    """
    Helper class for building image variations with Hanger51.

    An image variation is simply a named set of image operations that are
    performed to generate a new variation of an image.
    """

    def __init__(self):
        self._ops = []

    def __add__(self, other):
        """
        Allow adding of one variation object to another retuning a new
        Variation.
        """
        variation = Variation()
        variation._ops = self.ops + other.ops
        return variation

    def crop(self, top=0.0, right=1.0, bottom=1.0, left=0.0):
        """
        Add the crops operation to the variation. Coordinates must be a value
        between 0.0-1.0 (where 1.0 represents the full width/height of the
        image).
        """
        self._ops.append(['crop', [top, right, bottom, left]])
        return self

    def fit(self, width, height=None):
        """
        Add the fit operation causing the image to fit with the given width
        and height (in pixels).

        NOTE: If only a width is specified then the fit will be applied as a
        square of width x width.
        """
        self._ops.append(['fit', [width, height or width]])
        return self

    def rotate(self, angle):
        """
        Add the rotate action to the variation for the given angle.
        """
        self._ops.append(['rotate', angle])
        return self

    def output(self, format, quality=None):
        """Add the output operation to the variation"""

        # Build the parameters for the ouput operation
        params = {'format': format}
        if quality:
            params['quality'] = quality

        self._ops.append(['output', params])
        return self

    @property
    def ops(self):
        """Return the ops for the variation."""
        return self._ops