from __future__ import unicode_literals

import threading
import logging

from hitboxy import ApiClient
from hitboxy.ChatClient import ChatClient as SingleChannelChatClient

LOG = logging.getLogger(__name__)

class ChatClient(SingleChannelChatClient, threading.Thread):
    def __init__(self, parent, channel, username="UnknownSoldier", password=""):
        """
            @type parent: MultiChannelChatClient
            @type client_lock: threading.Lock
        """
        SingleChannelChatClient.__init__(self, username, password)
        threading.Thread.__init__(self)

        self.parent = parent
        self.client_lock = parent.client_lock
        self.api = parent.api
        self.channel = channel

    def __str__(self, *args, **kwargs):
        return "<ChatClient(channel=%s)>" % self.channel

    def run(self):
        LOG.debug("starting new chat client thread: %s", self)
        self.connect()
        LOG.debug("chat client thread %s finished", self)

    def on_login(self):
        SingleChannelChatClient.on_login(self)

        with self.client_lock:
            self.parent.on_login(self)

        self.join_channel(self.channel)

    def on_channel_login(self, channel, name, role):
        SingleChannelChatClient.on_channel_login(self, channel, name, role)

        with self.client_lock:
            self.parent.on_channel_joined(self, channel, name, role)

    def on_chat_message(self, timestamp, channel, name, text, role, name_color, is_owner, is_staff, is_follower, is_subscriber, is_community, is_media, is_buffer):
        SingleChannelChatClient.on_chat_message(self, timestamp, channel, name, text, role, name_color, is_owner, is_staff, is_follower, is_subscriber, is_community, is_media, is_buffer)

        user = {
            "name": name,
            "role": role,
            "name_color": name_color,
            "is_owner": is_owner,
            "is_staff": is_staff,
            "is_follower": is_follower,
            "is_subscriber": is_subscriber,
            "is_community": is_community,
        }
        content = {
            "text": text,
            "is_media": is_media,
            "is_buffer": is_buffer
        }

        with self.client_lock:
            self.parent.on_chat_message(self, timestamp, channel, user, content)

class MultiChannelChatClient(object):
    def __init__(self, username="UnknownSoldier", password=""):
        self.username = username
        self.password = password

        self.api = ApiClient()
        self.clients = {}
        self.client_lock = threading.Lock()

    def _create_client(self, channel):
        """
            @rtype: ChatClient
        """
        return ChatClient(self, channel, self.username, self.password)

    def _get_channel_by_client(self, client):
        for ch,cl in self.clients.items():
            if cl is client:
                return ch

    def get_channels(self):
        return self.clients.keys()

    def join_channel(self, channel):
        channel = channel.lower()
        if channel in self.clients:
            return self.clients[channel]

        client = self._create_client(channel)
        client.daemon = True
        self.clients[channel] = client
        client.start()

        return client

    def part_channel(self, channel):
        channel = channel.lower()
        if not channel in self.clients:
            return

        client = self.clients[channel]
        client.part_channel(channel)
        LOG.debug("disconnecting client %s", client)
        client.disconnect()
        client.join()

        del self.clients[channel]

        self.on_channel_parted(self, channel)

    def send_chat_message(self, channel, text):
        channel = channel.lower()
        if not channel in self.clients:
            return
        client = self.clients[channel]
        client.send_chat_message(channel, text)

    def broadcast_chat_message(self, text):
        for c in self.get_channels():
            self.send_chat_message(c, text)

    def send_direct_message(self, channel, user, text):
        channel = channel.lower()
        if not channel in self.clients:
            return
        client = self.clients[channel]
        client.send_direct_message(channel, user, text)

    def kick_user(self, channel, user, timeout=10):
        channel = channel.lower()
        if not channel in self.clients:
            return
        client = self.clients[channel]
        client.kick_user(channel, user, timeout)

    def ban_user(self, channel, user, ip_ban=False):
        channel = channel.lower()
        if not channel in self.clients:
            return
        client = self.clients[channel]
        client.ban_user(channel, user, ip_ban=False)

    def unban_user(self, channel, user):
        channel = channel.lower()
        if not channel in self.clients:
            return
        client = self.clients[channel]
        client.unban_user(channel, user)

    def add_moderator(self, channel, user):
        channel = channel.lower()
        if not channel in self.clients:
            return
        client = self.clients[channel]
        client.add_moderator(channel, user)

    def remove_moderator(self, channel, user):
        channel = channel.lower()
        if not channel in self.clients:
            return
        client = self.clients[channel]
        client.remove_moderator(channel, user)

    def slow_mode(self, channel, time=0):
        channel = channel.lower()
        if not channel in self.clients:
            return
        client = self.clients[channel]
        client.slow_mode(channel, time)

    def subscriber_only(self, channel, enable, rate=0):
        channel = channel.lower()
        if not channel in self.clients:
            return
        client = self.clients[channel]
        client.subscriber_only(channel, enable, rate)

    def sticky_message(self, channel, message=""):
        channel = channel.lower()
        if not channel in self.clients:
            return
        client = self.clients[channel]
        client.sticky_message(channel, message)

    #--

    def on_login(self, client):
        LOG.debug("on_login: %s", client)

    def on_channel_joined(self, client, channel, name, role):
        LOG.debug("on_channel_joined: client=%s, channel=%s, name=%s, role=%s", client, channel, name, role)

    def on_channel_parted(self, client, channel):
        LOG.debug("on_channel_parted: client=%s, channel=%s", client, channel)

    def on_chat_message(self, client, timestamp, channel, user, content):
        LOG.debug("on_chat_message: channel=%s, user=%s, content=%s", channel, user, content)
