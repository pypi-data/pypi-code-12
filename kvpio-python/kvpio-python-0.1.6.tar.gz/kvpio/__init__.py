"""
`copyright` (c) 2016 by Steelhive, LLC

`license` MIT, see LICENSE for more details

kvpio
-----
__The core python bindings for [kvp.io](https://www.kvp.io)__

Accessing account information:

    import kvpio
    kvpio.api_key = '123abc'
    account = kvpio.Account().get()
    # {"id": "kvp.io", "email": "support@kvp.io", "reads": 87, "size": 124}

Writing to your bucket:

    data = {
        'foo': 123,
        'bar': True,
        'baz': {
            'boo': 321,
            'far': False,
            'faz': [1, 2, 3]
        }
    }
    bucket = kvpio.Bucket()
    bucket.set('my_key', data)

Reading nested data from your bucket:

    data = bucket.get('my_key/baz/faz')
    # [1, 2, 3]

"""

# imports
import os
import requests
import json as JSON


# The API key to use for authentication
api_key = None

# The API version in use, e.g., `v1`
api_ver = 'v1'

# The base url of the API, e.g., _https://api.kvp.io_
api_base = 'https://api.kvp.io'

# Toggle auto-parsing of JSON, default: `False`
load_json = False

# The supported HTTP methods
http_methods = [
    'get',
    'post',
    'delete'
]

class Endpoint(object):
    """
    __Represents an API endpoint from the client-side's perspective.__

    This class should not need to be instantiated manually. It is essentially
    a convenience wrapper for the [requests](http://docs.python-requests.org)
    library with a few properties.

    - params:
        - name: name of the api endpoint to access, e.g., 'bucket'
    """
    name = None

    def __init__(self, name):
        self.name = name

    @property
    def auth(self):
        """
        __Gets a `requests` compatible Basic Auth tuple.__
        """
        return (api_key, '')

    @property
    def url(self):
        """
        __Gets the compiled target url of the endpoint.__
        """
        return '/'.join([api_base, api_ver, self.name])

    def request(self, method, key='', params=None, json=None):
        """
        __A simple request wrapper. Used by get, post, etc. methods.__

        - params:
            - method: a supported HTTP verb
            - key: a key path appended to an endpoint url
            - params: the url parameters to pass to the endpoint
            - json: a JSON encodable value to pass to the endpoint

        - returns:
            - tuple: a tuple of the form (int, str) where the first element is the response code and the second is a JSON decodable value or an empty string
        """
        if method not in http_methods:
            raise Exception('Unsupported method attempted: {}'.format(method))
        # cause an exception if the data can't be jsonified
        JSON.dumps(json)
        response = getattr(requests, method)(
            '{}/{}'.format(self.url, key),
            params=params,
            json=json,
            auth=self.auth
        )
        if load_json:
            try:
                return (response.status_code, JSON.loads(response.text))
            except:
                pass
        return (response.status_code, response.text)


class Account(Endpoint):
    """
    __Provides access to account information.__
    """
    def __init__(self):
        super(Account, self).__init__('account')

    def get(self):
        """
        __Requests the current account information as a JSON string, e.g.,__

            {
                'id': 'Account Name',
                'email': 'you@domain.tld',
                'reads': 154,
                'size': 140762
            }

        - returns:
            - tuple: status code, JSON encoded string representation of the account
        """
        return self.request('get')


class Bucket(Endpoint):
    """
    __Provides access to bucket (key/value pair) storage.__
    """
    def __init__(self):
        super(Bucket, self).__init__('bucket')

    def list(self):
        """
        __Retrieves the current list of keys.__

        - returns:
            - tuple: status code, JSON encoded list of keys
        """
        return self.request('get')

    def get(self, key):
        """
        __Retrieves either the value stored at the key.__

        - params:
            - key: the key or key path under which a value is stored

        - returns:
            - tuple: status code, JSON encoded string of the value
        """
        return self.request('get', key)

    def set(self, key, data):
        """
        __Assigns a value to the key path.__

        - params:
            - key: the key or key path under which a value is stored
            - data: JSON encodable value to assign to store under key

        - returns:
            - tuple: status code, empty string
        """
        return self.request('post', key, json=data)

    def delete(self, key):
        """
        __Deletes a key, it's value, and all values beneath it.__

        - params:
            - key: the key or key path under which a value is stored

        - returns:
            - tuple: status code, empty string
        """
        return self.request('delete', key)


class Templates(Endpoint):
    """
    __Provides access to templates storage.__
    """
    def __init__(self):
        super(Templates, self).__init__('templates')

    def list(self):
        """
        __Retrieves the current list of templates.__

        - returns:
            - tuple: status code, JSON encoded list of templates
        """
        return self.request('get')

    def get(self, key, data=None, raw=False):
        """
        __Retrieves the template stored at key.__

        The template is rendered with
        data pulled from the account's bucket using the
        [Jinja2](http://jinja.pocoo.org) engine.

        If `raw` is `True, returns the template un-rendered.

        If `data` is provided, it is used to override bucket values.

        - params:
            - key: the key or key path under which the template is stored
            - data: JSON encodable value used to override bucket data
            - raw: whether or not to render the template

        - returns:
            - tuple: status code, the rendered, or un-rendered, template document
        """
        return self.request('get', key, params={'raw': raw}, json=data)

    def set(self, key, template):
        """
        __Stores the template document under key.__

        - params:
            - key: the key under which the template will be stored
            - template: the template document, optionally written with Jinja2

        - returns:
            - tuple: status code, empty string
        """
        return self.request('post', key, json=template)

    def delete(self, key):
        """
        __Deletes a key and it's template document.__

        - params:
            - key: the key under which the template is stored

        - returns:
            - tuple: status code, empty string
        """
        return self.request('delete', key)
