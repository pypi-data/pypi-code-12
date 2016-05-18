__author__ = 'zhonghong'

from cgi import escape
from urlparse import parse_qs

class Input(object):

    def __init__(self, environ):
        self.environ = environ

    def get(self, key):
        # Returns a dictionary in which the values are lists
        items = parse_qs(self.environ['QUERY_STRING'])

        # As there can be more than one value for a variable then
        # a list is provided as a default value.
        value = items.get(key, [''])[0]

        # Always escape user input to avoid script injection
        value = escape(value)

        return value

    def post(self, key):
        # the environment variable CONTENT_LENGTH may be empty or missing
        try:
            request_body_size = int(self.environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_body_size = 0

        # When the method is POST the variable will be sent
        # in the HTTP request body which is passed by the WSGI server
        # in the file like wsgi.input environment variable.
        request_body = self.environ['wsgi.input'].read(request_body_size)
        items = parse_qs(request_body)

        # As there can be more than one value for a variable then
        # a list is provided as a default value.
        value = items.get(key, [''])[0]

        # Always escape user input to avoid script injection
        value = escape(value)

        return value


