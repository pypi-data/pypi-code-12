#!/usr/bin/env python

import os

import example_pythonpath
from example_utils import ExampleServer, ExampleStaticFile

from kombu import Exchange, Queue
from gevent import monkey

import mushroom
from mushroom import messaging
from mushroom import rpc

BROKER_URL = 'amqp://mushroom:mushroom@localhost//mushroom'
CHAT_EXCHANGE = Exchange('chatex', type='fanout')
CHAT_QUEUE = Queue('chat', exchange=CHAT_EXCHANGE, routing_key='chat')

class ChatServer(ExampleServer):
    urls = [
        ('/', ExampleStaticFile('chat.html')),
    ] + ExampleServer.urls

    def server_init(self):
        monkey.patch_socket()
        transport = messaging.Transport(BROKER_URL, CHAT_EXCHANGE, CHAT_QUEUE)
        self.mom = rpc.Engine(transport, mushroom.MethodDispatcher(self, prefix='mom_'))
        transport.start()

    def rpc_message(self, request):
        self.mom.notify('message', request.data, routing_key='chat')

    def mom_message(self, request):
        self.sessions.notify('message', request.data)


if __name__ == '__main__':
    ChatServer.main()
