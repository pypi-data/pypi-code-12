from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import sys
from io import BytesIO

from immunio.exceptions import ImmunioBlockedError, ImmunioOverrideResponse


HTTP_STATUS_CODES = {
    200: b"200 OK",
    201: b"201 Created",
    202: b"202 Accepted",
    204: b"204 No Content",

    301: b"301 Moved Permanently",
    302: b"302 Found",
    303: b"303 See Other",
    304: b"304 Not Modified",
    307: b"307 Temporary Redirect",

    400: b"400 Bad Request",
    401: b"401 Unauthorized",
    403: b"403 Forbidden",
    404: b"404 Not Found",
    405: b"405 Method Not Allowed",

    500: b"500 Internal Server Error",
}

class WsgiWrapper(object):
    """
    Accepts new requests and hands off to a new WsgiRequest object to handle.

    The WsgiRequest object takes care of calling Agent.http_request_finish() on
    completion.
    """
    def __init__(self, agent, app, request_uuid_header):
        self._agent = agent
        self._app = app
        self._request_uuid_header = request_uuid_header

    def __call__(self, environ, start_response):
        """
        Register new request with Agent then create a WsgiRequest object to
        handle it.
        """
        # If a request is already in progress for this thread, don't start a
        # new one.
        if self._agent.get_request_id() is not None:
            # Just call original app directly.
            return self._app(environ, start_response)

        request_id = self._agent.http_new_request()

        wsgi_request = WsgiRequest(self._agent,
            self._app, request_id, self._request_uuid_header)

        return wsgi_request.handle_request(environ, start_response)


