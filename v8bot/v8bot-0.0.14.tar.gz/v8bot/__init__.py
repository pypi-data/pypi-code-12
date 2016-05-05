#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2016, David Ewelt
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from __future__ import unicode_literals, print_function, division

__author__  = "David Ewelt"
__version__ = "0.0.14"
__license__ = "BSD"

import sys
import os
import glob
import time
import argparse
import logging
import threading
import signal
import atexit

import traceback

from hitboxy import ApiClient
from hitboxy.MultiChannelChatClient import MultiChannelChatClient

import PyV8
from PyV8 import JSContext, JSLocker, JSArray, JSObject, JSClass

LOG = logging.getLogger("V8Bot")

from v8bot import API

def safepath(origin, path):
    return os.path.abspath(os.path.join(origin, os.path.normpath(os.path.sep + path).lstrip(os.path.sep)))

def write(value):
    value = str(value)
    sys.stdout.write(value)
    sys.stdout.flush()

class EventManagerEventHandler(object):
    def __init__(self, callback, args=[]):
        self.callback = callback
        self.args = args

    def test(self):
        return False

    def run(self, args=None):
        if not args:
            args = self.args
        try:
            self.callback(*args)
        except:
            LOG.exception("error in event handler callback")

class TimedEventHandler(EventManagerEventHandler):
    def __init__(self, callback, args=[]):
        EventManagerEventHandler.__init__(self, callback, args)
        self.last_run = time.time()

    def test(self):
        return time.time() - self.last_run >= 1.0

    def run(self):
        EventManagerEventHandler.run(self)
        self.last_run = time.time()

class EventManager(threading.Thread):
    class Startup(EventManagerEventHandler):
        pass
    class Shutdown(EventManagerEventHandler):
        pass

    class ChannelJoined(EventManagerEventHandler):
        pass
    class ChannelParted(EventManagerEventHandler):
        pass
    class ChatMessage(EventManagerEventHandler):
        pass

    class ApiRequest(EventManagerEventHandler):
        pass

    class EverySecond(TimedEventHandler):
        def test(self):
            return time.time() - self.last_run >= 1.0
    class EveryTenSeconds(TimedEventHandler):
        def test(self):
            return time.time() - self.last_run >= 10.0
    class EveryMinute(TimedEventHandler):
        def test(self):
            return time.time() - self.last_run >= 60.0
    class EveryFifteenMinutes(TimedEventHandler):
        def test(self):
            return time.time() - self.last_run >= 60.0*15.0
    class EveryThirtyMinutes(TimedEventHandler):
        def test(self):
            return time.time() - self.last_run >= 60.0*30.0
    class EveryHour(TimedEventHandler):
        def test(self):
            return time.time() - self.last_run >= 60.0*60.0

    def __init__(self, bot):
        """
            @type bot: V8Bot
        """
        threading.Thread.__init__(self)

        self.bot = bot

        self.handler_classes = {
            "Startup": EventManager.Startup,
            "Shutdown": EventManager.Shutdown,

            "ChannelJoined": EventManager.ChannelJoined,
            "ChannelParted": EventManager.ChannelParted,
            "ChatMessage": EventManager.ChatMessage,

            "EverySecond": EventManager.EverySecond,
            "EveryTenSeconds": EventManager.EveryTenSeconds,
            "EveryMinute": EventManager.EveryMinute,
            "EveryFifteenMinutes": EventManager.EveryFifteenMinutes,
            "EveryThirtyMinutes": EventManager.EveryThirtyMinutes,
            "EveryHour": EventManager.EveryHour,

            "ApiRequest": EventManager.ApiRequest,
        }
        self.handlers = {}

    def add(self, event, args, fnc):
        if not event in self.handler_classes:
            LOG.error("could not find event handler '%s'", event)
            return

        if not event in self.handlers:
            self.handlers[event] = []

        self.handlers[event].append( self.handler_classes[event](fnc, args) )

    def raise_event(self, event, args=[]):
        LOG.debug("EventManager.raise_event: event=%s, args=%s", event, args)
        if not event in self.handlers:
            return
        for h in self.handlers[event]:
            try:
                if self.bot.v8_entered:
                    h.run(args)
                else:
                    with self.bot.v8_lock:
                        self.bot.enter_v8()
                        h.run(args)
                        self.bot.leave_v8()
            except:
                LOG.exception("error running event handler for '%s'", event)

    def run(self):
        while True:
            for handlers in self.handlers.values():
                for h in handlers:
                    if h.test():
                        with self.bot.v8_lock:
                            self.bot.enter_v8()
                            h.run()
                            self.bot.leave_v8()

            time.sleep(1.0)

