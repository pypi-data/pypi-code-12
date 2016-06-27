import logging

import aiozmq
from aiozmq import rpc
from pyramid.view import view_config

from xbus.monitor.models.monitor import Event
from xbus.monitor.aiozmq_util import resolve_endpoint
from .util import get_list
from .util import get_record
from . import view_decorators


_MODEL = 'event'
log = logging.getLogger(__name__)


def _request_retry_event(front_url, login, password, loop, event_id):

    log.debug('Establishing RPC connection...')
    client = yield from rpc.connect_rpc(connect=front_url, loop=loop)
    log.debug('RPC connection OK')
    token = yield from client.call.login(login, password)
    log.debug('Got connection token: %s', token)

    retry_id = yield from client.call.retry_event(token, event_id)
    log.debug('Got the retry event id: %s', retry_id)

    yield from client.call.logout(token)
    log.debug('Logged out; terminating')

    client.close()
    log.debug('Done.')

    return retry_id


@view_config(
    http_cache=0, renderer='json', permission='read', request_method='POST',
    route_name='retry_event'
)
def retry_event(request):
    """Ask Xbus for a fresh new list of Xbus consumers.
    """
    record = get_record(request, _MODEL)

    front_url = request.registry.settings['xbus.broker.front.url']
    login = request.registry.settings['xbus.broker.front.login']
    password = request.registry.settings['xbus.broker.front.password']

    front_url = resolve_endpoint(front_url)

    # Send our request via 0mq to the Xbus front-end.
    zmq_loop = aiozmq.ZmqEventLoopPolicy().new_event_loop()
    consumers_future = _request_retry_event(
        front_url, login, password, zmq_loop, record.id
    )
    retry_id = zmq_loop.run_until_complete(consumers_future)
    log.debug('Got retry event ID: %s', retry_id)
    return record.as_dict()


@view_decorators.list(_MODEL)
def event_list(request):
    def wrapper(ev):
        """a small wrapper to add the envelope_id & role_login keys
        to the resulting records of the list
        """
        ret = ev.as_dict()
        ret['envelope_id'] = ev.envelope.id
        if ev.emitter:
            ret['emitter_login'] = ev.emitter.login
        else:
            ret['emitter_login'] = ""

        ret['type_name'] = ev.type.name
        return ret

    return get_list(Event, request.GET, record_wrapper=wrapper)


@view_decorators.read(_MODEL)
def event_read(request):
    record = get_record(request, _MODEL)
    ret = record.as_dict()

    ret.update({
        # Also include tracking items.
        'tracking': [tracker.id for tracker in record.tracking_list],

        # Also include inactive consumers.
        'consumer_inactivities': [
            inactivity.as_dict() for inactivity in record.consumer_inactivities
        ],

        # Also include user names for convenience.
        'user_name': (
            record.responsible.display_name if record.responsible else ''
        ),
    })

    return ret