class WsgiRequest(object):
    def __init__(self, agent, app, request_id, request_uuid_header):
        self._agent = agent
        self._app = app
        self._request_id = request_id
        self._request_uuid_header = request_uuid_header

        self._orig_start_response = None
        self._start_response_called = False
        self._wrapped_input = None
        self._output_gen = None
        self._inspect_response = False
        self._buffer_response = False

    def handle_request(self, environ, start_response):
        # Keep a reference to the original start_response
        self._orig_start_response = start_response

        # Extract request meta
        request_metadata = self._extract_request_meta(environ)

        # Guard call to original app
        try:
            # Report to engine
            hook_result = self._agent.run_hook(
                "wsgi",
                "http_request_start",
                request_metadata,
                request_id=self._request_id)

            inspect_body = hook_result.get("inspect_body", False)
            buffer_body = inspect_body and hook_result.get("buffer_body", False)

            # If the agent wants to see the request body, add our wrapper.
            if inspect_body:
                # Wrap the wsgi input object
                self.wrapped_input = WsgiInputWrapper(
                    self._request_id, self._agent, environ["wsgi.input"])
                environ["wsgi.input"] = self.wrapped_input

            if buffer_body:
                # Engine wants request body in single call, instead of
                # chunk by chunk
                self.wrapped_input.immunio_readall()

            # Call into original app
            result = self._app(environ, self._wrapped_start_response)
            self._output_gen = iter(result)

        except ImmunioBlockedError:
            # Block this request
            self._block_request()

        except ImmunioOverrideResponse as exc:
            # Block this request
            status, headers, body = exc.args
            self._block_request(status, headers, body)

        except Exception as exc:
            # Report error to engine
            self._agent.run_hook(
                "wsgi", "exception", {
                    "source": "WsgiWrapper.__call__",
                    "exception": str(exc),
                }, request_id=self._request_id)
            # This request is over
            self.close()
            # Re-raise to framework so it can clean up
            raise

        # This object also implements the iterator protocol
        return self

    def _wrapped_start_response(self, status, headers, exc_info=None):
        if self._request_uuid_header:
            headers.append((str(self._request_uuid_header), self._request_id))

        # `status` is a string like "404 NOT FOUND" but Lua expects a number.
        status_code = int(status[:3])

        # We can't pass actual exceptions into Lua, so stringify if present
        if exc_info:
            exc_info_str = "%s %s" % (exc_info[0].__name__, exc_info[1])
        else:
            exc_info_str = None

        hook_response = self._agent.run_hook(
            "wsgi", "http_response_start", {
                "status": status_code,
                "status_string": status,
                "headers": headers,
                "exc_info": exc_info_str,
            }, request_id=self._request_id)

        # Check if response body should be inspected
        self._inspect_response = hook_response.get("inspect_body", False)
        # Default to no buffering
        self._buffer_response = (self._inspect_response and
                                 hook_response.get("buffer_body", False))

        # If new headers are provided, use those instead
        if "headers" in hook_response:
            headers = hook_response["headers"]

        # Guard call to original start_response
        try:
            result = self._orig_start_response(status, headers, exc_info)
            self._start_response_called = True
        except Exception as exc:
            # Report error to engine
            self._agent.run_hook(
                "wsgi", "exception", {
                    "source": "start_response",
                    "exception": str(exc),
                }, request_id=self._request_id)
            # Re-raise to framework so it can clean up
            raise

        return result

    def _extract_request_meta(self, environ):
        request_metadata = {}
        request_metadata["protocol"] = environ.get("SERVER_PROTOCOL")
        request_metadata["scheme"] = environ.get("wsgi.url_scheme")
        request_metadata["uri"] = environ.get("REQUEST_URI")
        request_metadata["querystring"] = environ.get("QUERY_STRING")
        request_metadata["method"] = environ.get("REQUEST_METHOD")
        request_metadata["path"] = environ.get("PATH_INFO")
        request_metadata["socket_ip"] = environ.get("REMOTE_ADDR")
        request_metadata["socket_port"] = environ.get("REMOTE_PORT")

        # Extract HTTP Headers
        request_metadata["headers"] = {}
        for k, v in environ.items():
            # All headers start with HTTP_
            if k.startswith("HTTP_"):
                # Reformat as lowercase, dash separated
                header = k[5:].lower().replace('_', '-')
                request_metadata["headers"][header] = v

        return request_metadata

    def _block_request(self, status=b"403 Forbidden", headers=None,
                       body=b"Request blocked"):
        """
        Block an http request by returning a Forbidden response.
        """
        # TODO Make this look pretty

        # status may be provided as an integer. If so, convert to the
        # equivalent string status.
        if isinstance(status, int):
            status = HTTP_STATUS_CODES.get(status, str(status))
        # Status must also be a binary string
        if isinstance(status, unicode):
            status = status.encode("ascii")
        status = str(status)

        if headers is None:
            headers = [(b"Content-Type", b"text/plain")]
        # Iterate through each header to ensure it is binary
        for i, (name, value) in enumerate(headers):
            # Coerce the name to binary (header names must be ASCII)
            if isinstance(name, unicode):
                name = name.encode("ascii")
            name = str(name)
            # Coerce the value to binary (header values must be latin1)
            if isinstance(value, unicode):
                value = value.encode("latin1")
            value = str(value)
            # Save the coerced values
            headers[i] = name, value

        # Ensure body is a binary string
        if isinstance(body, unicode):
            body = body.encode("utf8")

        if self._request_uuid_header:
            headers.append((str(self._request_uuid_header), self._request_id))

        if self._start_response_called:
            # start_response has already been called. In order to cancel the
            # response now we need to call start_response with exc_info set.
            exc_info = sys.exc_info()
        else:
            self._start_response_called = True
            exc_info = None

        # `status` is a string like "404 NOT FOUND" but Lua expects a number.
        status_code = int(status[:3])

        # We can't pass actual exceptions into Lua, so stringify if present
        if exc_info:
            exc_info_str = "%s %s" % (exc_info[0].__name__, exc_info[1])
        else:
            exc_info_str = None

        # Manually send the response start hook
        self._agent.run_hook(
            "wsgi", "http_response_start", {
                "status": status_code,
                "status_string": status,
                "headers": headers,
                "exc_info": exc_info_str,
            }, request_id=self._request_id)

        self._orig_start_response(status, headers, exc_info)
        self._output_gen = iter([body])

    def __iter__(self):
        # Guard call to original output iterator
        try:
            buff = []
            # We have to start iterating before testing self._inspect_response
            # because start_response() might not be called until iteration
            # begins.
            for chunk in self._output_gen:
                if not self._inspect_response:
                    yield chunk
                elif self._buffer_response:
                    buff.append(chunk)
                    yield ""
                else:
                    # Report the outgoing chunk to the engine
                    self._agent.run_hook(
                        "wsgi", "http_response_body_chunk", {
                            "chunk": chunk,
                            "buffered": False,
                        }, request_id=self._request_id)

                    yield chunk
            if self._inspect_response and self._buffer_response:
                body = "".join(buff)

                # Report the buffered body to the engine
                self._agent.run_hook(
                    "wsgi", "http_response_body_chunk", {
                        "chunk": body,
                        "buffered": True,
                    }, request_id=self._request_id)
                yield body

        except ImmunioBlockedError:
            # Kill current iterator
            # TODO Should we finish iterating through it first?
            self._output_gen.close()
            # Block request (this call will replace the closed self._output_gen)
            self._block_request()
            for chunk in self._output_gen:
                yield chunk

        except ImmunioOverrideResponse as exc:
            # Kill current iterator
            # TODO Should we finish iterating through it first?
            self._output_gen.close()

            # Block request (this call will replace the closed self._output_gen)
            status, headers, body = exc.args
            self._block_request(status, headers, body)
            for chunk in self._output_gen:
                yield chunk

        except Exception as exc:
            # Report error to engine
            self._agent.run_hook(
                "wsgi", "exception", {
                    "source": "WsgiWrapper.__next__",
                    "exception": str(exc),
                }, request_id=self._request_id)
            # Re-raise to framework so it can clean up
            raise

    def close(self):
        # Guard call to original iterator close
        try:
            # If original generator has 'close' method, we need to call it
            if hasattr(self._output_gen, "close"):
                self._output_gen.close()
        except Exception as exc:
            # Report error to engine
            self._agent.run_hook(
                "wsgi", "exception", {
                    "source": "WsgiWrapper.close",
                    "exception": str(exc),
                }, request_id=self._request_id)
            # Re-raise to framework so it can clean up
            raise
        finally:
            # Report end to engine
            self._agent.http_request_finish(request_id=self._request_id)
            # Reset for next request
            self._request_id = None
            self._output_gen = None
            self._orig_start_response = None
            self._start_response_called = False

