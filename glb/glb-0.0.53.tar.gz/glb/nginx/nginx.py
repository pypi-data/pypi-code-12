# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from jinja2 import Environment, PackageLoader

from . import parser


JENV = Environment(loader=PackageLoader('glb.nginx', 'templates'))


def render_template(template_name, **kwargs):
    return (JENV
            .get_template(template_name)
            .render(**kwargs))


def get_config(data, unsupport_protocol):
    http_conf_file_name = "glb_cluster_http.conf"
    tcp_conf_file_name = "glb_cluster_tcp.conf"
    http_vals, tcp_vals, ssl_files = parser.parse(data, unsupport_protocol)
    http_conf = render_template('http.conf.jinja2', **http_vals)
    tcp_conf = render_template('tcp.conf.jinja2', **tcp_vals)
    http_files = {http_conf_file_name: http_conf}
    tcp_files = {tcp_conf_file_name: tcp_conf}
    cf_names = dict(tcp=tcp_conf_file_name)
    return dict(http_files=http_files,
                tcp_files=tcp_files,
                ssl_files=ssl_files,
                cf_names=cf_names)
