import json
from StringIO import StringIO

from testtools import TestCase
from testtools.matchers import (
    AfterPreprocessing, ContainsDict, Equals, IsInstance, MatchesAll,
    MatchesListwise, MatchesStructure)
from testtools.twistedsupport import failed, succeeded
from treq.testing import StringStubbingResource, StubTreq
from twisted.web.http_headers import Headers

from txdocumint._client import (
    content_type, create_session, documint_request_factory, get_session,
    json_request, post_json, Session)
from txdocumint.error import DocumintError, MalformedDocumintError


class JSONRequestTests(TestCase):
    """
    Tests for `txdocumint._client.json_request`.
    """
    def test_overwrite_accept(self):
        """
        If an existing ``Accept`` header exists it is overwritten.
        """
        def _response_for(method, url, params, headers, data):
            self.assertThat(method, Equals(u'GET'))
            self.assertThat(url, Equals(b'http://example.com/get_json'))
            self.assertThat(
                headers,
                ContainsDict(
                    {b'Accept': Equals([b'application/json'])}))
            return 200, {}, json.dumps({u'arst': u'arst'})
        resource = StringStubbingResource(_response_for)
        treq = StubTreq(resource)
        self.assertThat(
            json_request(treq.request, b'GET', b'http://example.com/get_json',
                         headers={b'Accept': b'text/plain'}),
            succeeded(
                Equals({u'arst': u'arst'})))

    def test_request(self):
        """
        Makes a request and decodes JSON responses.
        """
        def _response_for(method, url, params, headers, data):
            self.assertThat(method, Equals(u'GET'))
            self.assertThat(url, Equals(b'http://example.com/get_json'))
            self.assertThat(
                headers,
                ContainsDict(
                    {b'Accept': Equals([b'application/json'])}))
            return 200, {}, json.dumps({u'arst': u'arst'})
        resource = StringStubbingResource(_response_for)
        treq = StubTreq(resource)
        self.assertThat(
            json_request(treq.request, b'GET', b'http://example.com/get_json'),
            succeeded(
                Equals({u'arst': u'arst'})))


class PostJSONTests(TestCase):
    """
    Tests for `txdocumint._client.post_json`.
    """
    def test_own_content_type(self):
        """
        If an existing ``Content-Type`` header exists it is used instead of
        ``application/json``.
        """
        def _response_for(method, url, params, headers, data):
            self.assertThat(method, Equals(u'POST'))
            self.assertThat(url, Equals(b'http://example.com/post_json'))
            self.assertThat(
                headers,
                ContainsDict(
                    {b'Accept': Equals([b'application/json']),
                     b'Content-Type': Equals([b'text/plain'])}))
            return 200, {}, json.dumps({u'arst': u'arst'})
        resource = StringStubbingResource(_response_for)
        treq = StubTreq(resource)
        self.assertThat(
            post_json(treq.request, b'http://example.com/post_json',
                      headers={b'Content-Type': b'text/plain'}),
            succeeded(
                Equals({u'arst': u'arst'})))

    def test_request(self):
        """
        Makes a POST request and decodes JSON responses.
        """
        def _response_for(method, url, params, headers, data):
            self.assertThat(method, Equals(u'POST'))
            self.assertThat(url, Equals(b'http://example.com/post_json'))
            self.assertThat(
                headers,
                ContainsDict(
                    {b'Accept': Equals([b'application/json']),
                     b'Content-Type': Equals([b'application/json'])}))
            return 200, {}, json.dumps({u'arst': u'arst'})
        resource = StringStubbingResource(_response_for)
        treq = StubTreq(resource)
        self.assertThat(
            post_json(treq.request, b'http://example.com/post_json'),
            succeeded(
                Equals({u'arst': u'arst'})))