class V8File(object):
    @staticmethod
    def open(path, mode):
        return open(safepath(os.curdir, path), mode)

    @staticmethod
    def exists(path):
        return os.path.exists(safepath(os.curdir, path))

class V8Log(object):
    def __init__(self):
        pass

    def info(self, msg, *args, **kwargs):
        LOG.info(msg, *args, **kwargs)
    def debug(self, msg, *args, **kwargs):
        LOG.debug(msg, *args, **kwargs)

class V8ApiClient(ApiClient):
    """
        Wraps ApiClient for use with the PyV8
    """

    @staticmethod
    def get_chat_servers():
        return JSArray( ApiClient.get_chat_servers() )

    def get_channel_status(self, channel):
        return ApiClient.get_channel_status(self, channel)

    def get_channel_followers(self, channel, offset=None, limit=None, reverse=False):
        return JSArray( ApiClient.get_channel_followers(self, channel, offset=offset, limit=limit, reverse=reverse) )

    def update_livestream_nice(self, channel, info):
        return ApiClient.update_livestream_nice(self, channel, dict(info))

class V8Bot(MultiChannelChatClient):
    def __init__(self):
        MultiChannelChatClient.__init__(self)

        self.event_manager = None

        self.api = V8ApiClient()

        self.v8 = JSContext({
            "ApiClient": self.api,

            "Log": V8Log(),
            "File": V8File(),

            "create_pubsub_server": lambda h,p: API.LongPollingServer((h,p)),

            "include": self.include,
            "__version__": "V8Bot v%s, V8 engine v%s" % (__version__, PyV8.JSEngine.version),

            "write": write,
            "time": time.time,
            "sleep": time.sleep,

            "get_channels": lambda: JSArray(self.get_channels()),
            "get_channel_users": lambda c: self.clients[c.lower()].users,

            "register_command": self.register_command,

            "join_channel": self.join_channel,
            "part_channel": self.part_channel,

            "send_chat_message": self.send_chat_message,
            "send_direct_message": self.send_direct_message,
            "kick_user": self.kick_user,
            "ban_user": self.ban_user,
            "unban_user": self.unban_user,
            "add_moderator": self.add_moderator,
            "remove_moderator": self.remove_moderator,
            "slow_mode": self.slow_mode,
            "subscriber_only": self.subscriber_only,
            "sticky_message": self.sticky_message
        })
        self.v8_entered = False
        self.v8_lock = JSLocker()

        self.command_prefix = "!"
        self.commands = {}
        self.username = "UnknownSoldier"
        self.password = ""

        atexit.register(self.atexit_handler)

    def atexit_handler(self):
        try:
            self.event_manager.raise_event("Shutdown")
        except:
            LOG.exception("error calling atexit_handler")

    def include(self, source):
        LOG.debug("including source file: %s", source)
        with open(source, "rb") as fp:
            self.v8.eval(fp.read())

    def enter_v8(self):
        self.v8.enter()
        self.v8_entered = True

    def leave_v8(self):
        self.v8.leave()
        self.v8_entered = False

    def load_script(self, source):
        self.v8.eval(source)
        LOG.debug("script loaded successfully")

        if hasattr(self.v8.locals, "username"):
            self.username = self.v8.locals.username
        if hasattr(self.v8.locals, "password"):
            self.password = self.v8.locals.password
        if hasattr(self.v8.locals, "command_prefix"):
            self.command_prefix = self.v8.locals.command_prefix

    def register_command(self, cmd, num_args, fnc):
        if not isinstance(cmd, JSArray):
            cmd = [cmd]
        for cmd in cmd:
            LOG.debug("register_command: cmd=%s, fnc=%s", cmd, type(fnc))
            self.commands[cmd] = num_args, fnc

    def join_channel(self, channel):
        LOG.info("joining channel: %s", channel)
        MultiChannelChatClient.join_channel(self, channel)

    def part_channel(self, channel):
        LOG.info("leaving channel: %s", channel)
        MultiChannelChatClient.part_channel(self, channel)

    #--

    def on_channel_joined(self, client, channel, name, role):
        MultiChannelChatClient.on_channel_joined(self, client, channel, name, role)
        try:
            self.event_manager.raise_event("ChannelJoined", (channel, name, role))
        except:
            LOG.exception("error in callback function 'on_channel_joined'")

    def on_channel_parted(self, client, channel):
        MultiChannelChatClient.on_channel_parted(self, client, channel)
        try:
            self.event_manager.raise_event("ChannelParted", (channel,))
        except:
            LOG.exception("error in callback function 'on_channel_parted'")

    def on_chat_message(self, client, timestamp, channel, user, content):
        if not content["is_buffer"]:
            text = content["text"]
            if text.startswith(self.command_prefix):
                if " " in text:
                    command, args = text.split(" ", 1)
                else:
                    command = text
                    args = ""
                command = command[1:]
                self.on_command(channel, user, command, args)
                return

        #--

        with self.v8_lock:
            self.enter_v8()
            try:
                if hasattr(self.v8.locals, "on_chat_message"):
                    self.v8.locals.on_chat_message(timestamp, channel, user, content)
            except:
                LOG.exception("error in callback function 'on_chat_message'")
            self.leave_v8()

        #--

        self.event_manager.raise_event("ChatMessage", (timestamp, channel, user, content))

    def on_command(self, channel, user, cmd, args):
        if not cmd in self.commands:
            return

        num_args, fnc = self.commands[cmd]
        if num_args > 0:
            args = args.split(" ", num_args)
        elif num_args == -1:
            args = args.split(" ")
        else:
            args = [args]

        LOG.debug("on_command: channel=%s, user=%s, cmd=%s, args=%s", channel, user, cmd, args)

        with self.v8_lock:
            self.enter_v8()
            try:
                fnc(cmd, channel, user, JSArray(args) )
            except:
                LOG.exception("error in callback function for command '%s'", cmd)
            self.leave_v8()

