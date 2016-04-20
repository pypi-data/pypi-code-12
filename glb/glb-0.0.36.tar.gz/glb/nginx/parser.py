#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from glb.settings import Config


def __default_name(name):
    names = name.split("_")
    names.append(Config.GLB_URL)
    return ".".join(names)


def __parse_upstream(name, backends):
    servs = ["%s:%s" % (backend['address'], backend['port'])
             for backend in backends]
    return dict(name=name,
                servers=servs)


def __parse_server(name, upstream_name, backends, entrypoints):
    listens = []
    server_names = [name]
    proxy_pass = "http://%s" % upstream_name
    ssl_file = {}
    default_server = False if backends else True
    listens.append((80, default_server, False))

    def parse_entrypoints():
        ssl_certificate_list = set()
        ssl_certificate_key_list = set()

        for entrypoint in entrypoints:
            server_names.append(entrypoint['domain'])
            if entrypoint['protocol'] == 'ssl':
                listens.append((443, default_server, True))
                certificate = entrypoint.get('certificate', {})
                ssl_certificate_list.add(certificate['certificate_chain'])
                ssl_certificate_key_list.add(certificate['private_key'])
        if ssl_certificate_list:
            ssl_certificate = '%s.crt' % name
            ssl_certificate_key = '%s.key' % name
            ssl_certificate_content = "\n".join(ssl_certificate_list)
            ssl_certificate_key_content = "\n".join(ssl_certificate_key_list)
            ssl_file.update({ssl_certificate: ssl_certificate_content,
                              ssl_certificate_key: ssl_certificate_key_content})
    parse_entrypoints()
    server = dict(name=name,
                  listens=listens,
                  server_names=server_names,
                  proxy_pass=proxy_pass,
                  pattern='/',
                  has_ssl=True if ssl_file else False)
    return server, ssl_file


def __parse_balancer(balancer):
    default_name = __default_name(balancer.name)
    upstream_name = '%s_upstream' % default_name
    backends = getattr(balancer, 'backends', [])
    entrypoints = getattr(balancer, 'entrypoints', [])

    if backends:
        return {}, {}, {}
    upstream = __parse_upstream(upstream_name, backends)
    server, ssl_file = __parse_server(default_name, upstream_name, backends, entrypoints)
    return upstream, server, ssl_file


def parse(data, protocol_support):
    if not data:
        data = []
    upstreams = []
    servers = []
    ssl_files = {}

    for balancer in data:
        protocol = balancer.frontend['protocol']
        if protocol in protocol_support:
            upstream, server, ssl_file = __parse_balancer(balancer)
            upstreams.append(upstream)
            servers.append(server)
            ssl_files.update(ssl_file)
    upstreams.sort(key=lambda ups: ups['name'])
    return dict(upstreams=upstreams, servers=servers), ssl_files
