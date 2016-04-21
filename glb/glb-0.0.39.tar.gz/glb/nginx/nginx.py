# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from jinja2 import Environment, PackageLoader

from . import parser


JENV = Environment(loader=PackageLoader('glb.nginx', 'templates'))


def render_template(template_name, **kwargs):
    return (JENV
            .get_template(template_name)
            .render(**kwargs))


def get_config(data):
    conf, ssl_files = parser.parse(data, protocol_support=['http', 'ssl'])
    glb_cluster_conf = render_template('glb_cluster.conf.jinja2', **conf)
    conf_files = {'glb_cluster.conf': glb_cluster_conf}
    return dict(conf_files=conf_files,
                ssl_files=ssl_files)