class DocumintRequestFactoryTests(TestCase):
    """
    Tests for `txdocumint._client.documint_request_factory`.
    """
    def test_malformed_error(self):
        """
        Documint errors that do not have a JSON content type raise
        `MalformedDocumintError`.
        """
        def _response_for(method, url, params, headers, data):
            return 400, {}, b'an error'
        resource = StringStubbingResource(_response_for)
        treq = StubTreq(resource)
        request = documint_request_factory(treq.request)
        self.assertThat(
            request(b'GET', b'http://example.com/malformed_error'),
            failed(
                AfterPreprocessing(
                    lambda f: f.value,
                    MatchesAll(
                        IsInstance(MalformedDocumintError),
                        MatchesStructure(data=Equals(b'an error'))))))

    def test_not_json_error(self):
        """
        Documint errors that have a JSON content type but do not contain valid
        JSON raise `MalformedDocumintError`.
        """
        def _response_for(method, url, params, headers, data):
            return (400,
                    {b'Content-Type': b'application/json'},
                    b'hello world')
        resource = StringStubbingResource(_response_for)
        treq = StubTreq(resource)
        request = documint_request_factory(treq.request)
        self.assertThat(
            request(b'GET', b'http://example.com/not_json_error'),
            failed(
                AfterPreprocessing(
                    lambda f: f.value,
                    MatchesAll(
                        IsInstance(MalformedDocumintError),
                        MatchesStructure(data=Equals(b'hello world'))))))

    def test_error(self):
        """
        Documint errors are parsed into a structured exception.
        """
        def _response_for(method, url, params, headers, data):
            return (400,
                    {b'Content-Type': b'application/json'},
                    json.dumps({u'causes': [
                        {u'type': u'foo',
                         u'reason': 42,
                         u'description': u'nope'},
                        {u'type': u'bar',
                         u'reason': 42,
                         u'description': None},
                        {u'type': u'baz',
                         u'reason': None,
                         u'description': None}]}))
        resource = StringStubbingResource(_response_for)
        treq = StubTreq(resource)
        request = documint_request_factory(treq.request)

        def cause(t, r=None, d=None):
            return MatchesStructure(type=Equals(t),
                                    reason=Equals(r),
                                    description=Equals(d))
        self.assertThat(
            request(b'GET', b'http://example.com/error'),
            failed(
                AfterPreprocessing(
                    lambda f: f.value,
                    MatchesAll(
                        IsInstance(DocumintError),
                        MatchesStructure(
                            causes=MatchesListwise([
                                cause(u'foo', 42, u'nope'),
                                cause(u'bar', 42),
                                cause(u'baz')]))))))

    def test_success(self):
        """
        Status codes indicating success pass the response through without any
        exceptions.
        """
        def _response_for(method, url, params, headers, data):
            return 200, {}, b'hello world'
        resource = StringStubbingResource(_response_for)
        treq = StubTreq(resource)
        request = documint_request_factory(treq.request)
        self.assertThat(
            request(b'GET', b'http://example.com/success'),
            succeeded(
                AfterPreprocessing(
                    treq.content,
                    succeeded(Equals(b'hello world')))))


class ContentTypeTests(TestCase):
    """
    Tests for `txdocumint._client.content_type`.
    """
    def test_missing(self):
        """
        Default to ``application/octet-stream`` if there is no ``Content-Type``
        header.
        """
        headers = Headers()
        self.assertThat(
            content_type(headers),
            Equals(b'application/octet-stream'))

    def test_content_type(self):
        """
        Use the first ``Content-Type`` header.
        """
        headers = Headers({b'Content-Type': [b'application/json',
                                             b'text/plain']})
        self.assertThat(
            content_type(headers),
            Equals(b'application/json'))


