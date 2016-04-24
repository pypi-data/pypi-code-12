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

__author__  = "David Ewelt"
__version__ = "0.1.4"
__license__ = "BSD"

import sys
import os
import shutil
import time
import json
import subprocess
import platform

import logging
import codecs

import bytesize

import uconfig
from zoid import Util, Server

MASTER_BRANCH = "master"

SERVER_EXEC_FOLDER = "bin"
SERVER_DATA_FOLDER = "srv"

CONFIG_FILE = "zoid.conf"
HOME_PATH = os.path.expanduser("~/.zoid")

STEAM_APP_ID = "380870"

#--------------------------------------------------------------------------------------------------------------------------------

ARGS = None
DEFAULT_CONFIG = None
CONFIG = None
STEAMCMD_PATH = None
STEAMCMD_EXEC = None

#--------------------------------------------------------------------------------------------------------------------------------
#-- logging
#--------------------------------------------------------------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

LOG = logging.getLogger(__name__)

Server.LOG = LOG

#--------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------

def get_used_branches():
    branches = {}
    for cfg in CONFIG.get_derived_nodes("server"):
        beta = cfg.get_value("beta", None)
        if not beta is None:
            if not beta in branches:
                branches[beta] = cfg.get_value("betapassword", None)
        else:
            if not MASTER_BRANCH in branches:
                branches[MASTER_BRANCH] = None
    return branches

def get_server_config(name):
    return CONFIG[name]

def get_server_branch(server_name):
    cfg = get_server_config(server_name)
    beta = cfg.get_value("beta")
    if not beta is None:
        return beta, cfg.get_value("betapassword", None)
    return MASTER_BRANCH, None

def get_server_exec_path(branch):
    return os.path.join(HOME_PATH, SERVER_EXEC_FOLDER, branch)

def get_server_data_path(name):
    return os.path.join(HOME_PATH, SERVER_DATA_FOLDER, name)

def get_server(name):
    """
        @rtype: Server.Server
    """
    return Server.get(name)

def get_server_configs():
    for cfg in CONFIG.get_derived_nodes("server"):
        yield cfg

def get_servers():
    for cfg in CONFIG.get_derived_nodes("server"):
        yield Server.get(cfg.name)

def get_server_addresses():
    for srv in get_server_configs():
        yield (srv.get_value("ip"), srv.get_value("port")), srv.name

def is_server_branch_in_use(branch):
    #-- get all running server processes
    for server_name,_ in Server.get_server_processes():
        server_branch, _ = get_server_branch(server_name)
        if server_branch == branch:
            return True
    return False

#--------------------------------------------------------------------------------------------------------------------------------
#-- run_steamcmd
#--------------------------------------------------------------------------------------------------------------------------------

