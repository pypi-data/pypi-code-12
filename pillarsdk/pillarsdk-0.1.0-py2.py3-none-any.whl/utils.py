import json
import re
import sys
from datetime import datetime
from contextlib import closing
import requests

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

# from six:
PY3 = sys.version_info[0] == 3
if PY3:
    string_type = str
    text_type = str
else:
    string_type = basestring
    text_type = unicode


class PillarJSONEncoder(json.JSONEncoder):
    """JSON encoder with support for Pillar resources."""

    def default(self, obj):
        # Late import to prevent circular references.
        from .resource import Resource

        if isinstance(obj, datetime):
            return obj.isoformat(' ')
        if isinstance(obj, Resource):
            return obj.to_dict()

        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


def join_url(url, *paths):
    """
    Joins individual URL strings together, and returns a single string.

    Usage::

        >>> join_url("pillar:5000", "shots")
        'pillar:5000/shots'
    """

    assert isinstance(url, string_type), 'URL must be string type, not %r' % url
    for path in paths:
        assert isinstance(path, string_type), 'Path components must be string type, not %r' % path
        url = re.sub(r'/?$', re.sub(r'^/?', '/', path), url)
    return url


def join_url_params(url, params):
    """Constructs a query string from a dictionary and appends it to a url.

    Usage::

        >>> join_url_params("pillar:5000/shots", {"page-id": 2, "NodeType": "Shot Group"})
        'pillar:5000/shots?page-id=2&NodeType=Shot+Group'
    """

    if params is None:
        return url

    def convert_to_string(param):
        if isinstance(param, dict):
            return json.dumps(param, sort_keys=True)
        if isinstance(param, text_type):
            return param.encode('utf-8')
        return param

    # Pass as (key, value) pairs, so that the sorted order is maintained.
    jsonified_params = [
        (key, convert_to_string(params[key]))
        for key in sorted(params.keys())]
    return url + "?" + urlencode(jsonified_params)


def merge_dict(data, *override):
    """
    Merges any number of dictionaries together, and returns a single dictionary.

    Usage::

        >>> md = merge_dict({"foo": "bar"}, {1: 2}, {"foo1": "bar2"})
        >>> md == {1: 2, 'foo': 'bar', 'foo1': 'bar2'}
        True
        >>> merge_dict({'foo': 'bar'}, None)
        {'foo': 'bar'}
        >>> merge_dict(None, {'foo': 'bar'})
        {'foo': 'bar'}
        >>> merge_dict(None, None)
        {}
    """

    result = {}
    for current_dict in (data,) + override:
        if current_dict is None:
            continue
        result.update(current_dict)
    return result


def convert_datetime(item):
    """Starting from a JSON object, find and replace the _create and _updated
    keys with actual datetime objects.
    """
    keys = ['_updated', '_created']

    for k in keys:
        # Check if the key is in the document
        if k in item:
            item[k] = datetime.strptime(item[k], "%a, %d %b %Y %H:%M:%S %Z")

    return item


def remove_none_attributes(attributes):
    """Return a new dict with all None values removed
    :param attributes: Dictionary containing all the item attributes
    """
    # out = {}
    # for k, v in attributes.iteritems():
    #     if v is not None:
    #         if type(v) is dict:
    #             attributes[k] = remove_none_attributes(v)
    #         else:
    #             out[k] = v
    # return out

    if isinstance(attributes, (list, tuple, set)):
        return type(attributes)(remove_none_attributes(x) for x in attributes if x is not None)
    elif isinstance(attributes, dict):
        return type(attributes)((remove_none_attributes(k), remove_none_attributes(v))
                                for k, v in attributes.items() if k is not None and v is not None)
    else:
        return attributes


def download_to_file(url, filename, chunk_size=10 * 1024):
    """Downloads a file via HTTP(S) directly to the filesystem."""

    with closing(requests.get(url, stream=True, verify=True)) as req, \
            open(filename, 'wb') as outfile:
        for block in req.iter_content(chunk_size=chunk_size):
            outfile.write(block)


def sanitize_filename(file_name):
    """Sanitize the filename.

    Returns a new filename with only filename-safe characters.
    """

    # Removes quotes and other unsafe characters.
    # This is easier than keeping good characters and trying to be unicode-friendly.
    badchars = set('''!#$%&*()[]{}'"/\\<>''')
    safe_name = ''.join(c for c in file_name
                        if ord(c) > 31 and c not in badchars)
    return safe_name.strip(' .')
