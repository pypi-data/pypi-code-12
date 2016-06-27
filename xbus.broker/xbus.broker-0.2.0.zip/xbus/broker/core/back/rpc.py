# -*- encoding: utf-8 -*-

import asyncio
import json
import aiozmq
from aiozmq import rpc
from collections import defaultdict
import logging

from xbus.broker.model import validate_password

from xbus.broker.core.db import DatabaseUtils
from xbus.broker.core.base import XbusBrokerBase
from xbus.broker.core.back.envelope import Envelope
from xbus.broker.core.back.recipient import Recipient
from xbus.broker.core.features import RecipientFeature

__author__ = 'jgavrel'


log = logging.getLogger(__name__)


class BrokerBackError(Exception):
    pass


class XbusBrokerBack(XbusBrokerBase):
    """the XbusBrokerBack is in charge of handling workers and consumers
    on a specific 0mq socket.

    Before you can call any useful methods on the XbusBrokerBack you'll need
    to obtain a token through the login() call. Once you have a token you will
    need to give it to all subsequent calls.

    If you have finished your session you SHOULD call the logout() method.
    This is important in order to protect yourself. Calling logout will
    invalidate the token and make sure no one can reuse it ever.
    """

    def __init__(self, db, frontsocket, socket, loop=None):
        super(XbusBrokerBack, self).__init__(db, loop=loop)

        self.frontsocket = frontsocket
        self.socket = socket

        # {service ID: set(role ID)}
        self.consumers = defaultdict(set)
        # {service ID: {role ID: token}}
        self.active_roles = defaultdict(dict)

        # Registered recipients, with their metadata and a connection.
        # {role ID: Recipient instance}
        self.recipients = {}

        # {event type ID: set(waiting event IDs)
        self.wait_events = defaultdict(set)
        # {event type ID: set(absent services IDs)
        self.wait_services = defaultdict(set)
        # {service ID: set(event type IDs)
        self.wait_services_inv = defaultdict(set)

        self.envelopes = {}

        # {replaying event ID: set(target consumer IDs)
        self.replay_part = defaultdict(set)
        # set(replaying event IDs)
        self.replay_wait = set()

        # TODO: configurable timeouts (config file or database?)
        self.start_ping_timeout = 3

    @asyncio.coroutine
    def retry_event(
        self, old_event_id: str, targets: list=None, future_event_id=None
    ):

        event_data = yield from self.db.read_event(old_event_id)
        type_id, start_date, nb_items, old_state, origin_id = event_data
        origin_event_id = origin_id if origin_id else old_event_id
        if old_state == 'wait':
            log_inactive = True
        elif old_state == 'part':
            log_inactive = False
        elif old_state == 'stop':
            log_inactive = True
        else:
            return False, 'Invalid retried event state {}.'.format(old_state)

        type_name, immediate = yield from self.db.read_event_type(type_id)
        if immediate:
            return False, 'Cannot retry an event with immediate reply.'

        items = yield from self.db.read_items(origin_event_id)

        envelope_id = self.new_envelope()
        yield from self.start_envelope(envelope_id)
        yield from self.db.log_new_envelope(envelope_id, None)

        event_id = self.new_event()
        code, msg, inactive_ids = yield from self.start_event(
            envelope_id, event_id, type_id, type_name, targets=targets,
            log_inactive=log_inactive
        )
        if code != 0:
            yield from self.cancel_envelope(envelope_id)
            return False, msg
        # Do not log the retry event unless it can actually start.
        yield from self.db.log_new_event(
            event_id, envelope_id, None, type_id, nb_items, old_event_id,
        )
        if future_event_id is not None:
            future_event_id.set_result(event_id)

        item_count = 0
        for index, data in items:
            item_count += 1
            yield from self.send_item(envelope_id, event_id, index, data)

        if item_count != nb_items:
            yield from self.cancel_envelope(envelope_id)
            return False, 'Item number mismatch'
        else:
            yield from self.db.update_event_sent_items_count(
                event_id, nb_items,
            )

        end_res = yield from self.end_event(
            envelope_id, event_id, nb_items, False
        )
        if not end_res['success']:
            yield from self.cancel_envelope(envelope_id)
            return False, 'end_event failed'
        else:
            yield from self.db.update_event_state_exec(event_id)

        yield from self.db.update_envelope_state_received(envelope_id)
        res = yield from self.end_envelope(envelope_id, wait_end=True)
        if res.get('success', False) is False:
            return False, 'retry execution failed'

        if not log_inactive:
            active_ids = list(set(targets) - set(inactive_ids))
            yield from self.db.update_active_consumers(
                old_event_id, active_ids, event_id
            )
        else:
            yield from self.db.update_retry_event_id(old_event_id, event_id)
            wait_events = self.wait_events[type_id]
            wait_events.discard(old_event_id)
            if not wait_events:
                wait_services = self.wait_services[type_id]
                for service_id in wait_services:
                    self.wait_services_inv[service_id].discard(type_id)
                wait_services.clear()

        return True, event_id

    @asyncio.coroutine
    def register_on_front(self):
        """This method tries to register the backend on the frontend. If
        everything goes well it should return True.
        If we have an error during the registration process this method will
        raise a :class:`BrokerBackError`

        :return:
         True

        :raises:
         :class:`BrokerBackError`
        """
        yield from self.init_consumers()
        yield from self.init_waiting_events()
        client = yield from aiozmq.rpc.connect_rpc(connect=self.frontsocket)
        result = yield from client.call.register_backend(self.socket)
        if result is None:
            # yeeeks we got an error here ...
            # let's do something stupid and b0rk out
            raise BrokerBackError('Cannot register ourselves on the front')
        else:
            return True

    @rpc.method
    @asyncio.coroutine
    def login(self, login: str, password: str) -> str:
        """Before doing anything useful you'll need to login into the broker
        we a login/password. If the authentication phase is ok you'll get a
        token that must be provided during other method calls.

        :param login:
         the login you want to authenticate against

        :param password:
         the password that must match your login

        :return:
         a unicode token that can be used during the session
        """

        role_row = yield from self.db.find_role_by_login(login)
        role_id, role_pwd, service_id = role_row
        if role_id and validate_password(password, role_pwd):
            token = self.new_token()
            info = {'id': role_id, 'login': login, 'service_id': service_id}
            info_json = json.dumps(info)
            yield from self.save_key(token, info_json)
            log.info('Successful recipient login from %s - token: %s' % (
                login, token
            ))

        else:
            token = ""
            log.info('Failed recipient login from %s' % login)

        return token

    @rpc.method
    @asyncio.coroutine
    def logout(self, token: str) -> bool:
        """When you are done using the broker you should call this method to
        make sure your token is destroyed and no one can reuse it

        :param token:
         the token you want to invalidate

        :return:
         True if successful, False otherwise
        """

        log.info('Recipient logout request with the token: %s' % token)

        token_json = yield from self.get_key_info(token)
        try:
            token_data = json.loads(token_json)
        except (TypeError, ValueError):
            # Invalid token.
            return False

        role_id = token_data.get('id', None)
        service_id = token_data.get('service_id', None)

        service_roles = self.active_roles[service_id]
        if service_roles.get(role_id) == token:
            del service_roles[role_id]
            try:
                del self.recipients[role_id]
            except KeyError:
                pass
        res = yield from self.destroy_key(token)
        return res

    @asyncio.coroutine
    def check_partial_events(self, role_id: str) -> bool:
        event_ids = yield from self.db.check_consumer_inactivity(role_id)
        for eid in event_ids:
            replay_roles = self.replay_part[eid]
            if role_id in replay_roles:
                continue
            replay_roles.add(role_id)
            try:
                yield from self.retry_event(eid, [role_id])
            finally:
                replay_roles.remove(role_id)

    @asyncio.coroutine
    def check_waiting_events(self, service_id: str) -> bool:
        type_ids = self.wait_services_inv[service_id]
        event_ids = list(
            eid for tid in type_ids for eid in self.wait_events[tid]
        )
        for eid in event_ids:
            if eid in self.replay_wait:
                continue
            self.replay_wait.add(eid)
            try:
                yield from self.retry_event(eid)
            finally:
                self.replay_wait.remove(eid)

    @rpc.method
    @asyncio.coroutine
    def register_node(self, token: str, uri: str) -> bool:
        """Register a node (worker / consumer) on the broker. This node will be
        known by the broker and called when some work is available.

        The node must implement the API described in the "Xbus node API"
        section of the documentation.

        :param token:
         the token your worker previously obtained by using the
         :meth:`XbusBrokerBack.login` method

        :param uri:
         String representing the socket address on which the node is available.
         The node is effectivly a server and must answer on the designated
         socket when the broker calls elements of the node API.

        :return:
         True if the registration went well and the broker now knows the node.
         False if something went wrong during registration and the broker
         does not recognize the node as being part of its active graph.
        """

        log.info('Registering a recipient with the token: %s' % token)

        # Check the token.
        token_json = yield from self.get_key_info(token)
        try:
            token_data = json.loads(token_json)
        except (TypeError, ValueError):
            # Invalid token.
            log.info('Recipient reg for %s: Invalid token' % token)
            return False
        else:
            # Find the role the token was registered for.
            role_id = token_data.get('id', None)
            service_id = token_data.get('service_id', None)
            if role_id is None:
                log.info('Recipient reg for %s: No role found' % token)
                return False

        # Fill recipient information.
        recipient = Recipient(token, role_id)
        yield from recipient.connect(uri)
        self.recipients[role_id] = recipient

        if self.wait_services_inv[service_id]:
            asyncio.async(
                self.check_waiting_events(service_id), loop=self.loop
            )
        if service_id in self.consumers.keys():
            asyncio.async(self.check_partial_events(role_id), loop=self.loop)

        # Mark the node as active.
        res = yield from self.ready(token)
        log.info('Recipient reg for %s: Ready: %s' % (token, res))
        return res

    @rpc.method
    @asyncio.coroutine
    def ready(self, token: str) -> bool:
        """Signal that a node (worker / consumer) is "ready".

        :param token:
         the token your worker previously obtained by using the
         :meth:`XbusBrokerBack.login` method
        """

        # TODO Improve the above comment to explain what is "ready".

        # Check the token.
        token_json = yield from self.get_key_info(token)
        try:
            token_data = json.loads(token_json)
        except (TypeError, ValueError):
            # Invalid token.
            return False

        # Find the role and service the token was registered for.
        role_id = token_data.get('id', None)
        service_id = token_data.get('service_id', None)
        if role_id is None or service_id is None:
            return False
        if role_id not in self.recipients:
            return False

        # Add the role to the list of active roles of the service.
        service_roles = self.active_roles[service_id]
        service_roles[role_id] = token

        return True

    @rpc.method
    @asyncio.coroutine
    def start_envelope(self, envelope_id: str) -> str:
        """Start a new envelop giving its envelop UUID.
        This is just a way to register the envelop existance with the broker
        backend. This permits to cancel this envelop further down the road.

        :param envelope_id:
         the UUID of the envelop you want to start
         expressed as a string

        :return:
         the envelop id you just started
        """
        self.envelopes[envelope_id] = Envelope(
            envelope_id, self.db, self.redis_pool, self.loop
        )
        return envelope_id

    @rpc.method
    @asyncio.coroutine
    def start_event(
            self, envelope_id: str, event_id: str, type_id: str,
            type_name: str, *, targets: list=None, log_inactive: bool=True
    ) -> tuple:
        """Begin a new event inside an envelope opened against this broker
        backend.

        :param envelope_id:
         the previously opened envelope UUID to which this event is attached.
         If the envelope is unknown to the broker backend this will return an
         error code.

        :param event_id:
         the UUID representing the new event. If the UUID is already known to
         the broker backend (ie: already in use at the moment. We won't verify
         in the whole event history) then this method will return an error code
         instead of processing your data.

        :param type_id:
         the internal UUID that corresponds to the type of the started event.

        :param type_name:
         the name of the type of the started event.

        :param targets:
         the list of consumer ids you want to specifically target with this
         event. It is optional and in most normal cases (ie: first time the
         frontend sends an event) it will not be used. The rationale behind
         this is that you may have situations when a specific node failed
         and the bus knows that it could not try to send data to the
         consumers that were situated after the failed node.
         In this particular situation the bus will mark the consumers as "not
         properly finished" and stamp the envelope as "not properly finished".
         When a human operator sees this situation in the management console
         they will be able to correct the defect and ask for a replay of the
         failed branches.
         This will re-emit the event through a subset of the network composed
         of the branches that lead to "not properly finished" consumers.

        :return:
         a 3 tuple with the success code, a message, and if successful,
         the ids of the inactive consumer roles:

           - success -> (0, '<event_id>', [inactive_consumer_role_ids])
           - failure -> (1, "No such envelope : 87654345678", None)
        """
        envelope = self.envelopes.get(envelope_id, None)

        errors = []
        if envelope is None:
            errors.append("No such envelope : {}".format(envelope_id))

        elif event_id in envelope.events:
            errors.append("Event already started: {}".format(event_id))

        if errors:
            res = (1, "\n".join(errors), None)
            return res

        new_event = envelope.new_event(event_id, type_name, type_id)
        rows = yield from self.db.get_event_tree(type_id)
        any_active_consumer = False
        inactive = []
        target_set = set(targets) if targets is not None else None
        consumer_services = []

        while rows:
            row_by_node = {}
            node_ping = []
            for row in rows:
                node_id, service_id, is_start, child_ids = row
                row_by_node[node_id] = row
                service_roles = self.active_roles[service_id]

                if child_ids:  # Workers
                    if not service_roles:
                        self.wait_events[type_id].add(event_id)
                        self.wait_services[type_id].add(service_id)
                        self.wait_services_inv[service_id].add(type_id)
                        return False, 'No worker available', None
                    role_id, token = service_roles.popitem()
                    recipient = self.recipients[role_id]
                    ping = new_event.new_worker(
                        node_id, recipient, child_ids, is_start
                    )
                    node_ping.append(ping)

                else:  # Consumers
                    consumer_services.append(service_id)
                    role_ids = self.consumers[service_id]
                    if targets is not None:
                        role_ids = role_ids & target_set
                    active_ids = {
                        rid for rid in self.recipients if rid in role_ids
                    }
                    recipients = [self.recipients[r] for r in active_ids]
                    inactive_ids = role_ids - active_ids
                    inactive.extend(
                        (node_id, role_id, False) for role_id in inactive_ids
                    )
                    ping = new_event.new_consumer(
                        node_id, recipients, is_start
                    )
                    node_ping.append(ping)

            rows = []
            done, pending = yield from asyncio.wait(
                node_ping, timeout=self.start_ping_timeout, loop=self.loop
            )
            if not any_active_consumer:
                for ping in done:
                    node_id, node, unavailable = yield from ping
                    if node.is_consumer() and node.role_ids:
                        any_active_consumer = True

            for ping in pending:
                ping.cancel()
                node_id, node, unavailable = yield from ping
                # TODO: disable unavailable workers/consumers?
                if node is None:
                    rows.append(row_by_node[node_id])

                elif node.is_consumer():
                    inactive.extend(
                        (node_id, r.role_id, True) for r in unavailable
                    )

        if not any_active_consumer:
            self.wait_events[type_id].add(event_id)
            self.wait_services[type_id] |= set(consumer_services)
            for consumer_service_id in consumer_services:
                self.wait_services_inv[consumer_service_id].add(type_id)
            return 1, "No active consumer", None

        if inactive and log_inactive:
            yield from self.db.log_inactive_consumers(event_id, inactive)

        for node in new_event.start:
            if node.is_consumer():
                coro = envelope.consumer_start_event
            else:
                coro = envelope.worker_start_event
            asyncio.async(coro(node, new_event), loop=self.loop)

        yield from self.db.update_event_state_exec(event_id)
        inactive_ids = list(zip(*inactive))[1] if inactive else []
        res = (0, "{}".format(event_id), inactive_ids)

        return res

    @rpc.method
    @asyncio.coroutine
    def send_item(
        self, envelope_id: str, event_id: str, index: int, data: bytes
    ) -> tuple:
        """Send an item to the XBUS network.

        :param event_id:
         event UUID previously opened onto which this item will be sent

        :param index:
         the item index number.

        :param data:
         the raw data of the item. This data will not be opened or
         interpreted by the bus itself, but forwarded to all the workers and
         ultimately the consumers of the graph.

        :return:
         to be defined
        """
        # if we have an event_id this means we already have a precomputed graph
        # for this event... so lets send the item to the corresponding nodes

        envelope = self.envelopes.get(envelope_id)
        if not envelope:
            res = (1, 'No such envelope')
            return res

        event = envelope.events.get(event_id)
        if not event:
            res = (1, 'No such event')
            return res

        for node in event.start:
            if node.is_consumer():
                coro = envelope.consumer_send_item
            else:
                coro = envelope.worker_send_item
            asyncio.async(
                coro(node, event, [index], data, index), loop=self.loop
            )

        res = (0, "{}".format(event_id))
        return res

    @rpc.method
    @asyncio.coroutine
    def end_event(
        self, envelope_id: str, event_id: str, nb_items: int,
        immediate_reply: bool
    ) -> dict:
        """Finish an event normally.

        :param event_id:
         the event UUID you previously started

        :param immediate_reply: Whether an immediate reply is expected; refer
        to the "Immediate reply" section of the Xbus documentation for details.

        :return: Dictionary.

        Common keys:
        - success: Boolean (true when the call was succesful).

        Success keys:
        - reply_data: Data sent back by the consumer, when using the "immediate
        reply" feature; None otherwise.

        Error keys:
        - error_code: TBD.
        - error_message: TBD.
        """

        envelope = self.envelopes[envelope_id]
        event = envelope.events.get(event_id)
        if not event:
            # TODO Don't hard-code error codes.
            # TODO Separate way of getting error strings?
            return {
                'error_code': 1,
                'error_message': 'No such event',
                'success': False,
            }

        success = False
        reply_data = None

        for node in event.start:
            if node.is_consumer():
                coro = envelope.consumer_end_event
            else:
                coro = envelope.worker_end_event

            # When issuing a request with an "immediate reply", ensure:
            # - That there is only 1 consumer.
            # - That the recipient supports the feature.
            if immediate_reply:
                recipients = node.recipients

                if len(recipients) != 1:
                    # TODO Don't hard-code error codes.
                    # TODO Separate way of getting error strings?
                    return {
                        'error_code': 2,
                        'error_message': (
                            'Immediate reply with multiple or no recipients.'
                        ),
                        'success': False,
                    }

                if not recipients[0].has_feature(
                    RecipientFeature.immediate_reply
                ):
                    # TODO Don't hard-code error codes.
                    # TODO Separate way of getting error strings?
                    return {
                        'error_code': 3,
                        'error_message': (
                            'Immediate reply on a recipient with no such '
                            'support.'
                        ),
                        'success': False,
                    }

            reply_data_future = asyncio.async(
                coro(node, event, nb_items, immediate_reply),
                loop=self.loop,
            )

            if immediate_reply:
                success, reply_data = yield from reply_data_future

        ret = {'success': True}
        if immediate_reply:
            ret.update({
                'reply_data': reply_data,
                'success': success,
            })
        return ret

    @rpc.method
    @asyncio.coroutine
    def end_envelope(self, envelope_id: str, wait_end: bool=False) -> dict:
        """End an envelope normally.

        :param envelope_id:
         the envelope id you want to mark as finished

        :param wait_end:
         a keyword argument to specify if you want to receive the result
         directly or if you want to receive the result only when the
         end_envelope coroutine will be finished. Default is False

        :return:
         a dict containing information about the result like so
         {'success': True, 'message': "1200 lines inserted, import_id: 23455"}
        """

        log.debug(
            "Back: end_envelop received for envelope: {}".format(envelope_id)
        )

        envelope = self.envelopes.get(envelope_id)
        if not envelope:
            res = (1, 'No such envelope')
            return res

        task = asyncio.async(envelope.end_envelope(), loop=self.loop)
        del self.envelopes[envelope_id]

        if wait_end:
            success = yield from task
        else:
            success = True
        return {
            'success': success,
            'envelope_id': envelope_id,
            'message': 'OK'
        }

    @rpc.method
    @asyncio.coroutine
    def cancel_envelope(self, envelope_id: str) -> str:
        """This is used to cancel a previously started envelop and make sure
        the consumers will rollback their changes

        :param envelope_id:
         the UUID of the envelope you want to cancel

        :return:
         the UUID of the envelope that has just been cancelled
        """

        envelope = self.envelopes.get(envelope_id)
        if not envelope:
            res = (1, 'No such envelope')
            return res

        asyncio.async(envelope.stop_envelope(cancelled=True), loop=self.loop)
        del self.envelopes[envelope_id]
        return envelope_id

    @rpc.method
    @asyncio.coroutine
    def get_consumers(self) -> list:
        """Retrieve the list of consumers that have registered into the Xbus
        back-end, including their metadata and the features they support.

        :return: List of 2-element tuples (metadata dict, feature dict).
        """

        ret = []

        # Gather IDs of consumer roles.
        consumer_role_ids = []
        for role_ids in self.consumers.values():
            consumer_role_ids.extend(role_ids)

        # Add information about the recipients.
        for role_id in consumer_role_ids:
            recipient = self.recipients.get(role_id)
            if recipient:
                ret.append((recipient.metadata, recipient.features))

        return ret

    @rpc.method
    @asyncio.coroutine
    def do_retry_event(self, event_id: str):
        future_event_id = asyncio.Future(loop=self.loop)
        retry_call = self.retry_event(
            event_id, future_event_id=future_event_id
        )
        yield from asyncio.wait(
            [future_event_id, retry_call], loop=self.loop,
            return_when=asyncio.FIRST_COMPLETED
        )

        try:
            retry_event_id = future_event_id.result()
        except (asyncio.CancelledError, asyncio.InvalidStateError):
            retry_event_id = ""
        return retry_event_id

    @asyncio.coroutine
    def init_consumers(self) -> bool:
        consumer_roles = yield from self.db.get_consumer_roles()
        for service_id, role_ids in consumer_roles:
            self.consumers[service_id] = set(role_ids)
        return True

    @asyncio.coroutine
    def init_waiting_events(self) -> bool:
        waiting_events = yield from self.db.get_waiting_events()
        for type_id, event_id in waiting_events:
            self.wait_events[type_id].add(event_id)
        if not self.wait_events:
            return
        event_nodes = yield from self.db.get_services_for_types(
            list(self.wait_events.keys())
        )
        for type_id, service_id in event_nodes:
            self.wait_services[type_id].add(service_id)
            self.wait_services_inv[service_id].add(type_id)


@asyncio.coroutine
def get_backserver(engine_callback, config, socket, b2fsocket, loop=None):
    """A helper function that is used internally to create a running server for
    the back part of Xbus

    :param engine_callback:
     the engine constructor we will be to "yield from" to get a real dbengine

    :param config:
     the application configuration instance
     :class:`configparser.ConfigParser` it MUST contain a section redis and
     two keys: 'host' and 'port'

    :param socket:
     a string representing the socker address on which we will spawn our 0mq
     listener

    :param socket:
     the event loop the server must run with

    :return:
     a future that is waiting for a closed() call before being
     fired back.
    """
    dbengine = yield from engine_callback(config)
    db = DatabaseUtils(dbengine)
    broker_back = XbusBrokerBack(db, b2fsocket, socket, loop=loop)

    redis_host = config.get('redis', 'host')
    redis_port = config.getint('redis', 'port')

    yield from broker_back.prepare_redis(redis_host, redis_port)
    yield from broker_back.register_on_front()

    zmqserver = yield from rpc.serve_rpc(
        broker_back,
        bind=socket,
        loop=loop,
    )
    yield from zmqserver.wait_closed()


# we don't want our imports to be visible to others...
__all__ = ["XbusBrokerBack", "get_backserver"]
