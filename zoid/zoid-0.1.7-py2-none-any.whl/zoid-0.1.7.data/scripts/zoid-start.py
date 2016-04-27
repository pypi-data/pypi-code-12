#!python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

if __name__ == '__main__':
    import sys
    import zoid

    LOG = zoid.LOG

    zoid.ARGPARSER.add_argument("server_name", help="name of the server to start")
    zoid.ARGPARSER.add_argument("--timeout", dest="timeout", action="store", type=int, default=30, help="Duration to wait for the server to start in seconds. Defaults to 30")

    zoid.init()

    server_name = zoid.ARGS.server_name

    if not zoid.server_exists(server_name):
        LOG.error("server configuration for '%s' not exists" % server_name)
        sys.exit(-1)

    srv = zoid.get_server(server_name)

    if srv.is_running():
        LOG.error("server '%s' is allready running", server_name)
        sys.exit(-1)

    try:
        srv.start(zoid.ARGS.timeout)
    except zoid.Server.ServerAddressInUseError:
        LOG.error(sys.exc_info()[1])
    except zoid.Server.RConServerAddressInUseError:
        LOG.error(sys.exc_info()[1])