class WsgiInputWrapper(object):
    """
    Wraps a WSGI input stream. Reports chunks of the request body to
    the engine as they are read by the wrapped application.
    """
    def __init__(self, request_id, agent, original_input):
        self._request_id = request_id
        self._agent = agent
        self._input = original_input

    def report_chunk(self, chunk, buffered=False):
        self._agent.run_hook(
            "wsgi", "http_request_body_chunk", {
                "chunk": chunk,
                "buffered": buffered,
            }, request_id=self._request_id)

    def immunio_readall(self):
        """
        Special method used by the agent to read the entire input body
        for inspection. After reading, the original wsgi.input is replaced
        by a BytesIO version to maintain the file-like semantics for the
        protected application. No further request_body chunks will be
        reported to the engine for this request.
        """
        # Read entire input
        buff = self._input.read()

        self.report_chunk(buff, buffered=True)

        # Replace input with a BytesIO object
        self._input = BytesIO(buff)
        # Clear the _agent variable so no more chunks are reported
        self._agent = None
        return buff

    def read(self, size=-1):
        """
        Reads a specified number of bytes from input. size defaults to -1
        which reads the entire input.
        """
        chunk = self._input.read(size)
        if self._agent:
            self.report_chunk(chunk)
        return chunk

    def readline(self):
        chunk = self._input.readline()
        # Don't report empty last chunk to the Agent. It just indicates EOF.
        if chunk == "":
            return chunk
        if self._agent:
            self.report_chunk(chunk)
        return chunk

    def readlines(self, hint=None):
        lines = self._input.readlines(hint)
        if self._agent:
            chunk = "".join(lines)
            self.report_chunk(chunk)
        return lines

    def __iter__(self):
        for chunk in self._input:
            if self._agent:
                self.report_chunk(chunk)
            yield chunk
