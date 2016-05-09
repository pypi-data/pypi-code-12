#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from glb.settings import Config


def __parse_name(balancer_name):
    names = balancer_name.split("_")
    name = ".".join(names)
    return name, "%s.%s" % (name, Config.GLB_URL)


def __parse_upstream(name, backends):
    servs = ["%s:%s" % (backend['address'], backend['port'])
             for backend in backends]
    return dict(name=name, servers=servs)


def __parse_server(name, default_domain, frontend, backends, entrypoints):
    server = dict(name=name,
                  listens=set(),
                  server_names=set([default_domain]),
                  pattern='/',
                  has_ssl=False)
    ssl_file = {}
    protocol = frontend.get("protocol", "http")
    port = frontend.get("port", 80)

    def parse_entrypoints():
        ssl_certificate_list = set()
        ssl_certificate_key_list = set()

        for entrypoint in entrypoints:
            domain = entrypoint.get('domain', None)
            if domain:
                server['server_names'].add(domain)
            if entrypoint['protocol'] == 'ssl':
                server['listens'].add((443, True))
                certificate = entrypoint.get('certificate', {})
                ssl_certificate_list.add(certificate['certificate_chain'])
                ssl_certificate_key_list.add(certificate['private_key'])
            else:
                server['listens'].add((80, False))
        if ssl_certificate_list:
            ssl_file.setdefault("%s.crt" % name,
                                "\n".join(ssl_certificate_list))
            ssl_file.setdefault("%s.key" % name,
                                "\n".join(ssl_certificate_key_list))
    if protocol == "tcp":
        server['listens'].add((port, False))
    else:
        if protocol == "ssl":
            server['listens'].add((443, False))
        else:
            server['listens'].add((80, False))
        parse_entrypoints()
    return server, ssl_file


def __parse_balancer(balancer):
    name, default_domain = __parse_name(balancer.name)
    frontend = getattr(balancer, 'frontend', {})
    backends = getattr(balancer, 'backends', [])
    entrypoints = getattr(balancer, 'entrypoints', [])

    upstream = __parse_upstream(name, backends)
    server, ssl_file = __parse_server(name, default_domain,
                                      frontend, backends, entrypoints)
    return upstream, server, ssl_file


def parse(data, unsupport_protocol):
    if not data:
        data = []
    http_vals = {}
    tcp_vals = {}
    ssl_files = {}

    for balancer in data:
        protocol = balancer.frontend.get('protocol', 'http')
        backends = getattr(balancer, 'backends', [])
        if not backends:
            continue
        if protocol in unsupport_protocol:
            continue
        upstream, server, ssl_file = __parse_balancer(balancer)
        if protocol == 'tcp':
            tcp_vals.setdefault('upstreams', []).append(upstream)
            tcp_vals.setdefault('servers', []).append(server)
        else:
            http_vals.setdefault('upstreams', []).append(upstream)
            http_vals.setdefault('servers', []).append(server)
            ssl_files.update(ssl_file)
    http_vals.setdefault('upstreams', []).sort(key=lambda ups: ups['name'])
    tcp_vals.setdefault('upstreams', []).sort(key=lambda ups: ups['name'])
    return http_vals, tcp_vals, ssl_files
