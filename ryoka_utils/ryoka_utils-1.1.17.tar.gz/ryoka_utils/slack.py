#!/usr/bin/env python
# -*- coding: utf-8 -*-

from slacker import Slacker
from utils import Utils
from time import sleep
from datetime import datetime
 
class Slack(Slacker):
    def __init__(self, token, ignore_channel=False):
        Slacker.__init__(self, token)

        self.utils = Utils()
        self.channel_list = []
        self.username = "Slack Bot"

        self.ignore_channel = ignore_channel
        self.channel_id = None
        self.channel_name = None

        # Fetch channel list.
        raw_data = self.channels.list().body
        for data in raw_data["channels"]:
            if (self.channel_id is None):
                self.channel_id = data["id"]
                self.channel_name = data["name"]
            self.channel_list.append(dict(channel_id=data["id"], channel_name=data["name"])) 

    def _is_exist_channel(self):
        for c in self.channel_list:
            if (c["channel_name"] == self.channel_name): return True
        return False

    def set_channel(self, channel_name):
        self.channel_name = channel_name
        self.channel_id = self.channels.get_channel_id(channel_name)

    def set_username(self, username):
        self.username = username
 
    def get_channel_list(self):
        return self.channel_list

    def post_message(self, message):
        if (not self.ignore_channel and not self._is_exist_channel()):
            print("Not exist channel. [%s]" % (self.channel_name))
            print(self.channel_list)
            self.utils.exit()

        channel_name = "#" + self.channel_name
        self.chat.post_message(channel_name, message, username=self.username)

    def get_history(self, count=100, latest=None, oldest=None, unread=False):
        history = []
        for h in self.channels.history(self.channel_id, count=count, latest=latest, oldest=oldest, unreads=unread).body["messages"]:
            if ("username" in h):
                username = h["username"]
            else:
                username = None
                for u in self.users.list().body["members"]:
                    if (not "user" in h): break
                    if (u["id"] == h["user"]):
                         username = u["name"]
                         break
        
            text = "" if (not "text" in h) else h["text"]
            history.append({
                "username": username,
                "text": text,
            })
        return history

    def _get_now(self):
        return datetime.now().strftime('%s')

    def listen(self, interval=1000, callback=None):
        prev_time = self._get_now()
        try:
            while True:
                now_time = self._get_now()
                sleep(interval / 1000)
                history = self.get_history(oldest=prev_time, latest=now_time)
                if (len(history) != 0 and callback is not None):
                    callback(history)
                prev_time = now_time
        except KeyboardInterrupt:
            pass

#def recieve(history):
#    print(history)
#
#if __name__ == "__main__":
#    slack = Slack("xoxp-44427877605-44427877701-44425136774-df3a4e42b8")
#
#    slack.listen(callback=recieve)
#    slack.post_message("TEST1")
#    history = slack.get_history(count=10)
#
#    for m in history:
#        print(m)
#
