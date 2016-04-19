# -*- coding: utf-8 -*-
import click
from .process import Process


@click.command()
@click.option('-o', '--option',
              required=True,
              type=click.Choice(['start', 'stop', 'restart']))
@click.option('-h', '--host_port',
              required=True, default=('127.0.0.1', 5000),
              type=(unicode, int), help='Host and port of the server')
@click.option('-st', '--s_type',
              required=True, default='haproxy',
              type=click.Choice(['nginx', 'haproxy']), help='Service type')
@click.option('-pd', '--pid_dist',
              required=True, default='/var/run/',
              help='daemon-glb-slave.pid file location')
@click.option('-sc', '--s_command',
              help='Service command.')
@click.option('-sd', '--conf_dist',
              help='Native location of config file')
@click.option('-ld', '--ssl_dist',
              help='Native location of Service ssl files.')
def process(option, host_port, s_type, pid_dist,
            s_command, conf_dist, ssl_dist):
    websocket_uri = "ws://%s:%s/websocket" % host_port
    s_command = s_command if s_command else 'service %s reload' % s_type
    conf_dist = conf_dist if conf_dist else '/etc/%s/' % s_type
    ssl_dist = ssl_dist if ssl_dist else '/etc/%s/ssl/' % s_type
    p = Process(websocket_uri, s_type, pid_dist,
                s_command, conf_dist, ssl_dist)
    if option == 'start':
        print 'glb_slave service start'
        p.start()
    if option == 'stop':
        p.stop()
        print 'glb_slave service stop'
    if option == 'restart':
        p.restart()
        print 'glb_slave service restart'
