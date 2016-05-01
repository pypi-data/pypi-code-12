import json
from operator import itemgetter

import treq
from twisted.python.url import URL

from txdocumint.error import (
    DocumintError, DocumintErrorCause, MalformedDocumintError)


def json_request(request, method, url, **kw):
    """
    Make a request to a JSON-REST endpoint.
    """
    headers = kw.pop('headers', {})
    headers.update({b'Accept': b'application/json'})
    d = request(method, url, headers=headers, **kw)
    d.addCallback(treq.json_content)
    return d


def post_json(request, url, **kw):
    """
    Make a POST request to a JSON-REST endpoint.
    """
    headers = {b'Content-Type': b'application/json'}
    headers.update(kw.pop('headers', {}))
    return json_request(request, b'POST', url, headers=headers, **kw)


def documint_request_factory(request):
    """
    Create a function that issues a request to a Documint endpoint.

    Status codes outside the 2xx range are treated as errors. If error
    responses are JSON then `DocumintError` is raised, otherwise
    `MalformedDocumintError` is raised.

    If the status code indicates success, the `IResponse` is returned.
    """
    def _raise_error(data, response):
        if content_type(response.headers) == b'application/json':
            try:
                causes = json.loads(data).get(u'causes', [])
                raise DocumintError(
                    causes=[DocumintErrorCause(cause.get(u'type'),
                                               cause.get(u'reason'),
                                               cause.get(u'description'))
                            for cause in causes])
            except ValueError:
                pass
        raise MalformedDocumintError(data)

    def _check_status(response):
        if 200 <= response.code < 300:
            return response
        d = response.content()
        d.addCallback(_raise_error, response)
        return d

    def _request(*a, **kw):
        d = request(*a, **kw)
        d.addCallback(_check_status)
        return d

    return _request


def content_type(headers):
    """
    Extract the content type from a `Headers` instance, defaulting to
    ``application/octet-stream``.
    """
    return next(
        iter(headers.getRawHeaders(b'Content-Type', default=[])),
        b'application/octet-stream').split(';', 1)[0]


class Session(object):
    """
    Documint session.
    """
    def __init__(self, session_info, request):
        """
        :param dict session_info: Session information, as returned by ``GET
        /sessions/<session_id>`` from Documint.
        :param request: Callable for making requests.
        :type request: Callable mimicing the signature of `treq.request`.
        """
        self._session_info = session_info
        self._request = request

    def store_content(self, fileobj, content_type):
        """
        Temporarily store content in this session.

        :param file-like fileobj: File-like object to stream content data from.
        :param unicode content_type: Content type of the data being stored.
        :return: URI to the stored content.
        :rtype: Deferred<unicode>
        """
        d = post_json(self._request,
                      self._session_info[u'store-content'],
                      data=fileobj,
                      headers={b'Content-Type': content_type})
        d.addCallback(itemgetter(u'links'))
        d.addCallback(itemgetter(u'self'))
        return d

    def get_content(self, uri, write):
        """
        Fetch content.

        Technically ``uri`` need not be part of the session, this is
        just a convenience function.

        :param unicode uri: URI to retrieve the content from.
        :param write: Callable invoked to write streamed data to a destination.
        :type write: callable taking a single `bytes` argument
        :return: Content type.
        :rtype: Deferred<bytes>
        """
        def _collect(response):
            d = treq.collect(response, write)
            d.addCallback(lambda _: content_type(response.headers))
            return d
        d = self._request(b'GET', uri)
        d.addCallback(_collect)
        return d

    def perform_action(self, action_and_parser):
        """
        Perform a Documint action.

        :param action_and_parser: Action description and parameters, and a
        parser for the action result. See `txdocumint.actions`
        for action factories.
        :return: Action response.
        :rtype: Deferred<dict>
        """
        action, parser = action_and_parser
        d = post_json(self._request,
                      self._session_info[u'perform'],
                      data=json.dumps(action))
        d.addCallback(parser)
        return d

    def delete(self):
        """
        Delete the session and all its content.
        """
        d = self._request(b'DELETE', self._session_info[u'self'])
        d.addCallback(treq.content)
        return d


def create_session(endpoint, request=treq.request):
    """
    Create a new `Session` instance.

    :param unicode endpoint: URI to the root of the Documint service.
    :param request: Callable for making requests.
    :type request: Callable mimicing the signature of `treq.request`.
    """
    uri = URL.fromText(endpoint).child(u'sessions').child(u'')
    request = documint_request_factory(request)
    d = post_json(request, uri.asURI().asText().encode('utf-8'))
    d.addCallback(itemgetter(u'links'))
    d.addCallback(Session, request)
    return d


def get_session(uri, request=treq.request):
    """
    Create a `Session` instance from an existing session URI.

    :param unicode uri: Session URI.
    :param request: Callable for making requests.
    :type request: Callable mimicing the signature of `treq.request`.
    """
    request = documint_request_factory(request)
    d = json_request(request, b'GET', uri.encode('utf-8'))
    d.addCallback(itemgetter(u'links'))
    d.addCallback(Session, request)
    return d


__all__ = ['create_session', 'get_session']
