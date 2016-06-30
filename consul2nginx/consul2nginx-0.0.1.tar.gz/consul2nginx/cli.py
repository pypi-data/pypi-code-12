#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. module:: TODO
   :platform: Unix
   :synopsis: TODO.

.. moduleauthor:: Aljosha Friemann aljosha.friemann@gmail.com

"""

import click, logging

from .consul import Consul, Service
from .nginx import Nginx

logger = logging.getLogger(__name__)

@click.command()
@click.option('--test/--no-test', default=True, help='test the generated file before reloading nginx')
@click.option('--reload/--no-reload', default=True, help='reload nginx after file generation')
@click.option('-c', '--command', default='service nginx reload', help='use "-" to disable automatic reload')
@click.option('-o', '--output', default='/etc/nginx/nginx.conf')
@click.option('-h', '--host', default='127.0.0.1', help='consul host')
@click.option('-p', '--port', default=8500, type=int, help='consul port')
def main(test, reload, command, output, host, port):
    try:
        logger.debug('creating consul client')

        consul = Consul(host, port)

        logger.debug('checking consul connection')

        if not consul.check():
            logger.error('failed to connect to consul API via %s:%s', host, port)
            return 1

        logger.debug('creating nginx config from consul')

        Nginx.create_config(output, consul.get_services(), test)

        if reload:
            logger.debug('reloading nginx')
            Nginx.reload()

        return 0
    except Exception as e:
        logger.exception(e)
        print('unexpected Error: %s' % e)
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 fenc=utf-8
