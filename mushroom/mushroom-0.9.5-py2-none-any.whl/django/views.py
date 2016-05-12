try:
    import simplejson as json
except ImportError:
    import json

from django.http import (HttpResponse, JsonResponse,
        HttpResponseNotFound, HttpResponseNotAllowed,
        HttpResponseForbidden, HttpResponseBadRequest)

from mushroom.http import WebSocketTransport, PollTransport
from mushroom.session import session_id_generator, Session, SessionList, \
        SessionHandler, SessionHandlerAdapter
from mushroom.rpc.dispatcher import MethodDispatcher, dummy_rpc_handler
from mushroom.rpc.middleware import MiddlewareStack, MiddlewareAwareRpcHandler

from .middlewares import CloseOldConnectionsMiddleware


class HttpResponseNotImplemented(HttpResponse):
    status_code = 501


class MushroomView(object):
    csrf_exempt = True

    def __init__(self, rpc_handler=None, session_handler=None):
        self.sessions = SessionList()
        self.sid_generator = session_id_generator()
        self.middlewares = MiddlewareStack([
           CloseOldConnectionsMiddleware()
        ])
        self.rpc_handler = MiddlewareAwareRpcHandler(
                rpc_handler or dummy_rpc_handler,
                self.middlewares)
        self.session_handler = session_handler or SessionHandler()

    def __call__(self, request, sid=None):
        if sid is None:
            response = self.bootstrap(request)
        else:
            try:
                session = self.sessions[sid]
            except KeyError:
                response = HttpResponseNotFound()
            else:
                response = session.transport.handle_http_request(request, session)
        if response is None:
            # Empty response to make Django happy
            response = HttpResponse()
        response['Access-Control-Allow-Origin'] = '*'
        return response

    def bootstrap(self, request):
        # Only allow POST requests for bootstrapping
        if request.method != 'POST':
            return HttpResponseNotAllowed(['POST'])
        try:
            data = json.loads(request.body)
        except ValueError:
            raise HttpResponseBadRequest('Invalid JSON')
        if not isinstance(data, dict):
            raise HttpResponseBadRequest('Invalid transport negotiation request')
        transports = data.get('transports', [])
        if not isinstance(transports, list):
            raise HttpBadRequest('Invalid transport negotiation request')
        for transport in data.get('transports', []):
            if transport == 'ws':
                return self.start_session(request, data, WebSocketTransport())
            if transport == 'poll':
                return self.start_session(request, data, PollTransport())
        # No suitable transport found
        return HttpResponseNotImplemented('No suitable transport found')

    def start_session(self, request, data, transport):
        session = Session(self.sid_generator.next(), transport, self.rpc_handler)
        if not self.session_handler.authenticate(session, data.get('auth', None)):
            return HttpResponseForbidden()
        self.sessions.add(session)
        self.session_handler.connect(session)
        @transport.state.subscribe
        def state_listener(state):
            if state == 'DISCONNECTED':
                self.sessions.remove(session)
                self.session_handler.disconnect(session)
        return JsonResponse(transport.get_handshake_data(request, session))


class SimpleMushroomView(MushroomView):

    def __init__(self, *args, **kwargs):
        if 'rpc_handler' not in kwargs:
            kwargs['rpc_handler'] = MethodDispatcher(self, 'rpc_')
        if 'session_handler' not in kwargs:
            kwargs['session_handler'] = SessionHandlerAdapter(self, 'session_')
        super(SimpleMushroomView, self).__init__(*args, **kwargs)
