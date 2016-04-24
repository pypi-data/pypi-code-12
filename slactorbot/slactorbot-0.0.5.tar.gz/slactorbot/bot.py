#!/usr/bin/env python
import sys
import time
import yaml
from lib import plugins
from plugins import plugins_dir
from slackclient import SlackClient
from thespian.actors import *


def start():
    if len(sys.argv) < 2:
        print "usage: %s config_file_location" % sys.argv[0]
        sys.exit(1)
    else:
        config_file = sys.argv[1]
    with open(config_file, 'r') as stream:
        config = yaml.load(stream)

    slack_token = config['slack_token']
    slack_channel = config['slack_channel']
    bot_name = config['bot_name']

    slack_client = SlackClient(slack_token)
    actor_system = ActorSystem()
    plugin_actors = {}

    if slack_client.rtm_connect():
        print "slactorbot started"
        print "plugins dir: %s" % plugins_dir()
        channel = slack_client.server.channels.find(slack_channel)
        while True:
            try:
                plugin_actors = plugins.load_plugins(actor_system, plugin_actors)
                slack_client.server.ping()
                message = slack_client.rtm_read()
                if isinstance(message, list) and len(message) > 0:
                    message = message[0]
                    if 'type' in message.keys() and message['type'] == 'message':
                        if 'text' in message.keys() and message['text'].startswith(bot_name):
                            commands = message['text'].split()
                            if len(commands) == 1:
                                channel.send_message('please specify a command or help')
                            elif commands[1] == 'help':
                                help_message = "available commands: %s" % ','.join(plugin_actors.keys())
                                channel.send_message(help_message)
                            else:
                                actor = commands[1]
                                reply = actor_system.ask(plugin_actors[actor]['actor'], commands[2:], 1.5)
                                channel.send_message(reply)
                time.sleep(1)

            except KeyError:
                channel.send_message('unknown command')

            except KeyboardInterrupt:
                actor_system.shutdown()
                sys.exit(0)
    else:
        print "Connection Failed, invalid token?"
        sys.exit(2)