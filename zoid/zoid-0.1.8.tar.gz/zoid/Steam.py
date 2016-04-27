#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2016, David Ewelt
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from __future__ import unicode_literals, print_function, division

import os
import subprocess
import time

import bytesize

import zoid
from zoid import Util
LOG = None

STEAM_APP_ID = "380870"
MASTER_BRANCH = "master"

#--------------------------------------------------------------------------------------------------------------------------------
#-- ensure_steamcmd
#--------------------------------------------------------------------------------------------------------------------------------

def ensure_steamcmd():
    if not os.path.exists( zoid.STEAMCMD_EXEC ):
        if os.path.exists( zoid.STEAMCMD_PATH ):
            LOG.error("steamcmd executable not found but steamcmd folder exists, this is funny, please delete the following folder and restart: '%s'", zoid.STEAMCMD_PATH)
            return 1

        LOG.info("steamcmd seems not to be installed, downloading it now")

        steamcmd_source = zoid.CONFIG["steam.steamcmd.source"].get_value(os.name, default=None)
        if steamcmd_source is None:
            LOG.error("could not get the url for steamcmd, please report this bug")
            return 1

        LOG.debug("steamcmd source is '%s'" % steamcmd_source)

        try:
            local_file = os.path.join(zoid.HOME_PATH, os.path.split(steamcmd_source)[1])

            download = Util.Download(steamcmd_source, local_file)
            download.start()
            t_start = time.time()
            last_info = time.time()
            last_done = 0
            while download.running:
                if download.content_length == 0:
                    continue
                if time.time()-t_start >= 2.0 and time.time()-last_info >= 1.0: #-- show info every second but just after two seconds since start
                    LOG.info("finished %.02f%% (%s)", (download.bytes_received/download.content_length) * 100.0, bytesize.bytesize_format((download.bytes_received-last_done)/(time.time()-last_info), suffix="B/s"))
                    last_done = download.bytes_received
                    last_info = time.time()
            download.join()

            if not download.exception is None:
                raise download.exception

            LOG.info("download finished. loaded %s with %s", bytesize.bytesize_format(download.bytes_received), bytesize.bytesize_format(download.bytes_received/(time.time()-t_start), suffix="B/s"))

            if local_file.lower().endswith(".zip"):
                Util.unzip(local_file, zoid.STEAMCMD_PATH)
            elif local_file.lower().endswith(".tar.gz"):
                import tarfile
                with tarfile.open(local_file) as tar:
                    tar.extractall(zoid.STEAMCMD_PATH)
            else:
                LOG.error("unknown steamcmd archive type for file '%s', please report this bug", local_file)
                return 1
            os.remove(local_file)
        except:
            os.remove(local_file)
            LOG.exception("error while downloading steamcmd")
            return 1

    #-- run steamcmd selftest
    try:
        with open(os.path.join(zoid.STEAMCMD_PATH, "lastuse.dat"), "rb") as fp:
            last_steamcmd_use = int(fp.read())
    except:
        last_steamcmd_use = 0
    if time.time() - last_steamcmd_use > 300:
        LOG.info("i will now verify that steamcmd is working correctly ...")
        selftest_logfile = os.path.join(zoid.STEAMCMD_PATH, "steamcmd_selftest.log")
        selftest_result = run_steamcmd(["+login", "anonymous", "+info"])
        with open(selftest_logfile, "wb") as fp:
            fp.write(selftest_result.encode("utf-8"))
        if not "Account: anonymous" in selftest_result or \
           not "Logon state: Logged On" in selftest_result:
            LOG.error("mhm, seems steamcmd dont work like expected, a log was written to '%s' please report this bug" % selftest_logfile)
            return 1

        LOG.info("joy! steamcmd seems working just fine :)")
    else:
        pass

    return 0

#--------------------------------------------------------------------------------------------------------------------------------
#-- run_steamcmd
#--------------------------------------------------------------------------------------------------------------------------------

def run_steamcmd(args=[]):
    """
        run steamcmd and return the stdout/stderr
    """

    if os.name == "nt":
        p = subprocess.Popen([zoid.STEAMCMD_EXEC] + args + ["+exit"], shell=True, cwd=zoid.STEAMCMD_PATH, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        result = p.communicate()[0]
        p.wait()
        return result.decode('utf-8')
    elif os.name == "posix":
        p = subprocess.Popen([zoid.STEAMCMD_EXEC] + args + ["+exit"], cwd=zoid.STEAMCMD_PATH, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, env=dict(os.environ, HOME=zoid.HOME_PATH))
        result = p.communicate()[0]
        p.wait()
        return result.decode('utf-8')

    #-- create lastuse.dat file
    with open(os.path.join(zoid.STEAMCMD_PATH,"lastuse.dat"), "w") as fp:
        fp.write(str(int(time.time())))

#--------------------------------------------------------------------------------------------------------------------------------
#-- validate_server_files
#--------------------------------------------------------------------------------------------------------------------------------

def validate_server_files(branch, password=None):
    """
        run steamcmd app_update for a specific branch
    """

    #-- test if a server is running this branch, server files should not changed while in use
    if zoid.is_server_branch_in_use(branch):
        LOG.error("there is a server running on the branch that should be validated (branch: %s) please stop all servers wich use this branch before updating/validating" % branch)
        return 1

    server_exec_path = zoid.get_server_exec_path(branch)

    if os.path.exists(os.path.join(server_exec_path,"validated.dat")):
        LOG.debug("deleting 'validated.dat' file")
        os.remove(os.path.join(server_exec_path,"validated.dat"))

    LOG.info("steamcmd will now validating and/or downloading the server files for the '%s' branch, this may take a while ..." % branch)

    args = [
        "+login", "anonymous",
        "+force_install_dir", server_exec_path,
        "+app_update", STEAM_APP_ID
    ]

    #-- append beta args if branch is not master
    if branch != MASTER_BRANCH:
        args += ["-beta", branch]
        if not password is None:
            args += "-betapassword", password

    #-- append validate
    args.append("validate")

    #-- run steamcmd
    validate_result = run_steamcmd(args)

    #-- write result log file
    validate_logfile = os.path.join(zoid.STEAMCMD_PATH, "steamcmd_validate.log")
    with open(validate_logfile, "wb") as fp:
        fp.write(validate_result.encode("utf-8"))

    #-- test the result string for some nice strings wich tell us about the validation success
    if not "Success! App '%s' fully installed."%STEAM_APP_ID in validate_result:
        LOG.error("doh! steamcmd seems could not validate the server files, a log was written to '%s'" % validate_logfile)
        LOG.info("if your error is something like: './steamcmd.sh: line 29: /steamcmd/linux32/steamcmd: No such file or directory' you might have a recent x64 system like ubuntu or debian jessie. In this case you need to run 'apt-get install lib32gcc1' before using zoid.")

        return 1

    LOG.info("validation successfull :]")

    #-- create validated.dat file
    with open(os.path.join(server_exec_path,"validated.dat"), "w") as fp:
        fp.write(str(int(time.time())))

    return 0
