import aiozmq
from aiozmq import rpc
import asyncio
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_config

from xbus.monitor.aiozmq_util import resolve_endpoint


@asyncio.coroutine
def _coro_emitter(front_url, login, password, envelope_id, loop):
    """Send the replay request to Xbus.

    @return The envelope ID and logs.
    @rtype (envelope-ID, log list) tuple.
    """

    logs = []

    logs.append('Establishing RPC connection...')
    client = yield from rpc.connect_rpc(connect=front_url, loop=loop)
    logs.append('RPC connection OK')
    token = yield from client.call.login(login, password)
    logs.append('Got connection token: %s' % token)

    yield from client.call.replay_envelope(token, envelope_id)
    logs.append('Request to replay the envelope %s sent' % envelope_id)

    yield from client.call.logout(token)
    logs.append('Logged out; terminating')

    client.close()
    logs.append('Done.')

    return envelope_id, logs


@view_config(
    route_name='replay_envelope',
    renderer='json',
    http_cache=0,
)
def replay_envelope(request):
    """Attempt to send failed envelopes into Xbus again.
    """

    envelope_id = request.params.get('envelope_id')
    if not envelope_id:
        raise HTTPBadRequest(
            json_body={'error': 'No envelope selected'},
        )

    front_url = request.registry.settings['xbus.broker.front.url']
    login = request.registry.settings['xbus.broker.front.login']
    password = request.registry.settings['xbus.broker.front.password']

    front_url = resolve_endpoint(front_url)

    # Send our data via 0mq to the Xbus front-end.
    zmq_loop = aiozmq.ZmqEventLoopPolicy().new_event_loop()
    emitter = _coro_emitter(front_url, login, password, envelope_id, zmq_loop)
    envelope_id, logs = zmq_loop.run_until_complete(emitter)

    return {'envelope_id': envelope_id, 'logs': logs}
