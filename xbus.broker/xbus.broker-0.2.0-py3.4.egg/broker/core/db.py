# -*- encoding: utf-8 -*-
import asyncio
import itertools
from datetime import datetime
from uuid import uuid4

from sqlalchemy.sql import select
from sqlalchemy.sql import and_
from sqlalchemy import func

from xbus.broker.model import emitter
from xbus.broker.model import envelope
from xbus.broker.model import event
from xbus.broker.model import event_node
from xbus.broker.model import event_type
from xbus.broker.model import emitter_profile_event_type_rel
from xbus.broker.model import item
from xbus.broker.model import event_consumer_inactive_rel
from xbus.broker.model import role
from xbus.broker.model import event_error

from xbus.broker.model.helpers import get_event_tree
from xbus.broker.model.helpers import get_consumer_roles

__author__ = 'jeremie'


class DatabaseUtils(object):

    def __init__(self, dbengine):
        self.dbengine = dbengine

    @asyncio.coroutine
    def find_emitter_by_login(self, login: str) -> tuple:
        """Internal helper method used to find an emitter
        (id, password, profile_id) by looking up in the database its login

        :param login:
         the login that identifies the emitter you are searching for

        :return:
         a 3-tuple containing (id, password, profile_id), if nothing is found
         the tuple will contain (None, None, None)
        """
        query = select((emitter.c.id, emitter.c.password,
                        emitter.c.profile_id))
        query = query.where(emitter.c.login == login).limit(1)

        with (yield from self.dbengine) as conn:
            cr = yield from conn.execute(query)
            row = yield from cr.first()
            if row:
                return row.as_tuple()
            else:
                return None, None, None

    @asyncio.coroutine
    def find_event_type_by_name(self, name: str) -> tuple:
        """Internal helper method used to find an event type's id
        by looking up in the database its login

        :param name:
         the name that identifies the event type you are searching for

        :return: 2-element tuple, with:
        - The internal ID of the event type object (or None if not found).
        - Whether the event type has the "immediate reply" flag set.
        """
        query = select((event_type.c.id, event_type.c.immediate_reply))
        query = query.where(event_type.c.name == name)
        query = query.limit(1)

        with (yield from self.dbengine) as conn:
            cr = yield from conn.execute(query)
            row = yield from cr.first()
            if row:
                return row.as_tuple()
            else:
                return None, None

    @asyncio.coroutine
    def read_event_type(self, event_type_id: str) -> str:
        """Internal helper method used to read an event type's properties.

        :param event_type_id:
         the UUID of the event type

        :return: 2-element tuple with:
         - the name that identifies the event type
         - Whether the event type has the "immediate reply" flag set.
        """
        query = select((event_type.c.name, event_type.c.immediate_reply))
        query = query.where(event_type.c.id == event_type_id)
        query = query.limit(1)

        with (yield from self.dbengine) as conn:
            cr = yield from conn.execute(query)
            row = yield from cr.first()
            if row:
                return row.as_tuple()
            else:
                return None, None

    @asyncio.coroutine
    def check_event_access(self, profile_id: str, type_id: str) -> bool:
        """Internal helper method used to determine whether an emitter, by
        its profile, has the right to start an event of the given type.
        (id, password, profile_id) by looking up in the database its login

        :param profile_id:
         the internal UUID of the emitter's profile. This can be obtained
         using the method :meth:`.DatabaseUtils.find_emitter_by_login`.

        :param type_id:
         the internal UUID of the event type. This can be obtained using the
         method :meth:`.DatabaseUtils.find_event_type_by_name`.

        :return:
         True if the emitter has the right to start an event of this type,
         False otherwise
        """
        query = select((func.count(),))
        query = query.select_from(emitter_profile_event_type_rel)
        query = query.where(
            and_(
                emitter_profile_event_type_rel.c.profile_id == profile_id,
                emitter_profile_event_type_rel.c.event_id == type_id
            )
        )
        with (yield from self.dbengine) as conn:
            cr = yield from conn.execute(query)
            res = yield from cr.first()
            return True if res[0] > 0 else False

    @asyncio.coroutine
    def log_new_envelope(self, envelope_id: str, emitter_id: str):
        """Internal helper method used to log the creation of a new envelope.

        :param envelope_id:
         the UUID of the new envelope

        :param emitter_id:
         the internal UUID of the emitter of the new envelope
        """
        insert = envelope.insert()
        insert = insert.values(
            id=envelope_id, state='open', emitter_id=emitter_id,
            posted_date=func.localtimestamp()
        )
        with (yield from self.dbengine) as conn:
            yield from conn.execute(insert)

    @asyncio.coroutine
    def update_envelope_state_received(self, envelope_id: str):
        """Internal helper method used to log the fact that an envelope has
        been successfully received from its emitter, and is currently being
        treated by the back-end.

        :param envelope_id:
         the UUID of the envelope
        """
        update = envelope.update()
        update = update.where(envelope.c.id == envelope_id)
        update = update.values(state='received')
        with (yield from self.dbengine) as conn:
            yield from conn.execute(update)

    @asyncio.coroutine
    def update_envelope_state_cancel(self, envelope_id: str):
        """Internal helper method used to log the cancellation of an
        envelope before its emission was completed.

        :param envelope_id:
         the UUID of the envelope.
        """
        update = envelope.update()
        update = update.where(envelope.c.id == envelope_id)
        update = update.values(state='cancelled')
        with (yield from self.dbengine) as conn:
            yield from conn.execute(update)

        update = event.update()
        update = update.where(event.c.envelope_id == envelope_id)
        update = update.values(execution_state='canc')
        with (yield from self.dbengine) as conn:
            yield from conn.execute(update)

    @asyncio.coroutine
    def log_new_event(
        self, event_id: str, envelope_id: str, emitter_id: str, type_id: str,
        estimate: int, origin_event_id: str=None
    ):
        """Internal helper method used to log the creation of a new event.

        :param event_id:
         the UUID of the new event

        :param envelope_id:
         the UUID of the envelope which contains the event

        :param emitter_id:
         the internal UUID of the emitter of the new event

        :param type_id:
         the internal UUID of the event type. This can be obtained using the
         method :meth:`.DatabaseUtils.find_event_type_by_name`

        :param origin_event_id:
         if the event is a retry of a previous one, the UUID of that event.

        :param estimate:
         an estimation, by the emitter, of the number of items that will be
         sent for this event.
        """
        insert = event.insert()
        insert = insert.values(
            id=event_id, envelope_id=envelope_id, emitter_id=emitter_id,
            type_id=type_id, estimated_items=estimate, execution_state='wait',
            tracking_state='unprocessed', origin_event_id=origin_event_id
        )
        with (yield from self.dbengine) as conn:
            yield from conn.execute(insert)

    def read_event(self, event_id: str):
        """Internal helper method used to retrieve informations about an event.

        :param event_id:
         the UUID of the event

        :return: 5-element tuple with:
         - the UUID of the event's type
         - the date when the event's execution started.
         - the number of items sent by the emitter.
         - the execution state.
         - if the event is a retry of a previous one, the UUID of that event.
        """
        query = select((
            event.c.type_id, event.c.started_date, event.c.sent_items,
            event.c.execution_state, event.c.origin_event_id
        ))
        query = query.where(event.c.id == event_id)
        query = query.limit(1)

        with (yield from self.dbengine) as conn:
            cr = yield from conn.execute(query)
            row = yield from cr.first()
            if row:
                return row.as_tuple()
            else:
                return None, None, None, None, None

    @asyncio.coroutine
    def update_event_sent_items_count(self, event_id: str, sent_items: int):
        """Internal helper method used to log the number of items that was
        finally sent by the emitter for a given event.

        :param event_id:
         the UUID of the event

        :param sent_items:
         the number of items that were emitted
        """
        update = event.update()
        update = update.where(event.c.id == event_id)
        update = update.values(sent_items=sent_items)
        with (yield from self.dbengine) as conn:
            yield from conn.execute(update)

    @asyncio.coroutine
    def log_sent_item(self, event_id: str, index: int, data: bytes):
        """Internal helper method used to preserve the data of each item
        received from the emitter.

        :param event_id:
         the UUID of the event

        :param index:
         the position of the item in the event

        :param data:
         the item's data payload.
        """
        insert = item.insert()
        insert = insert.values(event_id=event_id, index=index, data=data)
        with (yield from self.dbengine) as conn:
            yield from conn.execute(insert)

    @asyncio.coroutine
    def read_items(self, event_id):
        """Internal helper method used to read the data associated with an
        event.

        :param event_id:
         the UUID of the event that was originally sent by the emitter.

        :return:
         the items as a list of tuple (index, data)
        """
        query = select((item.c.index, item.c.data))
        query = query.where(item.c.event_id == event_id)
        with(yield from self.dbengine) as conn:
            cr = yield from conn.execute(query)
            res = yield from cr.fetchall()
            return (row.as_tuple() for row in res)

    @asyncio.coroutine
    def log_inactive_consumers(self, event_id: str, inactive: list):
        """Internal helper method used to log all consumers that should have
        received the event data but were inactive or unavailable.

        :param event_id:
         the UUID of the event

        :param inactive:
         a list of tuples (node_id, role_id, was_unavailable)
        """
        insert = event_consumer_inactive_rel.insert()
        insert = insert.values([dict(
            event_id=event_id, node_id=i[0], role_id=i[1], was_unavailable=i[2]
        ) for i in inactive])
        with (yield from self.dbengine) as conn:
            yield from conn.execute(insert)

    @asyncio.coroutine
    def check_consumer_inactivity(self, role_id: str):
        """Internal helper method used to log all consumers that should have
        received the event data but were inactive or unavailable.

        :param role_id:
         the UUID of the consumer role

        :return:
         the list of events to replay for this consumer
        """
        query = select((event_consumer_inactive_rel.c.event_id,))
        query = query.where(and_(
            event_consumer_inactive_rel.c.role_id == role_id,
            event_consumer_inactive_rel.c.retry_event_id.is_(None)
        ))
        with (yield from self.dbengine) as conn:
            cr = yield from conn.execute(query)
            res = yield from cr.fetchall()
            return list(zip(row[0] for row in res))[0] if res else []

    @asyncio.coroutine
    def update_active_consumers(
        self, event_id: str, role_ids: list, retry_event_id: str
    ):
        """Internal helper method used to update the list of inactive consumer
        roles after an event has been replayed.

        :param event_id:
         the UUID of the original event

        :param event_id:
         the UUID of the roles that have successfully consumed the event
         after the retry

        :param retry_event_id:
         the UUID of the retry event
        """
        update = event_consumer_inactive_rel.update()
        update = update.where(and_(
            event_consumer_inactive_rel.c.event_id == event_id,
            event_consumer_inactive_rel.c.role_id.in_(role_ids)
        ))
        update = update.values(retry_event_id=retry_event_id)
        with (yield from self.dbengine) as conn:
            yield from conn.execute(update)

    @asyncio.coroutine
    def update_retry_event_id(self, event_id: str, retry_event_id: str):
        """Internal helper method used to log the number of items that was
        finally sent by the emitter for a given event.

        :param event_id:
         the UUID of the event
        """
        update = event.update()
        update = update.where(event.c.id == event_id)
        update = update.values(retry_event_id=retry_event_id)
        with (yield from self.dbengine) as conn:
            yield from conn.execute(update)

    @asyncio.coroutine
    def get_event_tree(self, type_id: str):
        """Internal helper method used to find all nodes and the links
        between them that constitute the execution tree of an event type.

        See xbus_get_event_tree in xbus_monitor/xbus/monitor/scripts/func.sql

        :param type_id
         the UUID that corresponds to the type of the event.

        :return:
         the event nodes, as a generator of 4-tuples containing
         (id, service_id, is_start, [child_id, child_id, ...])
        """
        with (yield from self.dbengine) as conn:
            event_tree = yield from get_event_tree(conn, type_id)
        return (row.as_tuple() for row in event_tree)

    @asyncio.coroutine
    def get_consumer_roles(self):
        with (yield from self.dbengine) as conn:
            consumer_roles = yield from get_consumer_roles(conn)
        return (row.as_tuple() for row in consumer_roles)

    @asyncio.coroutine
    def get_waiting_events(self):
        """Internal helper method to get all events in the 'wait' state along
        with their type.

        :return:
         the events, as a generator of 2-tuples containing (type_id, event_id)
        """
        query = select((event.c.type_id, event.c.id))
        query = query.where(and_(
            event.c.execution_state == 'wait', event.c.retry_event_id.is_(None)
        ))
        with (yield from self.dbengine) as conn:
            cr = yield from conn.execute(query)
            res = yield from cr.fetchall()
            return (row.as_tuple() for row in res)

    @asyncio.coroutine
    def get_services_for_types(self, type_ids: list):
        """Internal helper method to get all services included in the graph for
        the given event types.

        :return:
         the event types associated with the services they involve,
         as a generator of 2-tuples containing (type_id, service_id)
        """
        query = select((event_node.c.type_id, event_node.c.service_id))
        query = query.where(event_node.c.type_id.in_(type_ids))
        with (yield from self.dbengine) as conn:
            cr = yield from conn.execute(query)
            res = yield from cr.fetchall()
            return (row.as_tuple() for row in res)

    @asyncio.coroutine
    def find_role_by_login(self, login: str) -> tuple:
        """internal helper method used to find a role
        (id, password, service_id) by looking up in the database its login

        :param login:
         the login that identifies the role you are searching

        :return:
         a 3-tuple containing (id, password, service_id), if nothing is found
         the tuple will contain (None, None, None)
        """
        query = select((role.c.id, role.c.password, role.c.service_id))
        query = query.where(role.c.login == login).limit(1)

        with (yield from self.dbengine) as conn:
            cr = yield from conn.execute(query)
            row = yield from cr.first()
            if row:
                return row.as_tuple()
            else:
                return None, None, None

    @asyncio.coroutine
    def update_event_state_exec(self, event_id: str):
        """Internal helper method used to log the number of items that was
        finally sent by the emitter for a given event.

        :param event_id:
         the UUID of the event
        """
        update = event.update()
        update = update.where(event.c.id == event_id)
        update = update.values(
            execution_state='exec', started_date=func.localtimestamp()
        )
        with (yield from self.dbengine) as conn:
            yield from conn.execute(update)

    @asyncio.coroutine
    def update_events_state_done(self, done_event_ids, part_event_ids):
        """Internal helper method used to log the successful execution of all
        events in the envelope.
        """
        update_done = event.update()
        if done_event_ids:
            update_done = update_done.where(
                event.c.id.in_(done_event_ids),
                )
            update_done = update_done.values(
                execution_state='done', done_date=func.localtimestamp()
            )

        update_part = event.update()
        if part_event_ids:
            update_part = update_part.where(
                event.c.id.in_(part_event_ids),
            )
            update_part = update_part.values(
                execution_state='part', done_date=func.localtimestamp()
            )

        with (yield from self.dbengine) as conn:
            if done_event_ids:
                yield from conn.execute(update_done)
            if part_event_ids:
                yield from conn.execute(update_part)

    @asyncio.coroutine
    def update_events_state_stop(self, envelope_id):
        """Internal helper method used to log the failed execution of all
        events in the envelope.
        """
        update = event.update()
        update = update.where(event.c.envelope_id == envelope_id)
        update = update.values(execution_state='stop')
        with (yield from self.dbengine) as conn:
            yield from conn.execute(update)

    @asyncio.coroutine
    def log_event_errors(
        self, errors, envelope_id, event_id=None, node_id=None
    ):
        """Internal helper method to log the errors during the execution of an
        event.

        :param errors:
         a list of errors with the format (item_indices, message), where
         item_indices is a list of integers and message is a string.

        :param envelope_id:
         the envelope_id on which the error occured

        :param event_id:
         the Event id on which the error occured

        :param node_id:
         the Node id that threw the error.
        """
        error_iter = (dict(
            id=uuid4(), envelope_id=envelope_id, event_id=event_id,
            node_id=node_id, items=items, message=message,
            error_date=datetime.utcnow(), state='unprocessed'
        ) for items, message in self.error_format(errors))
        with (yield from self.dbengine) as conn:
            error_slice = list(itertools.islice(error_iter, 1000))
            while error_slice:
                insert = event_error.insert().values(error_slice)
                yield from conn.execute(insert)
                error_slice = list(itertools.islice(error_iter, 1000))

    @staticmethod
    def error_format(errors):
        """Used by :meth:`log_event_errors` to check the error list and
        reformat the item indices into a comma-separated string.

        :param errors:
         a list of errors with the format (item_indices, message), where
         item_indices is a list of integers and message is a string.

        :return:
         the list of errors, checked and reformatted, with appropriate error
         messages if the error list format is incorrect.
        """
        try:
            errors_iter = iter(errors)
        except TypeError:
            yield (None, "Invalid error format")
            return
        for error in errors_iter:
            try:
                indices, message = error
                items = ','.join(str(i) for i in indices)
                if isinstance(message, str):
                    yield (items, message)
                else:
                    yield (items, "Invalid error message")
            except (TypeError, ValueError):
                yield (None, "Invalid error format")
