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

    def list(self, q=None, type=None):
        """List assets for the current account"""
        return self.call_api('', params={'q': q, 'type': type})

    def get(self, uid):
        """Get the details of an asset"""
        return self.call_api('get', params={'uid': uid})

    def upload(self, file, name=None):
        """
        Upload an asset.

        Note: The file argument can be specified as a file object or a tuple of
        the form (filename, file). If a filename cannot be extracted from the
        file object then no extension will be used when saving the upload and so
        this is pretty vital, if you experience this issue you can manually set
        the filename by passing a tuple.
        """

        # Convert the file parameter to a tuple of the form (filename, file) if
        # possible.
        if not isinstance(file, tuple):
            if hasattr(file, 'filename'):
                file = (file.filename, file)

        return self.call_api(
            'upload',
            params={'name': name},
            files= {'asset': file},
            http_method='post'
            )

    def generate_variations(
            self,
            uid,
            variations,
            on_delivery=None,
            webhook=None
            ):
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

        # Build the params
        params = {'uid': uid, 'variations': json.dumps(variations)}

        # Add the `on_delivery` and `webhook` parameters if specified
        if on_delivery:
            params['on_delivery'] = on_delivery

        if webhook:
            params['webhook'] = webhook

        # Call the API and request the new variations
        return self.call_api(
            'generate-variations',
            params=params,
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

        # Build the params
        params = {'uid': uid}

        # Add the `expires` parameter if specified
        if expires:
            params['expires'] = expires

        # Call the API and request a new expiry date is set
        return self.call_api(
            'set-expires',
            params=params,
            http_method='post'
            )


class Hanger51ClientMock(Hanger51Client):
    """
    Mocked version of Hanger51Client for use in test environments.
    """

    def call_api(self, api_method, params=None, files=None, http_method='get'):
        """
        For the mock client we provide standard responses for each API method
        and for some special cases parameters will also be taken in to account
        (e.g `on_delivery` for the `generate_variations` method).
        """

        # If not parameters are provide set the value to an empty dictionary by
        # default.
        if params is None:
            params = {}

        # Return a response to the method
        if api_method == 'list':
            return self._list_response()

        elif api_method == 'generate_variations':
            on_delivery = params.get('on_delivery', 'wait')
            return self._generate_variations_response(on_delivery)

        elif api_method == 'get':
            return self._get_response()

        elif api_method == 'set_expires':
            return self._set_expires_response()

        elif api_method == 'upload':
            return self._upload_response()

    # Response methods

    def _list_response(self):
        # Return a mock response for the `list` API method
        return {
            'assets': [
                {
                    'created': '2016-03-27 14:20:01',
                    'store_key': 'file.bf6yfw.zip',
                    'type': 'file',
                    'uid': 'bf6yfw'
                }, {
                    'created': '2016-03-27 14:27:44',
                    'store_key': 'image.lxfngl.jpg',
                    'type': 'image',
                    'uid': 'lxfngl'
                }
            ],
            'total_assets': 2,
            'total_pages': 1
        }

    def _generate_variations_response(self, on_delivery='wait'):
        # Return a mock response for the `generate_variations` API method

        # Check if the request must wait for the variation to be generated
        if on_delivery == 'wait':
            return {
                'thumb': {
                    'ext': 'webp',
                    'meta': {
                        'image': {
                            'mode': 'RGB',
                            'size': [100, 133]
                        },
                        'length': 3004
                    },
                    'name': 'thumb',
                    'store_key': 'image.lxfngl.thumb.j1l.webp',
                    'version': 'j1l'
                }
            }

        return None

    def _get_response(self):
        # Return a mock response for the `get` API method
        return {
            'created': '2016-03-27 14:27:44',
            'ext': 'jpg',
            'meta': {
                'filename': 'image.jpg',
                'image': {
                    'mode': 'RGB',
                    'size': [720, 960]
                },
                'length': 130793
            },
            'modified': '2016-03-27 14:27:44',
            'name': 'image',
            'store_key': 'image.lxfngl.jpg',
            'type': 'image',
            'uid': 'lxfngl',
            'variations': []
        }

    def _set_expires_response(self):
        # Return a mock response for the `set_expires` API method
        return None

    def _upload_response(self):
        # Return a mock response for the `upload` API method
        return {
            'created': '2016-03-27 14:27:44',
            'ext': 'jpg',
            'meta': {
                'filename': 'image.jpg',
                'image': {
                    'mode': 'RGB',
                    'size': [720, 960]
                },
                'length': 130793
            },
            'modified': '2016-03-27 14:27:44',
            'name': 'image',
            'store_key': 'image.lxfngl.jpg',
            'type': 'image',
            'uid': 'lxfngl',
            'variations': []
        }


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