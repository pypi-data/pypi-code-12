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
__version__ = "0.2.1"
__license__ = "BSD"

import sys
import os
import shutil
import time
import json
import subprocess
import platform
import argparse
import logging
import codecs

import uconfig

#--------------------------------------------------------------------------------------------------------------------------------

SERVER_EXEC_FOLDER = "bin"
SERVER_DATA_FOLDER = "srv"

CONFIG_FILE = "zoid.conf"
HOME_PATH = os.path.expanduser("~/.zoid")

#--------------------------------------------------------------------------------------------------------------------------------

ARGS = None
DEFAULT_CONFIG = None
CONFIG = None
STEAMCMD_PATH = None
STEAMCMD_EXEC = None

#--------------------------------------------------------------------------------------------------------------------------------

from zoid import Util, Steam, Server
from zoid.Steam import MASTER_BRANCH

ARGPARSER = argparse.ArgumentParser(description='Zoid Commandline Interface (c) David "Uranoxyd" Ewelt')

ARGPARSER.add_argument(         '--config',  action='store',                             dest="config",           default=None, metavar='FILE', help='configuration file')
ARGPARSER.add_argument(         '--home',    action='store',                             dest="home",             default=None,  help='home directory')
ARGPARSER.add_argument('-v',    '--verbose', action='store_true',                        dest="verbose",                         help='show debug messages')
ARGPARSER.add_argument('-V',    '--version', action='store_const', const="show_version", dest="action",                          help='show the zoid version')
ARGPARSER.add_argument(     "--create-home", action="store_true",                        dest="create_home",      default=False, help="Create the home directory if not exist")

#--------------------------------------------------------------------------------------------------------------------------------
#-- logging
#--------------------------------------------------------------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

LOG = logging.getLogger(__name__)

Server.LOG = LOG
Steam.LOG = LOG

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

def server_exists(name):
    for cfg in CONFIG.get_derived_nodes("server"):
        if cfg.name == name:
            return True
    return False

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
#-- write_default_conf
#--------------------------------------------------------------------------------------------------------------------------------

def write_default_conf(path):
    with open(path, "w") as fp:
        fp.write("""steam {
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
        enable true;
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

    sandbox {
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

def init(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    global ARGPARSER
    global CONFIG_FILE
    global HOME_PATH
    global ARGS
    global DEFAULT_CONFIG
    global CONFIG
    global STEAMCMD_PATH
    global STEAMCMD_EXEC

    ARGS = ARGPARSER.parse_args(argv)

    if ARGS.verbose:
        LOG.setLevel(logging.DEBUG)

    LOG.info('Zoid by David "Uranoxyd" Ewelt. Version: %s', __version__)

    LOG.debug("os name: %s", os.name)
    LOG.debug("architecture: %s", platform.architecture())
    LOG.debug("machine: %s", platform.machine())
    LOG.debug("working directory: %s", os.path.abspath(os.curdir))
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
        if ARGS.create_home: # --create-home is set
            os.makedirs(HOME_PATH)
            LOG.info("home directory '%s' created." % HOME_PATH)
        else:
            LOG.error("home path '%s' dont exists, please ensure it exists." % HOME_PATH)
            return 1

    #-- create file logger
    file_log_handler = logging.FileHandler(os.path.join(HOME_PATH, "zoid.log"))
    file_log_handler.setFormatter(logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'))
    file_log_handler.setLevel(logging.DEBUG)
    LOG.addHandler(file_log_handler)

    CONFIG_FILE = os.path.join(HOME_PATH, "zoid.conf")

    #-- create default config if not exists
    if not os.path.exists(CONFIG_FILE):
        LOG.debug("creating default configuration file: %s", CONFIG_FILE)
        write_default_conf(CONFIG_FILE)

    try:
        CONFIG = uconfig.ExtendedConfig()

        #-- load config file
        if not ARGS.config is None: # --config switch is set
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

    if ARGS.action == "show_version":
        sys.exit(0)
