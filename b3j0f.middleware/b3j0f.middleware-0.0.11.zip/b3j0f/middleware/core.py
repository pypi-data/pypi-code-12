# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2016 Jonathan Labéjof <jonathan.labejof@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# --------------------------------------------------------------------

"""Core module which register middleware callable objects to protocols.

A protocol is a string value such as database, rpc, mongo, influxdb, etc."""

__all__ = ['register', 'unregister', 'getmcallers']

from collections import Iterable

from six import string_types

#: registry of middleware callers by protocol names.
_MIDDLEWARES_BY_PROTOCOLS = {}


def register(protocols, middlewares=None):
    """Register middlewares with input protocols.

    Middleware are callable objects, such as a socket connection.

    Could be also used such as a decorator.

    .. example::

        class Database(object): pass
        register(['database'], Database)

        # and

        @register(['database'])
        class DBClient(object): pass

        #are sames.

    :param str(s) protocols: protocols to register.
    :param callable(s) middlewares: callable middleware objects."""

    if isinstance(protocols, string_types):
        protocols = [protocols]

    def _registercls(middlewares):
        """In case of a decorator, this function register input callable
        middleware objects with input protocols.

        :param list middlewares: callable middleware objects to register."""

        result = middlewares

        if not isinstance(middlewares, Iterable):
            middlewares = [middlewares]

        for middleware in middlewares:

            if not callable(middleware):
                raise TypeError('Middleware {0} is not callable'.format(
                    middleware
                ))

            for protocol in protocols:
                _MIDDLEWARES_BY_PROTOCOLS.setdefault(protocol, set()).add(
                    middleware
                )

        return result

    if middlewares is None:  # in case of a decorator
        return _registercls

    else:
        _registercls(middlewares=middlewares)


def unregister(middlewares=None, protocols=None):
    """Unregister middlewares.

    :param callable(s) middlewares: middlewares to unregister. Default all.
    :param str(s) protocols: protocols to unregister. Default all."""

    if (middlewares, protocols) == (None, None):
        _MIDDLEWARES_BY_PROTOCOLS.clear()

    else:

        if middlewares is not None:
            if callable(middlewares):
                middlewares = [middlewares]

            middlewares = set(middlewares)

        if protocols is None:
            protocols = list(_MIDDLEWARES_BY_PROTOCOLS)

        elif isinstance(protocols, string_types):
            protocols = [protocols]

        for protocol in protocols:

            if middlewares is None:
                del _MIDDLEWARES_BY_PROTOCOLS[protocol]

            else:
                _middlewares = _MIDDLEWARES_BY_PROTOCOLS[protocol]

                _middlewares -= middlewares

                if _middlewares:
                    _MIDDLEWARES_BY_PROTOCOLS[protocol] = _middlewares

                else:
                    del _MIDDLEWARES_BY_PROTOCOLS[protocol]


def getmcallers(protocols):
    """Get middleware callers from input protocols.

    :param str(s) protocols: protocol names.
    :raises: ValueError if protocols are not registered.
    :rtype: set
    """

    result = set()

    if isinstance(protocols, string_types):
        protocols = [protocols]

    for protocol in protocols:
        try:
            pmiddlewares = _MIDDLEWARES_BY_PROTOCOLS[protocol]

        except (KeyError, IndexError):
            result = set()
            break

        else:
            if not result:
                result = set(pmiddlewares)

            else:
                result &= pmiddlewares

            if not result:
                break

    if not result:
        raise ValueError('{0} middleware not found.'.format(protocols))

    return result


def getprotocols(middlewares=None):
    """Get all protocols matching exclusively all input middlewares.

    :param callable(s) middlewares: group of middleware objects from where get
        protocols. If None, get all protocols.

    :return: protocols used by all middlewares, or all protocols if middlewares
        is not given.
    :rtype: set"""

    result = set()

    if middlewares is None:
        result = set(_MIDDLEWARES_BY_PROTOCOLS)

    else:
        if not isinstance(middlewares, Iterable):
            middlewares = [middlewares]

        middlewares = set(middlewares)
        for key in _MIDDLEWARES_BY_PROTOCOLS:

            if (middlewares & _MIDDLEWARES_BY_PROTOCOLS[key]) == middlewares:
                result.add(key)

    return result
