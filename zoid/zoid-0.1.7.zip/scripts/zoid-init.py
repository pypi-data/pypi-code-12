#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

if __name__ == '__main__':
    import sys, os, time
    import zoid

    LOG = zoid.LOG

    zoid.init()

    LOG.debug("init Zoid environment, os.name is %s" % os.name)

    #-- install and or update steamcmd
    retcode = zoid.Steam.ensure_steamcmd()
    if retcode != 0:
        sys.exit(retcode)

    #--
    #-- ensure the server files are available and valid
    #--

    for branch,password in zoid.get_used_branches().items():
        server_path = zoid.get_server_exec_path(branch)

        try:
            with open(os.path.join(server_path, "validated.dat"), "rb") as fp:
                last_validation = int(fp.read())
        except:
            last_validation = 0

        force_validation = False

        if not os.path.exists(server_path): #-- force because the server files dont exist at all
            force_validation = True

        if force_validation or time.time() - last_validation >= 300: #-- validate if last validation is 5 min ago
            retcode = zoid.Steam.validate_server_files(branch, password)
            if retcode != 0:
                sys.exit(retcode)
        else:
            LOG.info("last validation of server files (branch=%s) was not long ago, so i skip it. Use the '--force-validation <branch>' switch if you want to do it anyway." % branch)
