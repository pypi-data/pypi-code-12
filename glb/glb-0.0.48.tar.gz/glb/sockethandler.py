# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import gevent
import gevent.monkey
from geventwebsocket import WebSocketError

from glb.settings import Config
from glb.core.extensions import socket2redis as redis
from glb.models.balancer import Balancer as BalancerModel
from glb.models.slave import Slave as SlaveModel
from glb.haproxy import haproxy
from glb.nginx import nginx


gevent.monkey.patch_socket()


def handle_websocket(ws):
    '''handle with the websocket client requests'''

    def send_back():
        '''write back service(haproxy or nginx) configuration'''
        balancers = BalancerModel.retrieve_list()
        data = {}
        if slave_service_type == 'haproxy':
            data.setdefault('haproxy_files', haproxy.get_config(balancers, haproxy_unsupport_protocol))
        elif slave_service_type == 'nginx':
            data.setdefault('nginx_files', nginx.get_config(balancers, nginx_unsupport_protocol))
        else:
            data.setdefault('haproxy_files', haproxy.get_config(balancers, haproxy_unsupport_protocol))
            data.setdefault('nginx_files', nginx.get_config(balancers, nginx_unsupport_protocol))

        data.update(slave_version=redis.get(Config.LATEST_VERSION))
        try:
            ws.send(json.dumps(data))
        except WebSocketError:
            # print 'WebSocketError: Socket is dead'
            gevent.GreenletExit()

    def listen():
        '''monitor the changes from redis db'''
        channel = redis.pubsub()
        channel.subscribe(Config.LISTEN_REDIS_CHANNEL)
        for msg in channel.listen():
            publish_data = msg.get('data')
            if publish_data and isinstance(publish_data, str):
                if publish_data.startswith('balancer'):
                    send_back()
    while True:
        try:
            message = ws.receive()
            if not message:
                break
        except WebSocketError:
            break
        message = json.loads(message)
        slave_addr = message.get('addr')
        slave_service_type = message.get('service_type', 'both')
        nginx_unsupport_protocol = message.get('ni_protocol', ())
        haproxy_unsupport_protocol = message.get('hi_protocol', ())
        slave_version = message.get('slave_version', None)
        slave = SlaveModel.retrieve(slave_addr)
        if not slave:
            slave = SlaveModel.save(dict(address=slave_addr))

        def is_service_version_changed():
            version = redis.get(Config.LATEST_VERSION)
            if slave_version != version:
                return True
        if is_service_version_changed():
            send_back()
        greenlet = gevent.spawn(listen)
        gevent.joinall([greenlet])
        greenlet.kill()
