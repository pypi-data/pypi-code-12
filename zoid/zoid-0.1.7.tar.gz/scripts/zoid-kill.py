#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

if __name__ == '__main__':
    import sys
    import zoid

    LOG = zoid.LOG

    zoid.ARGPARSER.add_argument("server_name", help="Name of the server to stop")

    zoid.init()

    server_name = zoid.ARGS.server_name

    if not zoid.server_exists(server_name):
        LOG.error("server configuration for '%s' not exists" % server_name)
        sys.exit(-1)

    srv = zoid.get_server(server_name)

    if not srv.is_running():
        LOG.error("server '%s' is not running", server_name)
        sys.exit(-1)

    srv.kill()
