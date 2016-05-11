#!/usr/bin/env python

import time


class Snapshot(object):
    """A snapshot of data ready to send to the API"""

    def __init__(self, timestamp=None):
        """
        Creates a new snapshot for the specified timestamp. If a timestamp is not provided, it is assumed to be a
        snapshot taken at the current time.
        :param timestamp:
        :return:
        """
        self.timestamp = timestamp if timestamp else time.time()
        self.channels = {}
        self.alarms = {}

    def set_channel(self, channel_id, value):
        """
        Set a channel ID to a specified value for this snapshot.
        :param channel_id:
        :param value:
        :return:
        """
        self.channels[channel_id] = value

    def get_channel(self, channel_id):
        """
        Get a channel ID from this snapshot.
        :param channel_id:
        :return:
        """
        return self.channels.get(channel_id, None)

    def set_alarm(self, channel_id, alarm):
        """
        Set an alarm on a channel.
        :param channel_id:
        :param alarm:
        :return:
        """
        self.alarms[channel_id] = alarm

    def get_api_data(self):
        """
        Build an API representation of this snapshot.
        :return:
        """
        data = {}
        for channel_id, channel_value in self.channels.iteritems():
            data[channel_id] = [channel_value]
            if channel_id in self.alarms:
                data[channel_id].append(self.alarms.get(channel_id, ''))

        return {'timestamp': self.timestamp, 'data': data}

