from __future__ import unicode_literals

import httplib
import random
import json
import datetime
import logging

import websocket

from hitboxy import ApiClient

LOG = logging.getLogger(__name__)

class ConnectionFailedError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)

class ChatClient(object):
    def __init__(self, username="UnknownSoldier", password=""):
        self.path = '/socket.io/1'

        self.username = username
        self.password = password
        self.name_color = 'ff0000'
        
        self.api = ApiClient()
        self.auth_token = None
        
        self.channel = ""
        self.users = {}

    def _send(self, data):
        LOG.debug("_send: %s", data)
        self.socket.send(data)

    def _send_message(self, method, params):
        message = {
            'name': 'message',
            'args': [
                {
                    'method': method,
                    'params': params
                }
            ]
        }
        self._send('5:::' + json.dumps(message))

    def on_open(self, ws):
        pass

    def on_close(self, ws):
        pass

    def on_error(self, ws, error):
        pass

    def on_message(self, ws, message):
        message = message.decode("utf-8")
        LOG.debug("on_message: %s", message)
        if message == '1::':
            if self.username != "UnknownSoldier":
                LOG.debug("aquiring auth token for user %s ...", self.username)
                self.auth_token = self.api.authenticate(self.username, self.password)
            self.on_login()
        elif message == '2::':
            self.socket.send('2::')
            self.get_channel_users(self.channel)            
        elif message.startswith('5:::'):
            data = json.loads(message[4:])
            if data['name'] != 'message':
                return
            msg = json.loads(data['args'][0])
            self.on_system_message(msg['method'], msg['params'])      

    #--------------------------------------------------------------------------------------------------------------------------------
    #-- Events
    #--------------------------------------------------------------------------------------------------------------------------------
    def on_login(self):
        pass

    def on_channel_login(self, channel, name, role):
        pass

    def on_system_message(self, method, params):
        if method == 'loginMsg':
            self.channel = params['channel']
            self.on_channel_login(params['channel'], params['name'], params['role'])
            self.get_channel_users(self.channel)
        elif method == 'chatMsg':
            self.on_chat_message(
                datetime.datetime.fromtimestamp(params['time']), params['channel'], params['name'], params['text'], params['role'], params['nameColor'],
                params['isOwner'], params['isStaff'], params['isFollower'], params['isSubscriber'], params['isCommunity'], params['media'], params.get("buffer", False)
            )
        elif method == "userList":
            #channel = params['channel']
            data = params['data']
            
            users = {}
            def create_user():
                return {"role": "", "is_follower": False, "is_subscriber": False, "is_staff": False, "is_community": False}

            for role in ("admin", "user", "anon"):
                for name in data[role]:
                    if not name in users:
                        users[name] = create_user()
                    users[name]["role"] = role
                    
            for key,flag in (("isFollower", "is_follower"), ("isSubscriber","is_subscriber"), ("isStaff","is_staff"), ("isCommunity","is_community")):
                for name in data[key]:
                    users[name][flag] = True
                    
            self.users = users
            LOG.debug("users=%s", self.users)

        elif method == "chatLog":
            self.on_chat_log(
                datetime.datetime.fromtimestamp(params['timestamp']), params['channel'], params['text'], params.get("buffer", False)
            )

    def on_chat_message(self, timestamp, channel, name, text, role, name_color, is_owner, is_staff, is_follower, is_subscriber, is_community, is_media, is_buffer):
        pass
    
    def on_chat_log(self, timestamp, channel, text, is_buffer):
        pass
   
    #--------------------------------------------------------------------------------------------------------------------------------
    #-- public methods
    #--------------------------------------------------------------------------------------------------------------------------------

    def connect(self):
        self.servers = ApiClient.get_chat_servers()
        self.server = random.choice(self.servers)

        c = httplib.HTTPConnection(self.server)
        c.request("GET", self.path)
        r = c.getresponse()
        if r.status != 200:
            raise ConnectionFailedError('wrong status response from chat server: %s - %s' % (r.status, r.reason))            
        data = r.read()
        if not ':' in data:
            raise ConnectionFailedError("wrong response from chat server: '%s'" % (data))
        data = data.split(':')

        self.id = data[0]

        LOG.debug("choosen server: %s", self.server)
        LOG.debug("id: %s", self.id)

        #ws://<server>/socket.io/1/websocket/<id>
        wsurl = "ws://" + self.server + self.path + "/websocket/" + self.id

        websocket.setdefaulttimeout(10.0)
        self.socket = websocket.WebSocketApp(
            wsurl,
            on_message = self.on_message,
            on_error = self.on_error,
            on_close = self.on_close,
        )
        self.socket.on_open = self.on_open
        self.socket.run_forever()

    def disconnect(self):
        self.socket.close()
        
    def get_channel_users(self, channel):
        self._send_message(
            'getChannelUserList',
            {
                'channel': channel.lower(),
            }
        )        

    def join_channel(self, channel, admin=False):
        self._send_message(
            'joinChannel',
            {
                'channel': channel.lower(),
                'name': self.username,
                'token': self.auth_token,
                'isAdmin': admin
            }
        )

    def part_channel(self, channel):
        self._send_message(
            'partChannel',
            {
                'channel': channel.lower(),
                'name': self.username,
                'token': self.auth_token,
            }
        )

    def send_chat_message(self, channel, text):
        self._send_message(
            'chatMsg',
            {
                'channel': channel.lower(),
                'name': self.username,
                'nameColor': self.name_color,
                'text': text
            }
        )          

    def send_direct_message(self, channel, user, text):
        self._send_message(
            'directMsg',
            {
                'channel': channel.lower(),
                'from': self.username,
                'to': user,
                'nameColor': self.name_color,
                'text': text
            }
        )          

    def kick_user(self, channel, user, timeout=10):
        self._send_message(
            'kickUser',
            {
                'channel': channel.lower(),
                'token': self.auth_token,
                'name': user,
                'timeout': timeout
            }
        )

    def ban_user(self, channel, user, ip_ban=False):
        self._send_message(
            'banUser',
            {
                'channel': channel.lower(),
                'token': self.auth_token,
                'name': user,
                'banIP': ip_ban
            }
        )

    def unban_user(self, channel, user):
        self._send_message(
            'unbanUser',
            {
                'channel': channel.lower(),
                'token': self.auth_token,
                'name': user,
            }
        )
        
    def add_moderator(self, channel, user):
        self._send_message(
            'makeMod',
            {
                'channel': channel.lower(),
                'token': self.auth_token,
                'name': user,
            }
        )

    def remove_moderator(self, channel, user):
        self._send_message(
            'removeMod',
            {
                'channel': channel.lower(),
                'token': self.auth_token,
                'name': user,
            }
        )

    def slow_mode(self, channel, time=0):
        self._send_message(
            'removeMod',
            {
                'channel': channel.lower(),
                'token': self.auth_token,
                'time': time,
            }
        )

    def subscriber_only(self, channel, enable, rate=0):
        self._send_message(
            'slowMode',
            {
                'channel': channel.lower(),
                'token': self.auth_token,
                'subscriber': enable,
                'rate': rate,
            }
        )

    def sticky_message(self, channel, message=""):
        if message is None:
            message = ""
        self._send_message(
            'motdMsg',
            {
                'channel': channel.lower(),
                'token': self.auth_token,
                'nameColor': self.name_color,
                'text': message,
            }
        )