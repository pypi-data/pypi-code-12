# -*- encoding: utf-8 -*-
import asyncio
import aiozmq
import logging

from xbus.broker.core.features import RecipientFeature


log = logging.getLogger(__name__)


class Recipient(object):
    """Information about an Xbus recipient (a worker or a consumer):
    - its metadata;
    - the features it supports;
    - a socket.
    """

    def __init__(self, token, role_id):
        self.token = token
        self.role_id = role_id
        self.features = {}
        self.socket = None
        self.metadata = None

    def connect(self, url):
        """Initialize the recipient information holder. Open a socket to the
        specified URL and use it to fetch metadata and supported features.

        :param url: URL to reach the recipient.
        """

        log.info('Connecting to the recipient at %s' % url)
        self.socket = yield from aiozmq.rpc.connect_rpc(connect=url)

        log.info('Getting metadata from the recipient at %s' % url)
        self.metadata = yield from self.socket.call.get_metadata()

        log.info('Getting features from the recipient at %s' % url)
        yield from self.update_features()

    @asyncio.coroutine
    def ping(self) -> bool:
        yield from self.socket.call.ping(self.token)
        return self

    def has_feature(self, feature: RecipientFeature):
        """Tell whether the recipient has declared support for the specified
        feature.

        :param feature: Feature to check for.
        """

        return feature.name in self.features

    def update_features(self):
        """Refresh the list of features the recipient supports.
        :note: The socket must be open.
        """

        self.features = {}
        for feature in RecipientFeature:

            # By default, the feature is not supported.
            self.features[feature.name] = [False]

            # Send a "has_[feature]" API call to see what the recipient has to
            # announce about its support for the feature.
            feature_data = yield from getattr(
                self.socket.call, 'has_%s' % feature.name
            )()

            # Ensure we have received valid data.
            if not feature_data or not isinstance(feature_data, (list, tuple)):
                continue

            # Check the first part (boolean) to know feature support.
            if not feature_data[0]:
                continue

            # Save the data for features that are supported.
            self.features[feature.name] = feature_data
