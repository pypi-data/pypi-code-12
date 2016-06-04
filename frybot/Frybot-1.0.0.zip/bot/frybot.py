"""This is frybot.

A Slack bot that sends Futurama memes and quotes.

Sources:
https://github.com/shaunduncan/giphypop
https://en.wikiquote.org/wiki/Futurama
"""  # Module comment : detailed module explanation.

import asyncio
import json
from random import randrange
from time import sleep  # Separate Python stdlib and external imports (PEP8)

import giphypop
from slackclient import SlackClient

from conf.config import TOKEN, DEBUG
from bot.debug import print_debug
from bot import image_search


class FryBot(object):  # DOCSTRINGS btw triple-double-guote (PEP8) : http://stackoverflow.com/a/9448136/2652657
    """Bot that sends Futurama's Fry memes and quotes."""

    def __init__(self, token):
        """:param: token"""
        self.giphy = giphypop.Giphy()  # Giphy works with public auth, so we use it as is.
        self.sc = SlackClient(token)
        self.channel = None
        self.name = None
        self.user_id = None
        self.quote_list = ["Farnsworth: My God! I've got to save them! "
                           "Although I am already in my pajamas. [falls asleep]",
                           "Bender: Bite my shiny metal ass.\nFry: It doesn't look so shiny to me.",
                           "Prof. Farnsworth: Please, Fry. I don't know how to teach. I'm a professor."
                           ]

    def _fgif(self, event, event_username, user_channel):  # Private methods/functions start with _(PEP8)
        """Prepare GIF for sending
        :param: event
        :param: event_name
        :param: user_channel
        :return: media url"""
        query = event["text"][5:]
        response = self.giphy.search_list("Futurama", query)
        rand_index = randrange(0, len(response))
        input = response[rand_index]
        return self.sc.api_call("chat.postMessage", as_user="true", channel=user_channel,
                                text="<@{0}> {1}".format(event_username, "Shut up and take my Gif!"),
                                attachments=json.dumps([{"title": "image",
                                                         "image_url": input.media_url}]))

    def _fpict(self, event, event_username, user_channel):
        """Prepare picture URL for sending
        :param: event
        :param: event_name
        :param: user_channel
        :return: image url"""
        value = event["text"].find("fpict") + 6
        search_word = event["text"][value:]
        print_debug(search_word)
        return self.sc.api_call("chat.postMessage", as_user="true", channel=user_channel,
                                text="<@{0}> {1}".format(event_username, "Shut up and take my Pict!"),
                                attachments=json.dumps([{"title": "image",
                                                         "image_url": image_search.search_image(search_word)}])
                                )

    def _fquote(self, event_username, user_channel):
        """Prepare quote for sending
        :param: event
        :param: event_name
        :param: user_channel
        :return: quote"""
        rand_index = randrange(0, len(self.quote_list))
        input = self.quote_list[rand_index]
        return self.sc.api_call("chat.postMessage", as_user="true", channel=user_channel,
                                text="<@{0}> {1}".format(event_username, input)
                                )

    def _help(self):
        """Displays the help message to the channel
        :return: help text."""
        return "Not sure if need help or just lost..\n" \
               "This bot is dedicated to Futurama, hell yeah you can have some fun\n" \
               " - fquote : sends you a random quote \n" \
               " - fgif : sends you a random gif \n" \
               " - fpict : sends you a random pict \n" \
               " - help :  hehehe\n"

    def _parse(self, event):
        """Parse user input
        :param: event
        :return: help message if command not found"""
        event_username = self.sc.api_call('users.info', user=event["user"])['user']['name']
        user_channel = event["channel"]

        if "fgif" in event["text"]:
            msg = self._fgif(event, event_username, user_channel)
        elif "fquote" in event["text"]:
            msg = self._fquote(event_username, user_channel)
        elif "fpict" in event["text"]:
            msg = self._fpict(event, event_username, user_channel)
        else:
            self.sc.api_call("chat.postMessage", as_user="true", channel=user_channel,
                             text=self._help())

    def run(self):
        """Run the bot and treat incoming events
        :except: InterruptError
        :raise: RuntimeError"""
        for test in ["api.test", "im.open", "auth.test"]:  # Super pythonic testing stuff
            print_debug(self.sc.api_call(test))

            if self.sc.rtm_connect():
                self.user_id = self.sc.api_call("auth.test")["user_id"]
                while True:
                    try:
                        for event in self.sc.rtm_read():
                            if "type" in event:
                                if event["type"] == "message" and "text" in event \
                                     and "bot_id" not in event and event["text"].startswith("<@"+self.user_id+">:"):
                                    print_debug(event)
                                    self._parse(event)
                        sleep(0.5)
                    except InterruptedError:
                        print("Something went wrong there..")
            else:
                raise RuntimeError("Connection failed to Slack platform...")


if __name__ == '__main__':  # behavior "by default" when exec
    fb = FryBot(TOKEN)
    try:
        loop = asyncio.get_event_loop()
        loop.set_debug(DEBUG)
        loop.run_until_complete(fb.run())
        loop.close()
    except KeyboardInterrupt:  # ctrl-c
        print("Bye guyz, I'm out...")
