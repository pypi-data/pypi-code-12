"""Deal with Xbus consumers.

In particular, save whether they provide data clearing and the database they
use.
"""

import aiozmq
from aiozmq import rpc
import asyncio
from copy import copy
import logging
from pyramid.httpexceptions import HTTPBadRequest
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
import uuid
from zope.sqlalchemy import ZopeTransactionExtension

from xbus.monitor.aiozmq_util import resolve_endpoint


log = logging.getLogger(__name__)


def _make_session(db_url):
    """Build an SQLAlchemy session object from a database URL."""
    return scoped_session(sessionmaker(
        bind=create_engine(db_url),
        extension=ZopeTransactionExtension(),
    ))


# Store consumers and data clearing database URLs and 2 different arrays to
# make sure no database information is inadvertently leaked.

_consumers = []

# {consumer ID: SQLAlchemy session object to the data clearing database}
_consumer_clearing_sessions = {}


def get_consumers():
    """Get the cached list of consumers. To retrieve an up-to-date list, call
    "refresh_consumers" first.

    :rtype: List of dicts.
    """

    global _consumers
    return copy(_consumers)


def get_consumer_clearing_session(consumer_id):
    """Get an SQLAlchemy session object bound to the data clearing database
    provided by the specified consumer.

    :param consumer_id: UID of the Xbus consumer.
    :type consumer_id: String.

    :raise HTTPBadRequest.

    :rtype: sqlalchemy.orm.scoped_session.
    """

    if consumer_id:
        session = _consumer_clearing_sessions.get(consumer_id)
        if session:
            return session

    raise HTTPBadRequest(json_body={
        'error': 'Data clearing information missing.',
    })


@asyncio.coroutine
def _request_consumers(front_url, login, password, loop):
    """Ask Xbus for the list of consumers.

    :return: List of 2-element tuples (metadata dict, feature dict).
    """

    log.debug('Establishing RPC connection...')
    client = yield from rpc.connect_rpc(connect=front_url, loop=loop)
    log.debug('RPC connection OK')
    token = yield from client.call.login(login, password)
    log.debug('Got connection token: %s', token)

    consumers = yield from client.call.get_consumers(token)
    log.debug('Got the consumer list: %s', consumers)

    yield from client.call.logout(token)
    log.debug('Logged out; terminating')

    client.close()
    log.debug('Done.')

    return consumers


def refresh_consumers(request):
    """Ask Xbus for a fresh new list of Xbus consumers.
    """

    # Global arrays we are going to refresh.
    global _consumers
    global _consumer_clearing_sessions

    front_url = request.registry.settings['xbus.broker.front.url']
    login = request.registry.settings['xbus.broker.front.login']
    password = request.registry.settings['xbus.broker.front.password']

    front_url = resolve_endpoint(front_url)

    # Send our request via 0mq to the Xbus front-end.
    zmq_loop = aiozmq.ZmqEventLoopPolicy().new_event_loop()
    consumers_future = _request_consumers(front_url, login, password, zmq_loop)
    consumers_data = zmq_loop.run_until_complete(consumers_future)
    log.debug('Got consumers data: %s', consumers_data)

    # consumers_data: List of 2-element tuples (metadata dict, feature dict).
    # feature dict: {feature name: feature data}
    # data clearing feature data: 2-element tuple (feature support, DB URL).

    # Fill the consumer cache.
    _consumers = [
        {
            'clearing': bool(consumer_info[1]['clearing'][0]),
            'id': uuid.uuid4().hex,  # Just make one on-the-fly.
            'name': consumer_info[0]['name'],
        }
        for consumer_info in consumers_data
        if 'name' in consumer_info[0]  # Ignore wrongly registered ones.
    ]

    # Refresh the cache of consumers with data clearing.
    _consumer_clearing_sessions = {
        _consumers[consumer_index]['id']: (
            _make_session(consumer_info[1]['clearing'][1])
        )
        for consumer_index, consumer_info in enumerate(consumers_data)
        if consumer_info[1]['clearing'][0]
    }
