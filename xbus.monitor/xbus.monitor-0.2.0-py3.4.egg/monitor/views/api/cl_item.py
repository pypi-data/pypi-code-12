import aiozmq
from aiozmq import rpc
import asyncio
import logging
import msgpack
from pyramid.httpexceptions import HTTPNotImplemented
import transaction

from xbus.monitor.aiozmq_util import resolve_endpoint
from xbus.monitor.models.data_clearing import get_session
from xbus.monitor.models.data_clearing import Item
from xbus.monitor.models.monitor import DBSession
from xbus.monitor.models.monitor import EventType

from .util import get_list
from . import view_decorators


_MODEL = 'cl_item'


# Name of the event type with the "immediate reply" flag set to use when
# issuing Xbus requests related to data clearing items.
DATA_CLEARING_EVENT_TYPE = 'data_clearing'


log = logging.getLogger(__name__)


@view_decorators.list(_MODEL)
def cl_item_list(request):

    # TODO Remove the custom record wrapper when clients represent
    # relationships better (for now, we just include the data they are going
    # to need in the result list).

    def record_wrapper(record):
        """Include type names."""
        ret = record.as_dict()
        ret['type_name'] = record.type.display_name
        return ret

    return get_list(
        Item, request.GET, sqla_session=get_session(request),
        record_wrapper=record_wrapper,
    )


@view_decorators.create(_MODEL)
def cl_item_create(request):
    raise HTTPNotImplemented(json_body={})


@view_decorators.read(_MODEL)
def cl_item_read(request):
    """Send a request, via Xbus, to the consumer providing data clearing for
    information about the item.
    """

    res = _send_item_request(request, {
        'action': 'get_item_details',
        'item_id': request.context.record_id,
    })
    if res[0] and len(res[1]) > 0:
        return res[1][0]
    else:
        return res


@view_decorators.update(_MODEL)
def cl_item_update(request):
    raise HTTPNotImplemented(json_body={})


@view_decorators.delete(_MODEL)
def cl_item_delete(request):
    raise HTTPNotImplemented(json_body={})


@view_decorators.patch(_MODEL)
def cl_item_patch(request):
    """Send a request, via Xbus, to the consumer providing data clearing, to
    ask for the item to be "cleared" and for information about the item.
    """

    out_data = request.json_body.get('out_data')
    if out_data:
        return _send_item_request(request, {
            'action': 'clear_item',
            'item_id': request.context.record_id,
            'values': out_data
        })

    return False


def _ensure_item_clearing_event_type(request):
    """Ensure an event type used when issuing Xbus requests related to data
    clearing items exists; otherwise, create it. It will have the "immediate
    reply" flag set.
    """

    session = DBSession()

    if session.query(EventType).filter(
        EventType.name == DATA_CLEARING_EVENT_TYPE
    ).count() == 0:
        # Create an event type.
        event_type = EventType()
        event_type.description = (
            'Event type to carry Xbus requests related to data clearing items.'
        )
        event_type.immediate_reply = True
        event_type.name = DATA_CLEARING_EVENT_TYPE
        session.add(event_type)
        transaction.commit()


def _send_item_request(request, data):
    """Send a data clearing item request to Xbus.
    :param data: Data (of any type) to send to the Xbus consumer.
    :return: The result of an "end_event" Xbus API call.
    """

    _ensure_item_clearing_event_type(request)

    front_url = request.registry.settings['xbus.broker.front.url']
    login = request.registry.settings['xbus.broker.front.login']
    password = request.registry.settings['xbus.broker.front.password']

    front_url = resolve_endpoint(front_url)

    # Send our request via 0mq to the Xbus front-end.
    zmq_loop = aiozmq.ZmqEventLoopPolicy().new_event_loop()
    future = _send_item_request_(front_url, login, password, data, zmq_loop)
    return zmq_loop.run_until_complete(future)


@asyncio.coroutine
def _send_item_request_(front_url, login, password, data, loop):
    """Send a data clearing item request to Xbus.
    :param data: Data (of any type) to send to the Xbus consumer.
    :return: The result of an "end_event" Xbus API call.
    """

    log.debug('Establishing RPC connection...')
    client = yield from rpc.connect_rpc(connect=front_url, loop=loop)
    log.debug('RPC connection OK')
    token = yield from client.call.login(login, password)
    log.debug('Got connection token: %s', token)

    envelope_id = yield from client.call.start_envelope(token)
    log.debug('Envelope created: %s', envelope_id)

    event_id = yield from client.call.start_event(
        token, envelope_id, DATA_CLEARING_EVENT_TYPE, 0
    )
    log.debug('Event created: %s', event_id)

    yield from client.call.send_item(
        token, envelope_id, event_id,
        msgpack.packb(data, use_bin_type=True),
    )
    log.debug('Data sent (event ID: %s)', event_id)

    ret = yield from client.call.end_event(token, envelope_id, event_id)
    log.debug('Event %s done: return value: %s', event_id, ret)

    yield from client.call.end_envelope(token, envelope_id)
    log.debug('Envelope %s closed', envelope_id)

    yield from client.call.logout(token)
    log.debug('Logged out; terminating')

    client.close()
    log.debug('Done.')

    return ret