class Application(object):
    def __init__(self):
        parser = argparse.ArgumentParser(description='V8Bot v%s' % __version__)
        parser.add_argument('-v', '--verbose',  action='count',  dest="verbose",                      help='show debug messages')
        parser.add_argument('-u', '--user',     action='store',  dest="username",                     help='hitbox username')
        parser.add_argument('-p', '--pass',     action='store',  dest="password",                     help='hitbox password')
        parser.add_argument('-l', '--log',      action='store',  dest="logfile", default=None,        help='logfile')
        parser.add_argument('--command-prefix', action='store',  dest="command_prefix", default="!",  help='command prefix, default is !')
        parser.add_argument('--api-address',    action='store',  dest="api_address", default=None,    help='address for the api server, if left no api server is started')
        parser.add_argument('--pubsub-address', action='store',  dest="pubsub_address", default=None, help='address for the api server, if left no api server is started')
        parser.add_argument('-c', '--channel',  action='append', dest="channels",                     help='channels to join')
        parser.add_argument('-i', '--include',  action='append', dest="includes", default=[],         help='java sources to include, filename patterns are allowed')
        parser.add_argument(         'sources', action='append',                                      help='javascript sources to load, filename patterns are allowed')
        self.parser = parser

    def on_sigint(self, signal, frame):
        LOG.info("SIGINT received")
        sys.exit()

    def run(self, argv):
        signal.signal(signal.SIGINT, self.on_sigint)

        args = self.parser.parse_args(argv)

        loglevel = logging.INFO
        if args.verbose > 0:
            loglevel = logging.DEBUG
            logging.basicConfig(level=loglevel, format='[%(name)s] [%(levelname)s] %(message)s')

            if args.verbose < 2:
                for handler in logging.root.handlers:
                    handler.addFilter(logging.Filter(LOG.name))
        else:
            loglevel = logging.INFO
            logging.basicConfig(level=loglevel, format='[%(name)s] [%(levelname)s] %(message)s')

        if not args.logfile is None:
            #-- create file logger
            file_log_handler = logging.FileHandler(args.logfile)
            file_log_handler.setFormatter(logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'))
            file_log_handler.setLevel(loglevel)
            LOG.addHandler(file_log_handler)

        LOG.debug("verbosity level is %s" % args.verbose)
        LOG.debug("working directory is: %s", os.curdir)
        LOG.debug("safe_path resolves to: %s", safepath(os.curdir, '.'))

        #-- create the bot object
        bot = V8Bot()
        bot.username = args.username
        bot.password = args.password
        bot.command_prefix = args.command_prefix
        self.bot = bot

        #-- create the event manager
        event_manager = EventManager(bot)
        event_manager.daemon = True
        self.event_manager = event_manager

        bot.event_manager = event_manager

        #-- load source code
        source_code = ""
        for src in args.sources:
            for fn in glob.glob(src):
                LOG.debug("loading main source file: %s", src)
                with open(fn, "rb") as fp:
                    source_code += fp.read() + "\n"

        #-- append include code
        for inc in args.includes:
            for src in glob.glob(inc):
                LOG.debug("including source file: %s", fn)
                with open(src, "rb") as fp:
                    source_code += fp.read() + "\n"

        if source_code == "":
            LOG.error("no source")
            return -1

        #-- setup the v8 environment (set locals / load script)
        with bot.v8_lock:
            bot.enter_v8()

            bot.v8.locals.EventManager = event_manager

            t_start = time.time()
            try:
                bot.load_script(source_code)
            except:
                LOG.exception("error loading script")
                return 1
            t_end = time.time()
            LOG.info("javascript loaded in %.01f sec.", t_end-t_start)

            bot.leave_v8()

        LOG.debug("authenticate with Hitbox.tv API ...")
        bot.api.authenticate(bot.username, bot.password)

        #-- start the event manager and the bot
        event_manager.start()
        event_manager.raise_event("Startup")

        api_server = None
        if not args.api_address is None:
            def on_api_request(r):
                for k,v in r.query.items():
                    r.query[k] = JSArray(v)
                with JSLocker():
                    self.event_manager.raise_event("ApiRequest", (r,))

            host, _, port = args.api_address.rpartition(":")
            port = int(port)
            LOG.info("starting api server at %s:%s", host, port)

            api_server = API.Server((host,port))
            api_server.on_request = on_api_request
            api_server.daemon = True
            api_server.start()
            self.api_server = api_server

        pubsub_server = None
        if not args.pubsub_address is None:
            def publish_message(channel, message):
                if isinstance(message, JSObject):
                    message = dict(message)
                pubsub_server.send_message(channel, message)

            with bot.v8_lock:
                bot.enter_v8()
                bot.v8.locals.publish_message = publish_message
                bot.leave_v8()

            host, _, port = args.pubsub_address.rpartition(":")
            port = int(port)
            LOG.info("starting pubsub server at %s:%s", host, port)

            pubsub_server = API.LongPollingServer((host,port))
            pubsub_server.on_request = on_api_request
            pubsub_server.daemon = True
            pubsub_server.start()
            self.pubsub_server = pubsub_server
        else:
            def publish_message(channel, message):
                LOG.debug("publish_message was called but the pubsub server was not started")

            with bot.v8_lock:
                bot.enter_v8()
                bot.v8.locals.publish_message = publish_message
                bot.leave_v8()

        for c in args.channels:
            bot.join_channel(c)

        #event_manager.join()
        #if not api_server is None:
        #    api_server.join()
        #if not pubsub_server is None:
        #    pubsub_server.join()

        while threading.active_count() > 0:
            time.sleep(0.1)

        return 0

def main(argv):
    return Application().run(argv)

if __name__ == '__main__':
    main(sys.argv[1:])
