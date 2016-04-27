#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

if __name__ == '__main__':
    import sys
    import zoid

    LOG = zoid.LOG

    zoid.ARGPARSER.add_argument("server_name", help="Name of the server to stop")
    zoid.ARGPARSER.add_argument("-f", "--force", dest="force", action="store_true", help="Kill server if a gracefull shutdown fails")
    zoid.ARGPARSER.add_argument("--timeout", dest="timeout", action="store", type=int, default=30, help="Duration to wait for the server to shutdown gracefully in seconds. Defaults to 30")

    zoid.init()

    server_name = zoid.ARGS.server_name

    if not zoid.server_exists(server_name):
        LOG.error("server configuration for '%s' not exists" % server_name)
        sys.exit(-1)

    srv = zoid.get_server(server_name)

    if not srv.is_running():
        LOG.error("server '%s' is not running", server_name)
        sys.exit(-1)

    if not srv.stop(zoid.ARGS.timeout) and zoid.ARGS.force:
        LOG.warn("could not gracefully shutdown the server, killing it now because the --force switch was set")
        srv.kill()

    srv.start()