def run_steamcmd(args=[]):
    """
        run steamcmd and return the stdout/stderr
    """

    if os.name == "nt":
        p = subprocess.Popen([STEAMCMD_EXEC] + args + ["+exit"], shell=True, cwd=STEAMCMD_PATH, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        result = p.communicate()[0]
        p.wait()
        return result.decode('utf-8')
    elif os.name == "posix":
        p = subprocess.Popen([STEAMCMD_EXEC] + args + ["+exit"], cwd=STEAMCMD_PATH, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, env=dict(os.environ, HOME=HOME_PATH))
        result = p.communicate()[0]
        p.wait()
        return result.decode('utf-8')

    #-- create lastuse.dat file
    with open(os.path.join(STEAMCMD_PATH,"lastuse.dat"), "w") as fp:
        fp.write(str(int(time.time())))

#--------------------------------------------------------------------------------------------------------------------------------
#-- validate_server_files
#--------------------------------------------------------------------------------------------------------------------------------

def validate_server_files(branch, password=None):
    """
        run steamcmd app_update for a specific branch
    """

    #-- test if a server is running this branch, server files should not changed while in use
    if is_server_branch_in_use(branch):
        LOG.error("there is a server running on the branch that should be validated (branch: %s) please stop all servers wich use this branch before updating/validating" % branch)
        return 1

    server_exec_path = get_server_exec_path(branch)

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
    validate_logfile = os.path.join(STEAMCMD_PATH, "steamcmd_validate.log")
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

#--------------------------------------------------------------------------------------------------------------------------------
#-- ensure_steamcmd
#--------------------------------------------------------------------------------------------------------------------------------

def ensure_steamcmd():
    if not os.path.exists( STEAMCMD_EXEC ):
        if os.path.exists( STEAMCMD_PATH ):
            LOG.error("steamcmd executable not found but steamcmd folder exists, this is funny, please delete the following folder and restart: '%s'", STEAMCMD_PATH)
            return 1

        LOG.info("steamcmd seems not to be installed, downloading it now")

        steamcmd_source = CONFIG["steam.steamcmd.source"].get_value(os.name, default=None)
        if steamcmd_source is None:
            LOG.error("could not get the url for steamcmd, please report this bug")
            return 1

        LOG.debug("steamcmd source is '%s'" % steamcmd_source)

        try:
            LOG.info("download started")

            local_file = os.path.join(HOME_PATH, os.path.split(steamcmd_source)[1])

            download = Util.Download(steamcmd_source, local_file)
            download.start()
            last_info = time.time()
            last_done = 0
            while download.running:
                if download.content_length == 0:
                    continue
                if time.time() - last_info > 1.0:
                    LOG.info("finished %.02f%% (%s)", (download.bytes_received/download.content_length) * 100.0, bytesize.bytesize_format(download.bytes_received-last_done, suffix="B/s"))
                    last_done = download.bytes_received
                    last_info = time.time()
            download.join()

            if not download.exception is None:
                raise download.exception

            LOG.info("download finished")

            LOG.info("extracting archive ...")
            if local_file.lower().endswith(".zip"):
                Util.unzip(local_file, STEAMCMD_PATH)
            elif local_file.lower().endswith(".tar.gz"):
                import tarfile
                with tarfile.open(local_file) as tar:
                    tar.extractall(STEAMCMD_PATH)
            else:
                LOG.error("unknown steamcmd archive type for file '%s', please report this bug", local_file)
                return 1
            LOG.info("done")
            os.remove(local_file)
        except:
            os.remove(local_file)
            LOG.exception("error while downloading steamcmd")
            return 1

    #-- run steamcmd selftest
    try:
        with open(os.path.join(STEAMCMD_PATH, "lastuse.dat"), "rb") as fp:
            last_steamcmd_use = int(fp.read())
    except:
        last_steamcmd_use = 0
    if time.time() - last_steamcmd_use > 300:
        LOG.info("i will now verify that steamcmd is working correctly ...")
        selftest_logfile = os.path.join(STEAMCMD_PATH, "steamcmd_selftest.log")
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
#-- init
#--------------------------------------------------------------------------------------------------------------------------------

def init():
    LOG.debug("init Zoid environment, os.name is %s" % os.name)

    #-- install and or update steamcmd
    retcode = ensure_steamcmd()
    if retcode != 0:
        return retcode

    #--
    #-- ensure the server files are available and valid
    #--

    for branch,password in get_used_branches().items():
        server_path = get_server_exec_path(branch)

        try:
            with open(os.path.join(server_path, "validated.dat"), "rb") as fp:
                last_validation = int(fp.read())
        except:
            last_validation = 0

        force_validation = False

        if not os.path.exists(server_path): #-- force because the server files dont exist at all
            force_validation = True

        if force_validation or time.time() - last_validation >= 300: #-- validate if last validation is 5 min ago
            retcode = validate_server_files(branch, password)
            if retcode != 0:
                return retcode
        else:
            LOG.info("last validation of server files (branch=%s) was not long ago, so i skip it. Use the '--force-validation <branch>' switch if you want to do it anyway." % branch)

    return 0

def write_default_conf(path):
    with open(path, "w") as fp:
        fp.write("""
steam {
    steamcmd {
        /*
            The URLs where SteamCMD gets downloaded from.
        */
        source {
            posix "http://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz";
            nt    "http://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip";
        }
    }
}

sandbox_settings {
    override_lua false;

    speed 3;
    zombies 3;
    distribution 1;
    survivors 1;

    day_length 2;
    start_year 1;
    start_month 7;
    start_day 9;
    start_time 2;

    water_shut_modifier 14;
    elec_shut_modifier 14;

    food_loot 2;
    weapon_loot 2;
    other_loot 2;
    temperature 3;
    rain 3;
    erosion_speed 3;

    xp_multiplier 1.0;
    stats_decrease 3;
    nature_abundance 3;

    alarm 4;
    locked_houses 6;
    food_rot_speed 3;
    fridge_factor 3;
    farming 3;
    loot_respawn 1;
    starter_kit false;
    time_since_apo 1;
    plant_resilience 3;
    plant_abundance 3;
    end_regen 3;

    zombie_lore {
        speed 2;
        strength 2;
        toughness 2;
        transmission 1;
        mortality 5;
        reanimate 3;
        cognition 3;
        memory 2;
        decomp 1;
        sight 2;
        hearing 2;
        smell 2;
        thump_no_chasing 1;
    }
}

/*
    This is the server configuration template.
    Use this to create a new server, like:

    my_server : server {
        //...
    }
*/
server {
    ip 0.0.0.0;
    port 16261;
    password;
    adminpassword;

    beta;
    betapassword;

    ping_frequency 10;
    ping_limt 400;

    max_players 64;
    max_accounts 0;

    //-- online apperance
    public false;
    public_name My Zoid PZ Server;
    public_description;

    welcome_message ' <RGB:1,0,0> Welcome to Project Zomboid MP ! to chat locally press "t", to global chat press "y" or add "/all" before chatting <LINE> Press /help to have a list of server commands <LINE> <RGB:1,1,1> ';

    //-- whitelist
    open true;
    auto_whiteList false;
    drop_whitelist false;

    //-- system
    pause_empty false;
    global_chat true;
    announce_death false;
    corpse_removal 0;
    nightlengthmodifier 1.0;
    save_world_every 0;

    minutes_per_page 1.0;

    //-- pvp / safety
    pvp true;
    safety_system true;
    show_safety true;
    safety_toggle_timer 100;
    safety_cooldown_timer 120;
    display_username true;
    allow_sledge true;

    //-- security
    kick_fast false;
    do_lua_checksum true;
    log_local_chat false;

    //-- spawn
    map Muldraugh, KY;
    spawn_regions;
    spawn_items;
    spawn_point 0,0,0;

    //-- mods
    mods;

    //-- loot respawn
    hours_for_lootrespawn 0;
    max_items_for_lootrespawn 4;
    construction_prevents_lootrespawn true;

    //-- safehouse
    safehouse {
        admin false;
        player false;
        trespass true;
        fire true;
        loot true;
        respawn false;
        claim 0;
        removal 144;
    }

    //-- fire
    no_fire false;
    no_fire_spread false;

    //-- steam
    steam {
        enable false;
        port1 8766;
        port2 8767;
        vac true;
        scoreboard true;
        workshop_items;
    }

    rcon {
        port 28015;
        password;
    }

    sandbox : sandbox_settings {
    }

    vm {
        xms 2048m;
        xmx 2048m;
    }

    reset_id;
    server_player_id;
}

/*
    Include all *.conf files.
*/
include *.conf;
    """)

#--------------------------------------------------------------------------------------------------------------------------------
#-- main
#--------------------------------------------------------------------------------------------------------------------------------

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    global CONFIG_FILE
    global HOME_PATH
    global ARGS
    global DEFAULT_CONFIG
    global CONFIG
    global STEAMCMD_PATH
    global STEAMCMD_EXEC

    import argparse
    parser = argparse.ArgumentParser(description='Zoid Commandline Interface (c) David "Uranoxyd" Ewelt')

    parser.add_argument('-cfg',  '--config',  action='store',                             dest="config",           default=None, metavar='FILE', help='configuration file')
    parser.add_argument(         '--home',    action='store',                             dest="home",             default=None, help='home directory')

    parser.add_argument('-v',    '--verbose', action='store_true',                        dest="verbose",                        help='show debug messages')

    parser.add_argument(         '--init',    action='store_const', const="init",         dest="action",                         help='initialize environment')
    parser.add_argument('-ls',   '--list',    action='store_const', const="list_servers", dest="action",                         help='list servers')
    parser.add_argument('-V',    '--version', action='store_const', const="show_version", dest="action",                         help='show the zoid version')

    parser.add_argument('--create-home',      action='store_true',                        dest="create_home",      default=[],   help='force creation of the home directory if not existing')

    parser.add_argument('--validate-branch',  action='append',                            dest="validate_branch",  default=[],   metavar='BRANCH',  help='validate server files for a specific branch')
    parser.add_argument('--beta-password',    action='store',                             dest="beta_password",    default=None, help='set the beta password, may needed for "--validate-branch" switch')

    parser.add_argument('--validate-server',  action='append',                            dest="validate_server",  default=[],   metavar='SERVER',  help='validate server files for a specific server')

    parser.add_argument(         '--start',   action='append',                            dest="start_server",     default=[],   metavar='SERVER',  help='start server instances')
    parser.add_argument(         '--stop',    action='append',                            dest="stop_server",      default=[],   metavar='SERVER',  help='stop server instances')
    parser.add_argument(         '--kill',    action='append',                            dest="kill_server",      default=[],   metavar='SERVER',  help='kill server instances')
    parser.add_argument(         '--restart', action='append',                            dest="restart_server",   default=[],   metavar='SERVER',  help='stop server instances')
    parser.add_argument(         '--rcon',    action='store',                             dest="rcon_command",     default=None, metavar='COMMAND', help='send rcon command to a server')

    ARGS = parser.parse_args(argv)

    if ARGS.verbose:
        LOG.setLevel(logging.DEBUG)

    LOG.info('Zoid Commandline Interface (c) David "Uranoxyd" Ewelt. Version: %s', __version__)
    LOG.debug("architecture: %s", platform.architecture())
    LOG.debug("machine: %s", platform.machine())
    LOG.debug("argv: %s", argv)

    #-- test platform
    if not os.name in ("posix", "nt"):
        LOG.error("your platform '%s' is not supported, please report this error" % os.name)
        return 1

    if not ARGS.home is None:
        LOG.debug("overriding home path from config with command line arg")
        HOME_PATH = ARGS.home

    HOME_PATH = HOME_PATH.strip()
    if len(HOME_PATH) == 0:
        LOG.error("home path is not set, please set it via the --home switch")
        return 1

    #-- expand and get absolute home path
    HOME_PATH = os.path.abspath( os.path.expanduser( os.path.expandvars( HOME_PATH ) ) )

    LOG.debug("home path: %s", HOME_PATH)
    #-- test if the home folder exists
    if not os.path.exists(HOME_PATH):
        if ARGS.create_home:
            os.makedirs(HOME_PATH)
            LOG.info("home directory '%s' created." % HOME_PATH)
        else:
            LOG.error("home path '%s' dont exists, please ensure it exists." % HOME_PATH)
            return 1

    CONFIG_FILE = os.path.join(HOME_PATH, "zoid.conf")

    #-- create default config if not exists
    if not os.path.exists(CONFIG_FILE):
        LOG.debug("creating default configuration file: %s", CONFIG_FILE)
        write_default_conf(CONFIG_FILE)

    try:
        CONFIG = uconfig.ExtendedConfig()

        #-- load config file
        if not ARGS.config is None:
            CONFIG_FILE = os.path.abspath( os.path.expanduser(ARGS.config) )

            if not os.path.exists(CONFIG_FILE):
                LOG.error("configuration file '%s' dont exists" % CONFIG_FILE)
                sys.exit(1)

            LOG.debug("config file: %s", CONFIG_FILE)
            LOG.debug("loading user configuration")
            CONFIG.load(CONFIG_FILE)
        elif os.path.exists(CONFIG_FILE):
            LOG.debug("config file: %s", CONFIG_FILE)
            LOG.debug("loading user configuration")
            CONFIG.load(CONFIG_FILE)
    except:
        LOG.exception("configuration could not loaded")
        return 1

    STEAMCMD_PATH = os.path.join(HOME_PATH, "steamcmd")
    LOG.debug("STEAMCMD_PATH=%s", STEAMCMD_PATH)
    if os.name == "nt":
        STEAMCMD_EXEC = os.path.join(STEAMCMD_PATH, "steamcmd.exe")
    elif os.name == "posix":
        STEAMCMD_EXEC = os.path.join(STEAMCMD_PATH, "steamcmd.sh")
    LOG.debug("STEAMCMD_EXEC=%s", STEAMCMD_EXEC)

    #--------------------------------------------------------------------------------------------------------------------------------
    #-- process the commands
    #--------------------------------------------------------------------------------------------------------------------------------

    #-- process "--validate-branch <branch>" switches
    for branch in ARGS.validate_branch:
        retcode = validate_server_files(branch, ARGS.beta_password)
        if retcode != 0:
            return retcode

    #-- process "--validate-server <name>" switches
    for server_name in ARGS.validate_server:
        if not server_name in CONFIG:
            LOG.error("server configuration for '%s' not exists" % server_name)
            continue

        branch, password = get_server_branch(server_name)
        retcode = validate_server_files(branch, password)
        if retcode != 0:
            return retcode

    #-- process "--start <name>" switches
    for server_name in ARGS.start_server:
        if not server_name in CONFIG:
            LOG.error("server configuration for '%s' not exists" % server_name)
            continue

        srv = Server.get(server_name)

        if srv.is_running():
            LOG.error("server '%s' is allready running", server_name)
            return

        srv.start()

    #-- process "--stop <name>" switches
    for server_name in ARGS.stop_server:
        if not server_name in CONFIG:
            LOG.error("server configuration for '%s' not exists" % server_name)
            continue

        srv = Server.get(server_name)

        if not srv.is_running():
            LOG.error("server '%s' is not running", server_name)
            return

        srv.stop()

    #-- process "--kill <name>" switches
    for server_name in ARGS.kill_server:
        if not server_name in CONFIG:
            LOG.error("server configuration for '%s' not exists" % server_name)
            continue

        srv = Server.get(server_name)

        if not srv.is_running():
            LOG.error("server '%s' is not running", server_name)
            return

        srv.kill()

    #-- process "--restart <name>" switches
    for server_name in ARGS.restart_server:
        if not server_name in CONFIG:
            LOG.error("server configuration for '%s' not exists" % server_name)
            continue

        srv = Server.get(server_name)
        srv.stop()
        srv.start()

    if ARGS.action == "show_version":
        print(__version__)
    elif ARGS.action == "init":
        return init()
    elif ARGS.action == "list_servers":
        print("-"*80)
        print("%- 16s %- 15s %- 8s %s" % ("name", "ip", "port", "branch") )
        print("-"*80)
        for cfg in CONFIG.get_derived_nodes("server"):
            branch = cfg.get_value("beta")
            if branch is None:
                branch = MASTER_BRANCH
            print("%- 16s %- 15s %- 8s %s" % (cfg.name, cfg.get_value("ip"), cfg.get_value("port"), branch) )

