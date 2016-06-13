__author__ = 'zhonghong'

import cgi
from cgi import escape
from urlparse import parse_qs
import traceback
traceback.format_exc()


def is_post_request(environ):
    if environ['REQUEST_METHOD'].upper() != 'POST':
        return False
    content_type = environ.get('CONTENT_TYPE', 'application/x-www-form-urlencoded')
    return (content_type.startswith('application/x-www-form-urlencoded')
            or content_type.startswith('multipart/form-data'))


class InputProcessed(object):
    def read(self, *args):
        raise EOFError('The wsgi.input stream has already been consumed')
    readline = readlines = __iter__ = read


def getfield(f):
    """convert values from cgi.Field objects to plain values."""
    if isinstance(f, list):
        return [getfield(x) for x in f]
    else:
        return f.value


def get_post_form(environ):
    assert is_post_request(environ)
    input = environ['wsgi.input']
    post_form = environ.get('wsgi.post_form')
    if (post_form is not None
        and post_form[0] is input):
        return post_form[2]
    # This must be done to avoid a bug in cgi.FieldStorage
    environ.setdefault('QUERY_STRING', '')
    fs = cgi.FieldStorage(fp=input,
                          environ=environ,
                          keep_blank_values=1)
    new_input = InputProcessed()
    post_form = (new_input, input, fs)
    environ['wsgi.post_form'] = post_form
    environ['wsgi.input'] = new_input
    return fs


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
        fieldstorage = get_post_form(self.environ)
        items = dict([(k, getfield(fieldstorage[k])) for k in fieldstorage])
        value = items.get(key, '')

        # Always escape user input to avoid script injection
        value = escape(value)

        return value

    def data(self):
        """Returns the data sent with the request."""

        # the environment variable CONTENT_LENGTH may be empty or missing
        try:
            request_body_size = int(self.environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_body_size = 0

        data = self.environ['wsgi.input'].read(request_body_size)

        return data
