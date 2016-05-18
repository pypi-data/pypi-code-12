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

#: registry of middleware callers by protocol names.
_MIDDLEWARES_BY_PROTOCOLS = {}


def register(protocols, middleware=None):
    """Register a middleware with input protocols.

    A middleware is a callable object, such as a socket connection.

    Could be also used such as a decorator.

    .. example::

        class Database(object): pass
        register(['database'], Database)

        # and

        @register(['database'])
        class DBClient(object): pass

        #are sames.

    :param list protocols: protocols to register.
    :param callable middleware: callable middleware."""


    def _registercls(middleware):
        """In case of a decorator, this function register input callable
        middleware object with input protocols.

        :param callable middleware: middleware to register."""

        for protocol in protocols:
            middlewares = _MIDDLEWARES_BY_PROTOCOLS.setdefault(protocol, [])
            middlewares.append(middleware)

        return middleware

    if middleware is None:  # in case of a decorator
        return _registercls

    else:
        _registercls(middleware=middleware)


def unregister(middlewares=None, protocols=None):
    """Unregister middlewares.

    :param list middlewares: middlewares to unregister. Default all.
    :param list protocols: protocols to unregister. Default all."""

    if (middlewares, protocols) == (None, None):
        _MIDDLEWARES_BY_PROTOCOLS.clear()

    else:
        if middlewares is not None:
            middlewares = set(middlewares)

        if protocols is None:
            protocols = list(_MIDDLEWARES_BY_PROTOCOLS.keys())

        for protocol in protocols:

            _middlewares = _MIDDLEWARES_BY_PROTOCOLS[protocol]

            if middlewares is None:
                del _MIDDLEWARES_BY_PROTOCOLS[protocol]

            else:
                _middlewares = list(set(_middlewares) & middlewares)
                if _middlewares:
                    _MIDDLEWARES_BY_PROTOCOLS[protocol] = _middlewares

                else:
                    del _MIDDLEWARES_BY_PROTOCOLS[protocol]


def getmcallers(protocols):
    """Get middleware callers from input protocols.

    :param list protocols: protocol names.
    :raises: ValueError if protocols are not registered.
    """

    result = None

    for protocol in protocols:
        try:
            pmiddlewares = _MIDDLEWARES_BY_PROTOCOLS[protocol]

        except (KeyError, IndexError):
            result = False
            break

        else:
            if result is None:
                result = set(pmiddlewares)

            else:
                result &= pmiddlewares

            if not result:
                break

    if not result:
        raise ValueError('{0} middleware not found.'.format(protocols))

    return result
