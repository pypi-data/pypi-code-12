# -*- coding: utf-8 -*-
import click
from .process import Process


@click.command()
@click.option('-h', '--host_port',
              required=True, default=('127.0.0.1', 5000),
              type=(unicode, int), help='Host and port of the server')
@click.option('-st', '--service_type',
              required=True, default='both',
              type=click.Choice(['both', 'nginx', 'haproxy']), help='Service type')
@click.option('-pd', '--pid_dist',
              required=True, default='/var/run/',
              help='daemon-glb-slave.pid file location')
@click.option('-nc', '--nginx_command',
              required=True, default='service nginx reload',
              help='Nginx command.')
@click.option('-nd', '--nginx_conf_dist',
              required=True, default='/etc/nginx/',
              help='Native location of nginx config file')
@click.option('-nsd', '--nginx_ssl_dist',
              required=True, default='/etc/nginx/ssl/',
              help='Native location of nginx ssl files.')
@click.option('-nip', '--nginx_ignore_protocol',
              multiple=True,
              type=click.Choice(['http', 'ssl', 'tcp']),
              help='Service nginx unsupport protocol.')
@click.option('-hc', '--haproxy_command',
              required=True, default='service haproxy reload',
              help='Haproxy command.')
@click.option('-hd', '--haproxy_conf_dist',
              required=True, default='/etc/haproxy/',
              help='Native location of haproxy config file')
@click.option('-hsd', '--haproxy_ssl_dist',
              required=True, default='/etc/haproxy/ssl/',
              help='Native location of haproxy ssl files.')
@click.option('-hip', '--haproxy_ignore_protocol',
              multiple=True,
              type=click.Choice(['http', 'ssl', 'tcp']),
              help='Service hapaproxy unsupport protocol.')
def process(host_port, service_type, pid_dist, nginx_command,
            nginx_conf_dist, nginx_ssl_dist, nginx_ignore_protocol,
            haproxy_command, haproxy_conf_dist, haproxy_ssl_dist,
            haproxy_ignore_protocol):
    websocket_uri = "ws://%s:%s/websocket" % host_port
    if service_type == "both":
        if nginx_ignore_protocol:
            haproxy_ignore_protocol = tuple(
                set(['http', 'ssl', 'tcp']) - set(nginx_ignore_protocol))
        elif haproxy_ignore_protocol:
            nginx_ignore_protocol = tuple(
                set(['http', 'ssl', 'tcp']) - set(haproxy_ignore_protocol))
        else:
            nginx_ignore_protocol = ('tcp',)
            haproxy_ignore_protocol = ('http', 'ssl')
    p = Process(websocket_uri, service_type, pid_dist, nginx_command,
                nginx_conf_dist, nginx_ssl_dist, nginx_ignore_protocol,
                haproxy_command, haproxy_conf_dist, haproxy_ssl_dist,
                haproxy_ignore_protocol)
    print 'glb_slave service start'
    p.run()
