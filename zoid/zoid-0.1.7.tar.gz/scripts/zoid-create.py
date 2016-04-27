#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

if __name__ == '__main__':
    import sys, os
    import zoid
    from zoid import Util

    LOG = zoid.LOG

    zoid.ARGPARSER.add_argument("server_name", help="name of the server to start")

    zoid.init()

    server_name = zoid.ARGS.server_name

    if zoid.server_exists(server_name):
        LOG.error("server configuration for '%s' allready exists" % server_name)
        sys.exit(-1)

    with open(os.path.join(zoid.HOME_PATH, "%s.conf"%server_name), "w") as fp:
        fp.write("""%(name)s : server {
    adminpassword %(adminpass)s;

    rcon {
        password %(rconpass)s;
    }
}""" % {
            "name": server_name,
            "adminpass": Util.create_password(32),
            "rconpass": Util.create_password(32)
        })

    LOG.info("server configuration file for server '%s' created", server_name)
