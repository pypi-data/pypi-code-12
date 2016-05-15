import asyncio

import aioxmpp.disco
import aioxmpp.service
import aioxmpp.stanza

from . import xso as pubsub_xso


class Service(aioxmpp.service.Service):
    """
    Client service implementing a Publish-Subscribe client. By loading it into
    a client, it is possible to subscribe to, publish to and otherwise interact
    with Publish-Subscribe nodes.

    (Un-)subscribing and configuring ones own subscription:

    .. automethod:: subscribe

    .. automethod:: request_subscription_config

    .. automethod:: request_default_config

    .. automethod:: set_subscription_config

    .. automethod:: unsubscribe

    Retrieving items:

    .. automethod:: request_items

    .. automethod:: request_items_by_id

    """
    ORDER_AFTER = [
        aioxmpp.disco.Service
    ]

    @asyncio.coroutine
    def subscribe(self, jid, node=None, *,
                  subscription_jid=None,
                  config=None):
        """
        Subscribe to the pubsub `node` hosted at `jid`.

        By default, the subscription request will be for the bare JID of the
        client. It can be specified explicitly using the `subscription_jid`
        argument.

        If the service requires it or if it makes sense for other reasons, the
        subscription configuration :class:`~.forms.xso.Data` form can be passed
        using the `config` argument.

        On success, the whole :class:`.xso.Request` object returned by the
        server is returned. It contains a :class:`.xso.Subscription`
        :attr:`~.xso.Request.payload` which has information on the nature of
        the subscription (it may be ``"pending"`` or ``"unconfigured"``) and
        the :attr:`~.xso.Subscription.subid` which may be required for other
        operations.

        On failure, the corresponding :class:`~.errors.XMPPError` is raised.
        """

        subscription_jid = subscription_jid or self.client.local_jid.bare()

        iq = aioxmpp.stanza.IQ(to=jid, type_="set")
        iq.payload = pubsub_xso.Request(
            pubsub_xso.Subscribe(subscription_jid, node=node)
        )

        if config is not None:
            iq.payload.options = pubsub_xso.Options(
                subscription_jid,
                node=node
            )
            iq.payload.options.data = config

        response = yield from self.client.stream.send_iq_and_wait_for_reply(
            iq
        )
        return response

    @asyncio.coroutine
    def unsubscribe(self, jid, node=None, *,
                    subscription_jid=None,
                    subid=None):
        """
        Unsubscribe from the pubsub `node` hosted at `jid`.

        By default, the unsubscribe request will be for the bare JID of the
        client. It can be specified explicitly using the `subscription_jid`
        argument.

        If available, the `subid` should also be specified.

        If an error occurs, the corresponding :class:`~.errors.XMPPError` is
        raised.
        """

        subscription_jid = subscription_jid or self.client.local_jid.bare()

        iq = aioxmpp.stanza.IQ(to=jid, type_="set")
        iq.payload = pubsub_xso.Request(
            pubsub_xso.Unsubscribe(subscription_jid, node=node, subid=subid)
        )

        yield from self.client.stream.send_iq_and_wait_for_reply(
            iq
        )

    @asyncio.coroutine
    def request_subscription_config(self, jid, node=None, *,
                                    subscription_jid=None,
                                    subid=None):
        """
        Request the current configuration of a subscription to the pubsub
        `node` hosted at `jid`.

        By default, the request will be on behalf of the bare JID of the
        client. It can be overriden using the `subscription_jid` argument.

        If available, the `subid` should also be specified.

        On success, the :class:`~.forms.xso.Data` form is returned.

        If an error occurs, the corresponding :class:`~.errors.XMPPError` is
        raised.
        """

        subscription_jid = subscription_jid or self.client.local_jid.bare()

        iq = aioxmpp.stanza.IQ(to=jid, type_="get")
        iq.payload = pubsub_xso.Request()
        iq.payload.options = pubsub_xso.Options(
            subscription_jid,
            node=node,
            subid=subid,
        )

        response = yield from self.client.stream.send_iq_and_wait_for_reply(
            iq
        )
        return response.options.data

    @asyncio.coroutine
    def set_subscription_config(self, jid, data, node=None, *,
                                subscription_jid=None,
                                subid=None):
        """
        Update the subscription configuration of a subscription to the pubsub
        `node` hosted at `jid`.

        By default, the request will be on behalf of the bare JID of the
        client. It can be overriden using the `subscription_jid` argument.

        If available, the `subid` should also be specified.

        The configuration must be given as `data` as a
        :class:`~.forms.xso.Data` instance.

        If an error occurs, the corresponding :class:`~.errors.XMPPError` is
        raised.
        """

        subscription_jid = subscription_jid or self.client.local_jid.bare()

        iq = aioxmpp.stanza.IQ(to=jid, type_="set")
        iq.payload = pubsub_xso.Request()
        iq.payload.options = pubsub_xso.Options(
            subscription_jid,
            node=node,
            subid=subid,
        )
        iq.payload.options.data = data

        yield from self.client.stream.send_iq_and_wait_for_reply(
            iq
        )

    @asyncio.coroutine
    def request_default_config(self, jid, node=None):
        """
        Request the default configuration of the pubsub `node` hosted at
        `jid`.

        On success, the :class:`~.forms.xso.Data` form is returned.

        If an error occurs, the corresponding :class:`~.errors.XMPPError` is
        raised.
        """

        iq = aioxmpp.stanza.IQ(to=jid, type_="get")
        iq.payload = pubsub_xso.Request(
            pubsub_xso.Default(node=node)
        )

        response = yield from self.client.stream.send_iq_and_wait_for_reply(iq)
        return response.payload.data

    @asyncio.coroutine
    def request_items(self, jid, node, *, max_items=None):
        """
        Request the most recent items from the pubsub `node` hosted at `jid`.

        By default, as many as possible items are requested. If `max_items` is
        given, it must be a positive integer specifying the maximum number of
        items which is to be returned by the server.

        Return the :class:`.xso.Request` object, which has a
        :class:`~.xso.Items` :attr:`~.xso.Request.payload`.
        """

        iq = aioxmpp.stanza.IQ(to=jid, type_="get")
        iq.payload = pubsub_xso.Request(
            pubsub_xso.Items(node, max_items=max_items)
        )

        return (yield from self.client.stream.send_iq_and_wait_for_reply(iq))

    @asyncio.coroutine
    def request_items_by_id(self, jid, node, ids):
        """
        Request specific items by their IDs from the pubsub `node` hosted at
        `jid`.

        `ids` must be an iterable of :class:`str` of the IDs of the items to
        request from the pubsub node. If the iterable is empty,
        :class:`ValueError` is raised (as otherwise, the request would be
        identical to calling :meth:`request_items` without `max_items`).

        Return the :class:`.xso.Request` object, which has a
        :class:`~.xso.Items` :attr:`~.xso.Request.payload`.
        """

        iq = aioxmpp.stanza.IQ(to=jid, type_="get")
        iq.payload = pubsub_xso.Request(
            pubsub_xso.Items(node)
        )

        iq.payload.payload.items = [
            pubsub_xso.Item(id_)
            for id_ in ids
        ]

        if not iq.payload.payload.items:
            raise ValueError("ids must not be empty")

        return (yield from self.client.stream.send_iq_and_wait_for_reply(iq))
