#!/usr/bin/env python
# -*- coding: utf-8 -*-
from slacker import Slacker
from utils import Utils
 
class Slack(Slacker):
    def __init__(self, token):
        Slacker.__init__(self, token)

        self.utils = Utils()
        self.channel_list = []
        self.username = "Slack Bot"

        # Fetch channel list.
        raw_data = self.channels.list().body
        for data in raw_data["channels"]:
            self.channel_list.append(dict(channel_id=data["id"], channel_name=data["name"])) 

    def _is_exist_channel(self, channel):
        for c in self.channel_list:
            if (c["channel_name"] == channel): return True
        return False

    def set_username(self, username):
        self.username = username
 
    def get_channel_list(self):
        return self.channel_list

    def post_message_to_channel(self, channel, message):
        if (not self._is_exist_channel(channel)):
            print("Not exist channel. [%s]" % (channel))
            print(self.channel_list)
            self.utils.exit()

        channel_name = "#" + channel
        self.chat.post_message(channel_name, message, username=self.username)
 
#if __name__ == "__main__":
#    slack = Slack("xoxp-44427877605-44427877701-44425136774-df3a4e42b8")
#
#    slack.post_message_to_channel("general", "TEST")
#
