# coding: utf8
from __future__ import unicode_literals
from api_star.exceptions import NotAcceptable, UnsupportedMediaType
from api_star.parsers import json_parser, multipart_parser, urlencoded_parser
from api_star.renderers import json_renderer
from werkzeug.datastructures import MultiDict


def _negotiate_parser(content_type, parsers):
    """
    Given the value of a 'Content-Type' header, return the appropriate
    parser registered to decode the request content.
    """
    if content_type is None:
        return parsers[0]

    content_type = content_type.split(';')[0].strip().lower()

    for parser in parsers:
        if parser.media_type == content_type:
            return parser

    raise UnsupportedMediaType()


def _negotiate_renderer(accept, renderers):
    """
    Given the value of a 'Accept' header, return a two tuple of the appropriate
    content type and codec registered to encode the response content.
    """
    if accept is None:
        return renderers[0]

    acceptable = set([
        item.split(';')[0].strip().lower()
        for item in accept.split(',')
    ])

    for renderer in renderers:
        if renderer.media_type in acceptable:
            return renderer

    for renderer in renderers:
        if renderer.media_type.split('/')[0] + '/*' in acceptable:
            return renderer

    if '*/*' in acceptable:
        return renderers[0]

    raise NotAcceptable()


class RequestMixin(object):
    _parsers = (json_parser(), multipart_parser(), urlencoded_parser())
    _renderers = (json_renderer(),)
    _authenticators = ()

    @property
    def parsers(self):
        return self._parsers

    @property
    def renderers(self):
        return self._renderers

    @property
    def authenticators(self):
        return self._authenticators

    # Accessing `request.parser` or `request.renderer` will return the
    # negotiatated instance, given the instances available on the request.
    @property
    def parser(self):
        if not hasattr(self, '_parser'):
            try:
                self._parser = self._determine_parser()
            except:
                self._parser = None
                raise
        return self._parser

    @property
    def renderer(self):
        if not hasattr(self, '_renderer'):
            try:
                self._renderer = self._determine_renderer()
            except:
                self._renderer = None
                raise
        return self._renderer

    @property
    def authenticator(self):
        if not hasattr(self, '_authenticator'):
            try:
                self._auth, self._authenticator = self._authenticate()
            except:
                self._auth, self._authenticator = (None, None)
                raise
        return self._authenticator

    @property
    def auth(self):
        if not hasattr(self, '_auth'):
            try:
                self._auth, self._authenticator = self._authenticate()
            except:
                self._auth, self._authenticator = (None, None)
                raise
        return self._auth

    # The properties `request.parsers`, `request.parser`, `request.renderers`
    # and `request.renderer` can only be modified up until the point we
    # perform content negotiation against them.
    @parsers.setter
    def parsers(self, value):
        if hasattr(self, '_parser'):
            msg = "You cannot set the `request.parsers` property after parsing the request data."
            raise RuntimeError(msg)
        self._parsers = value

    @parser.setter
    def parser(self, value):
        if hasattr(self, '_parser'):
            msg = "You cannot set the `request.parser` property after parsing the request data."
            raise RuntimeError(msg)
        self._parser = value

    @renderers.setter
    def renderers(self, value):
        if hasattr(self, '_renderer'):
            msg = "You cannot set the `request.renderers` property after rendering the response."
            raise RuntimeError(msg)
        self._renderers = value

    @renderer.setter
    def renderer(self, value):
        if hasattr(self, '_renderer'):
            msg = "You cannot set the `request.renderer` property after rendering the response."
            raise RuntimeError(msg)
        self._renderer = value

    @authenticators.setter
    def authenticators(self, value):
        if hasattr(self, '_authenticator'):
            msg = "You cannot set the `request.authenticators` property after authenticating the request."
            raise RuntimeError(msg)
        self._authenticators = value

    @authenticator.setter
    def authenticator(self, value):
        if hasattr(self, '_auth'):
            msg = "You cannot set the `request.authenticator` property after authenticating the request."
            raise RuntimeError(msg)
        self._authenticator = value

    @auth.setter
    def auth(self, value):
        if hasattr(self, '_auth'):
            msg = "You cannot set the `request.auth` property after authenticating the request."
            raise RuntimeError(msg)
        self._auth = value

    # Accessing `request.data` returns the parsed request content.
    @property
    def data(self):
        if not hasattr(self, '_data'):
            try:
                self._data = self._parse()
            except:
                self._data = None
                raise
        return self._data

    # The `request.data` attribute should be used in preference to Flask's
    # `request.form` and `request.files`.
    @property
    def form(self):
        msg = 'Accessing `request.form` in Flask API is incorrect, use `request.data` instead.'
        raise NotImplementedError(msg)

    @property
    def files(self):
        msg = 'Accessing `request.files` in Flask API is incorrect, use `request.data` instead.'
        raise NotImplementedError(msg)

    # Implementations of negotiation and request parsing.
    def _parse(self):
        """
        Parse the body of the request, using whichever parser satifies the
        client 'Content-Type' header, returning the parsed data.
        """
        if not self.content_type or not self.content_length:
            return MultiDict()

        context = {
            'headers': self.headers,
            'content_type': self.content_type,
            'content_length': self.content_length
        }
        return self.parser(self.stream, **context)

    def _authenticate(self):
        """
        Authenticate the incoming request, populating the `request.auth`
        and `request.authenticator` properties.
        """
        for authenticator in self.authenticators:
            auth = authenticator(self)

            if auth is not None:
                return (auth, authenticator)

        return (None, None)

    def _determine_parser(self):
        """
        Determine which of the available parsers should be used for
        parsing the request content, based on the client 'Content-Type' header.
        """
        return _negotiate_parser(self.content_type, self.parsers)

    def _determine_renderer(self):
        """
        Determine which of the available renderers should be used for
        rendering the response content, based on the client 'Accept' header.
        """
        accept = self.headers.get('Accept', '*/*')
        return _negotiate_renderer(accept, self.renderers)
