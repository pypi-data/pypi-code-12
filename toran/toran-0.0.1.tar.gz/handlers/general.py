from util import transport as util_transport
import json
import traceback


def handle(environ, start_response, transport, request_id, logger, resource, action, version):
    """
    Handles any request from a resource and action pair, It will send the transport to the 'resource_name' with
    the routing.default key of resource_name.action.process
    :param environ: Holds all environment values
    :param start_response: Callback to reply to requester call it socket
    :param transport: transport packaged message
    :param request_id: generated request id
    :param logger: logger object
    :param resource: Resource to act upon
    :param action: Action to exert on the resource
    :param version: Version of the action
    :return:
    """
    response_type = '200 OK'
    start_response(response_type, [('Content-Type', 'application/json')])
    logger.log_http_response(environ, '200', request_id)

    result = json.dumps(transport)
    return [result]


def access_refused(environ, start_response, type, transport, error):
    """Called if not authorized for action"""
    result = util_transport.prepare_error(
        transport=transport,
        message=str(error),
        error='Access refused of type: ' + type + '',
        code='access_refused',
        status_code="401"
    )
    start_response('401 UNAUTHORIZED', [('Content-Type', 'application/json')])
    return [json.dumps(result)]


def access_failed(environ, start_response, type, transport, error):
    """Called if not authorized for action"""
    result = util_transport.prepare_error(
        transport=transport,
        message=str(error),
        error='Access unauthorized of type: ' + type + '',
        code='invalid_token',
        status_code="401"
    )
    start_response('401 UNAUTHORIZED', [('Content-Type', 'application/json')])
    return [json.dumps(result)]


def unauthorized(environ, start_response, transport):
    start_response('401 UNAUTHORIZED', [('Content-Type', 'application/json')])
    return [transport]


def url_not_found(environ, start_response, transport):
    """Called if no URL matches."""
    result = util_transport.prepare_error(
        transport=transport,
        message='Service Not Found',
        error='',
        code='endpoint_not_found',
        status_code="404"
    )
    start_response('404 NOT FOUND', [('Content-Type', 'application/json')])
    return [json.dumps(result)]


def bad_method(environ, start_response, transport):
    """Called if no URL matches."""
    result = util_transport.prepare_error(
        transport=transport,
        message='Method not allowed',
        error='',
        code='bad_method',
        status_code="405"
    )
    start_response('405 METHOD NOT ALLOWED', [('Content-Type', 'application/json')])
    return [json.dumps(result)]


def resource_not_found(environ, start_response, transport):
    """Called if no URL matches."""
    start_response('404 NOT FOUND', [('Content-Type', 'application/json')])
    return [transport]


def client_bad_request(environ, start_response, transport):
    """Called if no URL matches."""
    start_response('400 BAD REQUEST', [('Content-Type', 'application/json')])
    return [transport]


def bad_request(environ, start_response, transport, error, params=None):
    """Called if no URL matches."""
    if params is None:
        join_params = []
        code = 'bad_request'
    else:
        join_params = params
        code = 'missing_param'
    result = util_transport.prepare_error(
        transport=transport,
        message='Bad request ' + ", ".join(join_params),
        error=error,
        code=code,
        status_code="400"
    )
    start_response('400 BAD REQUEST', [('Content-Type', 'application/json')])
    return [json.dumps(result)]


def rpc_not_found(environ, start_response, name, transport, error, logger):
    """Called if no rpc queue matches."""
    logger.log_gateway_error(
        message='Exchange ' + name + ' Not Found',
        detail=str(error),
        request_id='',
        environ=environ
    )
    result = util_transport.prepare_error(
        transport=transport,
        message='Exchange ' + name + ' Not Found',
        error=error,
        code='not_found',
        status_code="500"
    )
    start_response('500 INTERNAL ERROR', [('Content-Type', 'application/json')])
    return [json.dumps(result)]


def gateway_timeout(environ, start_response, name, transport, error, logger):
    """Called if no rpc queue matches."""
    logger.log_gateway_error(
        message='Exchange ' + name + ' Not Found',
        detail=str(error),
        request_id='',
        environ=environ
    )
    result = util_transport.prepare_error(
        transport=transport,
        message='Could not connect to Broker',
        error='',
        code='internal_error',
        status_code="504"
    )
    start_response('504 GATEWAY TIMEOUT', [('Content-Type', 'application/json')])
    return [json.dumps(result)]


def service_unavailable(environ, start_response, transport, logger):
    """Called if no URL matches."""
    try:
        request_id = transport["@id"]
        main_error = transport['error']['errors'][0]
        status_code = transport['error']['status']
    except (Exception, KeyError):
        # print 'transport is ' + str(transport)
        loaded = json.loads(str(transport))
        request_id = loaded["@id"]
        main_error = loaded['error']['errors'][0]
        status_code = loaded['error']['status']
        transport = loaded

    logger.log_gateway_error(
        message=str(main_error['detail']),
        detail=main_error['title'],
        request_id=request_id,
        environ=environ
    )

    result = util_transport.prepare_error(
        transport=transport,
        message=str(main_error['detail']),
        error=Exception(main_error['title']),
        code='internal_error',
        status_code=status_code
    )
    start_response('503 SERVICE UNAVAILABLE', [('Content-Type', 'application/json')])
    return [json.dumps(result)]


def internal_error(environ, start_response, error, transport, logger, request_id):
    """Called if exception found."""
    trace_message = str(traceback.format_exc())

    logger.log_gateway_error(
        message='Gateway Fatal Error',
        detail=trace_message.replace('\n', ' ').replace('\r', ''),
        request_id=request_id,
        environ=environ
    )
    result = util_transport.prepare_error(
        transport=transport,
        message=error,
        error=str(error),
        code='internal_error',
        status_code="500"
    )

    start_response('500 INTERNAL ERROR', [('Content-Type', 'application/json')])
    return [json.dumps(result)]


def request_timeout(environ, start_response, transport, error, logger, request_id):
    """Returned when the rpc times out """
    logger.log_gateway_error(
        message='Gateway Timeout Error',
        detail=str(error),
        request_id=request_id,
        environ=environ
    )
    result = util_transport.prepare_error(
        transport=transport,
        message='rpc could not complete',
        error=error,
        code='request_timeout',
        status_code="408",
        request_id=request_id
    )
    start_response('408 REQUEST TIMEOUT', [('Content-Type', 'application/json')])
    return [json.dumps(result)]


def return_empty_response(environ, start_response, transport):
    start_response('204 NO CONTENT', [('Content-Type', 'application/json')])
    return []


def handle_dry_run(environ, start_response, transport):
    start_response('299 STABLE', [('Content-Type', 'application/json')])
    return [transport]


def return_conflict_response(environ, start_response, transport):
    try:
        loaded = json.loads(str(transport))
        del(loaded['error'])
        loaded = json.dumps(loaded)
    except (Exception, NameError, ValueError):
        loaded = transport
        pass
    start_response('409 CONFLICT', [('Content-Type', 'application/json')])
    return [loaded]
