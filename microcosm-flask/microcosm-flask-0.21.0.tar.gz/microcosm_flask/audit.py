"""
Audit log support for Flask routes.

"""
from collections import namedtuple
from functools import wraps
from logging import getLogger
from json import loads
from traceback import format_exc

from flask import current_app, g, request
from microcosm.api import defaults
from microcosm_flask.errors import (
    extract_context,
    extract_error_message,
    extract_status_code,
)


X_REQUEST = "X-Request"

AuditOptions = namedtuple("AuditOptions", [
    "include_request_body",
    "include_response_body",
    "include_header",
])


def include_header_matching_prefix(prefix):
    """
    Match all headers starting with prefix.

    """
    def include_header(header):
        return header.startswith(prefix)
    return include_header


def audit(func):
    """
    Record a Flask route function in the audit log.

    Generates a JSON record in the Flask log for every request.

    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        options = AuditOptions(
            include_request_body=True,
            include_response_body=True,
            include_header=include_header_matching_prefix(X_REQUEST),
        )
        return _audit_request(options, func, *args, **kwargs)

    return wrapper


def _audit_request(options, func, *args, **kwargs):
    """
    Run a request function under audit.

    """
    logger = getLogger("audit")

    response = None

    # always include these fields
    audit_dict = dict(
        operation=request.endpoint,
        func=func.__name__,
        method=request.method,
    )

    # include request body on debug (if any)
    if all((
        current_app.debug,
        options.include_request_body,
        request.get_json(force=True, silent=True),
        not g.get("hide_body"),
    )):
        audit_dict["request_body"] = request.get_json(force=True)

    # include headers (conditionally)
    audit_dict.update({
        header: value
        for header, value in request.headers.items()
        if options.include_header(header)
    })

    # process the request
    try:
        response = func(*args, **kwargs)
    except Exception as error:
        status_code = extract_status_code(error)
        success = 0 < status_code < 400
        audit_dict.update(
            success=success,
            message=extract_error_message(error)[:2048],
            context=extract_context(error),
            stack_trace=None if success else format_exc(limit=10),
            status_code=status_code,
        )
        raise
    else:
        body, status_code = parse_response(response)

        audit_dict.update(
            success=True,
            status_code=status_code,
        )

        # include response body on debug (if any)
        if all((
                current_app.debug,
                options.include_response_body,
                body,
                not g.get("hide_body"),
        )):
            try:
                audit_dict["response_body"] = loads(body)
            except (TypeError, ValueError):
                # not json
                audit_dict["response_body"] = body

        return response
    finally:
        # always log at INFO; we can't know whether a raised exception
        # is an error or expected behavior
        logger.info(audit_dict)


def parse_response(response):
    """
    Parse a Flask response into a body and status code.

    The returned value from a Flask view could be:
        * a tuple of (response, status) or (response, status, headers)
        * a Response object
        * a string
    """
    if isinstance(response, tuple) and len(response) > 1:
        return response[0], response[1]
    try:
        return response.data, response.status_code
    except AttributeError:
        return response, 200


@defaults(
    include_request_body=True,
    include_response_body=True,
    include_header_prefix=X_REQUEST,
)
def configure_audit_decorator(graph):
    """
    Configure the audit decorator.

    Example Usage:

        @graph.audit
        def login(username, password):
            ...
    """
    include_request_body = graph.config.audit.include_request_body
    include_response_body = graph.config.audit.include_response_body
    include_header_prefix = graph.config.audit.include_header_prefix

    def _audit(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            options = AuditOptions(
                include_request_body=include_request_body,
                include_response_body=include_response_body,
                include_header=include_header_matching_prefix(include_header_prefix),
            )
            return _audit_request(options, func, *args, **kwargs)

        return wrapper
    return _audit
