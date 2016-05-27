# -*- coding: utf-8 -*-
from __future__ import print_function

import glob
import os

try:
    from urlparse import parse_qs
except ImportError:
    from urllib.parse import parse_qs

modules = glob.glob(os.path.dirname(__file__) + "/*.py")
__all__ = [os.path.basename(f)[:-3] for f in modules
           if not os.path.basename(f).startswith('_') and
           not f.endswith('__init__.py') and os.path.isfile(f)]


def unicode_type():
    """ Find the Unicode class for this version of Python.
        Between Python 2.x and 3.x, classes and text handling has
        changed a considerable amount.
        Python 2.x uses ASCII strings with str() and Unicode with
        unicode().
        Python 3.x uses Unicode strings with str() and "strings of
        bytes" as bytes().
    """

    try:
        import builtins
        __old_unicode = False
    except ImportError:
        __old_unicode = True

    if __old_unicode:
        return unicode  # flake8: noqa
    elif not __old_unicode:
        return str  # flake8: noqa


def string_type():
    """ Find the String class for this version of Python.
        Between Python 2.x and 3.x, classes and text handling has
        changed a considerable amount.
        Python 2.x uses ASCII strings with str() and Unicode with
        unicode().
        Python 3.x uses Unicode strings with str() and "strings of
        bytes" as bytes().
    """

    try:
        import builtins
        __old_string = True
    except ImportError:
        __old_string = False

    if __old_string:
        return str  # flake8: noqa
    elif not __old_string:
        return bytes  # flake8: noqa


def unicode2str(obj):
    """ Recursively convert an object and members to str objects
        instead of unicode objects, if possible.

        This only exists because of the incoming world of unicode_literals.

        :param object obj: object to recurse
        :return: object with converted values
        :rtype: object
    """

    if isinstance(obj, dict):
        return {unicode2str(k): unicode2str(v) for k, v in
                obj.items()}
    elif isinstance(obj, list):
        return [unicode2str(i) for i in obj]
    elif isinstance(obj, unicode_type()):
        return obj.encode("utf-8")
    else:
        return obj


def str2unicode(obj, encoding='utf-8'):
    """ Recursively convert an object and members to unicode objects
        instead of str objects, if possible.

        This only exists because of the incoming world of unicode_literals.

        :param object obj: object to recurse
        :param str encoding: encoding to decode from
        :return: object with converted values
        :rtype: object
    """

    if isinstance(obj, dict):
        return {str2unicode(k): str2unicode(v) for k, v in
                obj.items()}
    elif isinstance(obj, list):
        return [str2unicode(i) for i in obj]
    elif isinstance(obj, string_type()):
        return obj.decode(encoding)
    else:
        return obj


def parse_uri(uri):
    """ This implies that we are passed a uri that looks something like:
          proto://username:password@hostname:port/database

        In most cases, you can omit the port and database from the string:
          proto://username:password@hostname

        Also, in cases with no username, you can omit that:
          proto://:password@hostname:port/database

        Also supports additional arguments:
          proto://hostname:port/database?arg1=val&arg2=vals

        :param str uri: URI to parse
        :rtype: dict
        :returns: Dictionary with parsed URL components

        .. note::
            This function may move, as the currently location may not
            be optimal. Location will be finalized by 1.0.0 stable release.
    """

    proto = uri.split('://')[0]
    uri = uri.split('://')[1]

    _host = uri.split('@')[-1]
    _host = _host.split(':')
    if len(_host) == 2:
        host = _host[0]
        if '/' in _host[1]:
            port = int(_host[1].split('/')[0])
        else:
            port = int(_host[1])
    else:
        host = _host[0]
        if '/' in host:
            host = host.split('/')[0]
        port = None

    if "@" in uri:
        _cred = uri[0:uri.rfind(':'.join(_host)) - 1]
        _cred = _cred.split(':')
        if len(_cred) == 2:
            _user = _cred[0]
            _pass = _cred[1]
        else:
            _user = _cred[0]
            _pass = None
    else:
        _user = None
        _pass = None

    database = uri.split('/')
    if len(database) >= 2:
        database = database[1]
        if '?' in database:
            _db = database.split('?')
            database = _db[0]
            args = parse_qs(_db[1], keep_blank_values = True)
        else:
            args = None
    else:
        database = None
        args = None

    return {
        "protocol": proto,
        "resource": uri,
        "host": host,
        "port": port,
        "username": _user,
        "password": _pass,
        "database": database,
        "args": args,
        "uri": "{}://{}".format(proto, uri),
    }
