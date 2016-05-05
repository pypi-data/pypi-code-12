# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from jinja2 import Environment, PackageLoader

from . import parser


JENV = Environment(loader=PackageLoader('glb.haproxy', 'templates'))


def render_template(t_name, **kwargs):
    return (JENV
            .get_template(t_name)
            .render(**kwargs))


def get_config(data, unsupport_protocol):
    conf, ssl_files = parser.parse(data, unsupport_protocol)
    haproxy_conf = render_template('haproxy.cfg.jinja2', **conf)
    conf_files = {'haproxy.cfg': haproxy_conf}
    return dict(conf_files=conf_files,
                ssl_files=ssl_files)