class SessionTests(TestCase):
    """
    Tests for `txdocumint._client.Session`.
    """
    def test_store_content(self):
        """
        Store content in a Documint session.
        """
        def _response_for(method, url, params, headers, data):
            self.assertThat(method, Equals(b'POST'))
            self.assertThat(
                headers,
                ContainsDict({
                    b'Accept': Equals([b'application/json']),
                    b'Content-Type': Equals([b'text/plain'])}))
            self.assertThat(
                url,
                MatchesAll(
                    IsInstance(bytes),
                    Equals(b'http://example.com/store')))
            self.assertThat(
                data,
                MatchesAll(
                    IsInstance(bytes),
                    Equals(b'hello world')))
            return (200,
                    {b'Content-Type': b'application/json'},
                    json.dumps(
                        {u'links':
                         {u'self': u'http://example.com/stored_object'}}))
        resource = StringStubbingResource(_response_for)
        treq = StubTreq(resource)
        session = Session({u'store-content': u'http://example.com/store'},
                          treq.request)
        # XXX: This is not a real file object because `StubTreq` doesn't
        # implement support for that.
        fileobj = b'hello world'
        self.assertThat(
            session.store_content(fileobj, b'text/plain'),
            succeeded(
                Equals(u'http://example.com/stored_object')))

    def test_get_content(self):
        """
        Stream content.
        """
        def _response_for(method, url, params, headers, data):
            self.assertThat(method, Equals(b'GET'))
            self.assertThat(
                url,
                MatchesAll(
                    IsInstance(bytes),
                    Equals(b'http://example.com/some_content')))
            return (200,
                    {b'Content-Type': b'text/plain'},
                    b'hello world')
        resource = StringStubbingResource(_response_for)
        treq = StubTreq(resource)
        session = Session({}, treq.request)
        buf = StringIO()
        self.assertThat(
            session.get_content(b'http://example.com/some_content', buf.write),
            succeeded(
                Equals(b'text/plain')))
        self.assertThat(
            buf.getvalue(),
            Equals(b'hello world'))

    def test_perform_action(self):
        """
        Perform an action within a session.
        """
        payload = {u'links':
                   {u'result': u'https://example.com/result'}}
        action = {u'action': u'some_action',
                  u'parameters': {u'foo': 42}}

        def _response_for(method, url, params, headers, data):
            self.assertThat(method, Equals(b'POST'))
            self.assertThat(
                url,
                MatchesAll(
                    IsInstance(bytes),
                    Equals(b'http://example.com/perform')))
            self.assertThat(
                json.loads(data),
                Equals(action))
            return (200,
                    {b'Content-Type': b'application/json'},
                    json.dumps(payload))
        resource = StringStubbingResource(_response_for)
        treq = StubTreq(resource)
        session = Session({u'perform': u'http://example.com/perform'},
                          treq.request)
        self.assertThat(
            session.perform_action((action, lambda x: x)),
            succeeded(Equals(payload)))

    def test_delete(self):
        """
        Delete a session.
        """
        def _response_for(method, url, params, headers, data):
            self.assertThat(method, Equals(b'DELETE'))
            self.assertThat(
                url,
                MatchesAll(
                    IsInstance(bytes),
                    Equals(b'http://example.com/session')))
            return 200, {}, b''
        resource = StringStubbingResource(_response_for)
        treq = StubTreq(resource)
        session = Session({u'self': u'http://example.com/session'},
                          treq.request)
        self.assertThat(
            session.delete(),
            succeeded(Equals(b'')))


class CreateSessionTests(TestCase):
    """
    Tests for `txdocumint._client.create_session`.
    """
    def test_create_session(self):
        """
        Create a session.
        """
        def _response_for(method, url, params, headers, data):
            self.assertThat(method, Equals(b'POST'))
            self.assertThat(
                url,
                MatchesAll(
                    IsInstance(bytes),
                    Equals(b'http://example.com/sessions/')))
            return (
                200,
                {},
                json.dumps(
                    {u'links':
                     {u'self': u'http://example.com/sessions/1234'}}))
        resource = StringStubbingResource(_response_for)
        treq = StubTreq(resource)
        self.assertThat(
            create_session(u'http://example.com', treq.request),
            succeeded(
                MatchesStructure(
                    _session_info=Equals(
                        {u'self': u'http://example.com/sessions/1234'}))))


class GetSessionTests(TestCase):
    """
    Tests for `txdocumint._client.get_session`.
    """
    def test_get_session(self):
        """
        Create a session.
        """
        def _response_for(method, url, params, headers, data):
            self.assertThat(method, Equals(b'GET'))
            self.assertThat(
                url,
                MatchesAll(
                    IsInstance(bytes),
                    Equals(b'http://example.com/sessions/1234')))
            return (
                200,
                {},
                json.dumps(
                    {u'links':
                     {u'self': u'http://example.com/sessions/1234'}}))
        resource = StringStubbingResource(_response_for)
        treq = StubTreq(resource)
        self.assertThat(
            get_session(u'http://example.com/sessions/1234', treq.request),
            succeeded(
                MatchesStructure(
                    _session_info=Equals(
                        {u'self': u'http://example.com/sessions/1234'}))))
