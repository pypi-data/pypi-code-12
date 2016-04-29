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
import re
import time
import subprocess
import socket
import platform
import json
from datetime import datetime

import zoid
from zoid.IS import ServerConfiguration
from zoid.SourceRcon import SourceRcon
from zoid import Util

LOG = None

def is_address_in_use(address, protocol=socket.SOCK_DGRAM):
    try:
        s = socket.socket(socket.AF_INET, protocol)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
        s.bind(address)
    except socket.error as e:
        if e.errno in (10048, 10013): #-- windows
            return True
        elif e.errno in (98,): #-- linux
            return True
        else:
            raise
    finally:
        s.close()
    return False

def get_server_processes():
    """
        yields (server_name, pid) for all running servers
    """

    if os.name == "nt":
        for e in Util.get_processes():
            if "zombie.network.GameServer" in e["cmd"]:
                a = e["cmd"].split(" ")
                if "cmd.exe" in a[0]:
                    continue
                yield a[-1], e["pid"]
    elif os.name == "posix":
        for e in Util.get_processes():
            if "start-server.sh" in e["cmd"] and "-servername" in e["cmd"]:
                a = e["cmd"].split(" ")
                yield a[-1], e["pid"]

def write_spawnregions_lua(path):
    with open(path, "w") as fp:
        fp.write("""-- This file was automatically generated when the server was first started.
-- Clients connecting to the server can choose to spawn in one of the following spawn regions.
-- The administrator can add as many different spawn regions as he/she wants.
function SpawnRegions()
    return {
        { name = "Muldraugh, KY", file = "media/maps/Muldraugh, KY/spawnpoints.lua" },
        { name = "West Point, KY", file = "media/maps/West Point, KY/spawnpoints.lua" },
        -- Uncomment the line below to add a custom spawnpoint for this server.
--        { name = "Twiggy's Bar", serverfile = "road_one_spawnpoints.lua" },
    }
end
""")

class ServerValidationError(Exception):
    pass
class ServerConfigValidationError(ServerValidationError):
    pass

class ServerAddressInUseError(Exception):
    def __init__(self, address):
        Exception.__init__(self, "the server address '%s:%s' is allready in use" % address)

class RConServerAddressInUseError(Exception):
    def __init__(self, address):
        Exception.__init__(self, "the RCon server address '%s:%s' is allready in use" % address)

class ServerRunningError(Exception):
    def __init__(self, msg="Server is allready running"):
        Exception.__init__(self, msg)

class ServerNotRunningError(Exception):
    def __init__(self, msg="Server is not running"):
        Exception.__init__(self, msg)

class Server(object):
    instances = {}

    @staticmethod
    def get(name):
        if not name in Server.instances:
            server = Server(name)
            Server.instances[name] = server
            LOG.debug("created new server instance %s for '%s'" % (server, name))
        else:
            server = Server.instances[name]

        server.validate()

        return server

    def __init__(self, name):
        self.name = name
        self.cfg = zoid.CONFIG[name]

    def validate_config(self):
        #-- ip
        if not self.cfg.has_value("ip"):
            raise ServerConfigValidationError("missing 'ip' config entry for server '%s'" % (self.name))
        if not re.match("[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", self.cfg.get_value("ip", "")):
            raise ServerConfigValidationError("'ip' config entry for server '%s' has a invalid value" % (self.name))

        #-- port
        if not self.cfg.has_value("port"):
            raise ServerConfigValidationError("missing 'port' config entry for server '%s'" % (self.name))
        if not re.match("[0-9]{1,6}", self.cfg.get_value("port", "")):
            raise ServerConfigValidationError("'port' config entry for server '%s' has a invalid value" % (self.name))

        #-- admin password
        if not self.cfg.has_value("adminpassword"):
            raise ServerConfigValidationError("missing 'adminpassword' config entry for server '%s'" % (self.name))
        if not re.match("[A-Za-z0-9]+", self.cfg.get_value("adminpassword", "")):
            raise ServerConfigValidationError("'adminpassword' config entry for server '%s' has a invalid value" % (self.name))

        #-- rcon
        if not "rcon" in self.cfg:
            raise ServerConfigValidationError("missing 'rcon' config section for server '%s'" % (self.name))
        if not self.cfg["rcon"].has_value("port"):
            raise ServerConfigValidationError("missing 'rcon.port' config entry for server '%s'" % (self.name))
        if not re.match("[0-9]{1,6}", self.cfg["rcon"].get_value("port", "")):
            raise ServerConfigValidationError("'rcon.port' config entry for server '%s' has a invalid value" % (self.name))
        if not re.match("[A-Za-z0-9]+", self.cfg["rcon"].get_value("password", "")):
            raise ServerConfigValidationError("'rcon.password' config entry for server '%s' has a invalid value. Zoid cant work without the RCon functionality, so please activate ist by setting a valid port and password" % (self.name))

    def validate(self):
        p = self.get_exec_path()
        if not os.path.exists(p):
            branch, password = self.get_branch()
            LOG.warn("could not find the server executable for the branch '%s' for server '%s', installing it now" % (branch, self.name))
            zoid.Steam.validate_server_files(branch, password)

        if not os.path.exists( os.path.join(p, "validated.dat") ):
            raise ServerValidationError("could not find the 'validated.dat' file, please run '--validate-server %s'" % self.name)

        self.validate_config()

    def get_ip(self):
        return self.cfg.get_value("ip")

    def get_port(self):
        return self.cfg.get_int("port")

    def get_address(self):
        return self.get_ip(), self.get_port()

    def get_branch(self):
        return zoid.get_server_branch(self.name)

    def get_data_path(self):
        return zoid.get_server_data_path(self.name)

    def get_exec_path(self):
        return zoid.get_server_exec_path(self.get_branch()[0])

    def get_pid(self):
        server_processes = dict( get_server_processes() )
        return server_processes.get(self.name, 0)

    def is_running(self):
        return self.get_pid() != 0

    def get_connections(self):
        """
            Get a nice list of player connections to the server

            @rtype: list

            Example Result:

            ::

                [
                    {
                        u'username': u'Uranoxyd',
                        u'steam_id': u'76561198074635135',
                        u'coop_num': [1, 4],
                        u'connection': [1, 1],
                        u'fully_connected': True,
                        u'id': 0
                    }
                ]
        """

        if not self.is_running():
            return []

        result = []
        connections = self.rcon("connections").split("\n")[:-1]
        for c in connections:
            connection_num, steamid, coop_num, uid, username, fully_connected = [ d.split("=",1) for d in c.split(" ") ]
            result.append({
                "connection": [ int(c) for c in connection_num[1].split("/",1) ],
                "steam_id": steamid[0],
                "coop_num": [ int(c) for c in coop_num[1].split("/",1) ],
                "id": int(uid[1]),
                "username": json.loads(username[1]),
                "fully_connected": fully_connected[1] == "true"
            })
        return result

    def _update_server_ini(self):
        """
            writes the zomboid servername.ini file with the settings from the server configuration
        """

        ini_path = os.path.join(self.get_data_path(), "Zomboid", "Server")
        if not os.path.exists(ini_path):
            LOG.debug("server ini path dont exist, creating it now")
            os.makedirs(ini_path)

        ini = ServerConfiguration()

        ini_file = os.path.join(ini_path, "%s.ini"%self.name)
        if os.path.exists(ini_file):
            with open(os.path.join(ini_path, "%s.ini"%self.name), "rb") as fp:
                ini.read(fp)

        ini["nightlengthmodifier"]             = self.cfg.get_float("nightlengthmodifier", 1.0)
        ini["PVP"]                             = self.cfg.get_bool("pvp", True)
        ini["PauseEmpty"]                      = self.cfg.get_bool("pause_empty", False)
        ini["GlobalChat"]                      = self.cfg.get_bool("global_chat", True)
        ini["Open"]                            = self.cfg.get_bool("open", True)
        ini["ServerWelcomeMessage"]            = self.cfg.get_value("welcome_message", "")
        ini["LogLocalChat"]                    = self.cfg.get_bool("log_local_chat", False)
        ini["AutoCreateUserInWhiteList"]       = self.cfg.get_bool("auto_whiteList", False)
        ini["DisplayUserName"]                 = self.cfg.get_bool("display_username", True)
        ini["SpawnPoint"]                      = self.cfg.get_value("spawn_point", "0,0,0")
        ini["SafetySystem"]                    = self.cfg.get_bool("safety_system", True)
        ini["ShowSafety"]                      = self.cfg.get_bool("show_safety", True)
        ini["SafetyToggleTimer"]               = self.cfg.get_int("safety_toggle_timer", 100)
        ini["SafetyCooldownTimer"]             = self.cfg.get_int("safety_cooldown_timer", 120)
        ini["SpawnItems"]                      = self.cfg.get_value("spawn_items", "")
        ini["DefaultPort"]                     = self.cfg.get_int("port", 17261)
        ini["Mods"]                            = self.cfg.get_value("mods", "")
        ini["Map"]                             = self.cfg.get_value("map", "Muldraugh, KY")
        ini["SpawnRegions"]                    = self.cfg.get_value("spawn_regions", "%s_spawnregions.lua"%self.name)
        ini["DoLuaChecksum"]                   = self.cfg.get_bool("do_lua_checksum", True)
        ini["Public"]                          = self.cfg.get_bool("public", False)
        ini["PublicName"]                      = self.cfg.get_value("public_name", "My Zoid PZ Server")
        ini["PublicDescription"]               = self.cfg.get_value("public_description", "")
        ini["MaxPlayers"]                      = self.cfg.get_int("max_players", 64)
        ini["PingFrequency"]                   = self.cfg.get_int("ping_frequency", 10)
        ini["PingLimit"]                       = self.cfg.get_int("ping_limt", 400)
        ini["HoursForLootRespawn"]             = self.cfg.get_int("hours_for_lootrespawn", 0)
        ini["MaxItemsForLootRespawn"]          = self.cfg.get_int("max_items_for_lootrespawn", 4)
        ini["ConstructionPreventsLootRespawn"] = self.cfg.get_bool("construction_prevents_lootrespawn", True)
        ini["DropOffWhiteListAfterDeath"]      = self.cfg.get_bool("drop_whitelist", False)
        ini["NoFireSpread"]                    = self.cfg.get_bool("no_fire_spread", False)
        ini["NoFire"]                          = self.cfg.get_bool("no_fire", False)
        ini["AnnounceDeath"]                   = self.cfg.get_bool("announce_death", False)
        ini["MinutesPerPage"]                  = self.cfg.get_float("minutes_per_page", 1.0)
        ini["HoursForCorpseRemoval"]           = self.cfg.get_int("corpse_removal", 0)
        ini["SaveWorldEveryMinutes"]           = self.cfg.get_int("save_world_every", 0)

        if "safehouse" in self.cfg:
            ini["PlayerSafehouse"]             = self.cfg["safehouse"].get_bool("player", False)
            ini["AdminSafehouse"]              = self.cfg["safehouse"].get_bool("admin", False)
            ini["SafehouseAllowTrepass"]       = self.cfg["safehouse"].get_bool("trespass", True)
            ini["SafehouseAllowFire"]          = self.cfg["safehouse"].get_bool("fire", True)
            ini["SafehouseAllowLoot"]          = self.cfg["safehouse"].get_bool("loot", True)
            ini["SafehouseAllowRespawn"]       = self.cfg["safehouse"].get_bool("respawn", False)
            ini["SafehouseDaySurvivedToClaim"] = self.cfg["safehouse"].get_int("claim", 0)
            ini["SafeHouseRemovalTime"]        = self.cfg["safehouse"].get_int("removal", 144)

        ini["AllowDestructionBySledgehammer"]  = self.cfg.get_bool("allow_sledge", True)
        ini["KickFastPlayers"]                 = self.cfg.get_bool("kick_fast", False)

        if "rcon" in self.cfg:
            ini["RCONPort"]                    = self.cfg["rcon"].get_int("port", 27015)
            ini["RCONPassword"]                = self.cfg["rcon"].get_value("password", "")

        ini["Password"]                        = self.cfg.get_value("password", "")
        ini["MaxAccountsPerUser"]              = self.cfg.get_int("max_accounts", 0)

        if "steam" in self.cfg:
            ini["SteamPort1"]                  = self.cfg["steam"].get_int("port1", 8766)
            ini["SteamPort2"]                  = self.cfg["steam"].get_int("port2", 8767)
            ini["SteamVAC"]                    = self.cfg["steam"].get_bool("vac", True)
            ini["WorkshopItems"]               = self.cfg["steam"].get_value("workshop_items", "")
            ini["SteamScoreboard"]             = self.cfg["steam"].get_bool("scoreboard", True)

        reset_id = self.cfg.get_value("reset_id", None)
        if not reset_id is None:
            ini["ResetID"]                     = int(reset_id)

        player_id = self.cfg.get_value("server_player_id", None)
        if not player_id is None:
            if player_id.lower() == "none":
                ini["ServerPlayerID"] = ""
            else:
                ini["ServerPlayerID"]          = int(player_id)

        with open(ini_file, "wb") as fp:
            ini.write(fp)

    def _update_sandbox_vars(self):
        path = os.path.join(self.get_data_path(), "Zomboid", "Server")
        if not os.path.exists(path):
            raise Exception("server path '%s' not found", path)

        cfg = self.cfg["sandbox"]

        with open(os.path.join(path, "%s_SandboxVars.lua"%self.name), "w") as fp:
            fp.write("SandboxVars = {\n")

            fp.write("\tSpeed = %s,\n" % cfg.get_int("speed"))
            fp.write("\tZombies = %s,\n" % cfg.get_int("zombies"))
            fp.write("\tDistribution = %s,\n" % cfg.get_int("distribution"))
            fp.write("\tSurvivors = %s,\n" % cfg.get_int("survivors"))

            fp.write("\tDayLength = %s,\n" % cfg.get_int("day_length"))
            fp.write("\tStartYear = %s,\n" % cfg.get_int("start_year"))
            fp.write("\tStartMonth = %s,\n" % cfg.get_int("start_month"))
            fp.write("\tStartDay = %s,\n" % cfg.get_int("start_day"))
            fp.write("\tStartTime = %s,\n" % cfg.get_int("start_time"))

            fp.write("\tWaterShutModifier = %s,\n" % cfg.get_int("water_shut_modifier"))
            fp.write("\tElecShutModifier = %s,\n" % cfg.get_int("elec_shut_modifier"))

            fp.write("\tFoodLoot = %s,\n" % cfg.get_int("food_loot"))
            fp.write("\tWeaponLoot = %s,\n" % cfg.get_int("weapon_loot"))
            fp.write("\tOtherLoot = %s,\n" % cfg.get_int("other_loot"))

            fp.write("\tTemperature = %s,\n" % cfg.get_int("temperature"))
            fp.write("\tRain = %s,\n" % cfg.get_int("rain"))
            fp.write("\tErosionSpeed = %s,\n" % cfg.get_int("erosion_speed"))

            fp.write("\tXpMultiplier = %s,\n" % cfg.get_float("xp_multiplier"))
            fp.write("\tStatsDecrease = %s,\n" % cfg.get_int("stats_decrease"))
            fp.write("\tNatureAbundance = %s,\n" % cfg.get_int("nature_abundance"))

            fp.write("\tAlarm = %s,\n" % cfg.get_int("alarm"))
            fp.write("\tLockedHouses = %s,\n" % cfg.get_int("locked_houses"))

            fp.write("\tFoodRotSpeed = %s,\n" % cfg.get_int("food_rot_speed"))
            fp.write("\tFridgeFactor = %s,\n" % cfg.get_int("fridge_factor"))
            fp.write("\tFarming = %s,\n" % cfg.get_int("farming"))
            fp.write("\tLootRespawn = %s,\n" % cfg.get_int("loot_respawn"))
            fp.write("\tStarterKit = %s,\n" % ("true" if cfg.get_bool("starter_kit") else "false"))
            fp.write("\tTimeSinceApo = %s,\n" % cfg.get_int("time_since_apo"))
            fp.write("\tPlantResilience = %s,\n" % cfg.get_int("plant_resilience"))
            fp.write("\tPlantAbundance = %s,\n" % cfg.get_int("plant_abundance"))
            fp.write("\tEndRegen = %s,\n" % cfg.get_int("end_regen"))

            fp.write("\tZombieLore = {\n")
            fp.write("\t\tSpeed = %s,\n" % cfg["zombie_lore"].get_int("speed"))
            fp.write("\t\tStrength = %s,\n" % cfg["zombie_lore"].get_int("strength"))
            fp.write("\t\tToughness = %s,\n" % cfg["zombie_lore"].get_int("toughness"))
            fp.write("\t\tTransmission = %s,\n" % cfg["zombie_lore"].get_int("transmission"))
            fp.write("\t\tMortality = %s,\n" % cfg["zombie_lore"].get_int("mortality"))
            fp.write("\t\tReanimate = %s,\n" % cfg["zombie_lore"].get_int("reanimate"))
            fp.write("\t\tCognition = %s,\n" % cfg["zombie_lore"].get_int("cognition"))
            fp.write("\t\tMemory = %s,\n" % cfg["zombie_lore"].get_int("memory"))
            fp.write("\t\tDecomp = %s,\n" % cfg["zombie_lore"].get_int("decomp"))
            fp.write("\t\tSight = %s,\n" % cfg["zombie_lore"].get_int("sight"))
            fp.write("\t\tHearing = %s,\n" % cfg["zombie_lore"].get_int("hearing"))
            fp.write("\t\tSmell = %s,\n" % cfg["zombie_lore"].get_int("smell"))
            fp.write("\t\tThumpNoChasing = %s,\n" % cfg["zombie_lore"].get_int("thump_no_chasing"))
            fp.write("\t}\n")

            fp.write("}\n")

            fp.write("""
local DefaultSandboxVars = {}
local DefaultZombieLore = {}
for k,v in pairs(SandboxVars) do
        DefaultSandboxVars[k] = v
end
for k,v in pairs(SandboxVars.ZombieLore) do
        DefaultZombieLore[k] = v
end

function setDefaultSandboxVars()
        for k,v in pairs(DefaultSandboxVars) do
                SandboxVars[k] = v
        end
        SandboxVars.ZombieLore = {}
        for k,v in pairs(DefaultZombieLore) do
                SandboxVars.ZombieLore[k] = v
        end
        ZombieConfig.getInstance():resetToDefault()
        ZombieConfig.getInstance():fromSandboxVars(SandboxVars)
end
            """)

    def _write_startup_args_json(self, filename):
        server_path = self.get_data_path()
        exec_path = self.get_exec_path()

        vm_xms = self.cfg["vm"].get_value("xms")
        vm_xmx = self.cfg["vm"].get_value("xmx")
        enable_steam = self.cfg["steam"].get_bool("enable", False)

        with open(os.path.join(exec_path, filename), "w") as fp:
            fp.write("""
                {
                        "mainClass": "zombie/network/GameServer",
                        "classpath": [
                                "java/",
                                "java/jinput.jar",
                                "java/lwjgl.jar",
                                "java/lwjgl_util.jar",
                                "java/sqlite-jdbc-3.8.10.1.jar",
                                "java/uncommons-maths-1.2.3.jar"
                        ],
                        "vmArgs": [
                                "-Xms%(vm_xms)s",
                                "-Xmx%(vm_xmx)s",
                                "-Duser.home=%(server_path)s",
                                "-Dzomboid.steam=%(steam)s",
                                "-Dzomboid.znetlog=1",
                                "-Djava.library.path=linux64/:natives/",
                                "-XX:-UseSplitVerifier",
                                "-Djava.security.egd=file:/dev/urandom"
                        ]
                }
            """ % {
                "server_path": server_path,
                "steam": ("1" if enable_steam else "0"),
                "vm_xms": vm_xms,
                "vm_xmx": vm_xmx,
            })

    def runfile_exists(self):
        return os.path.exists(os.path.join(self.get_data_path(), self.name + ".run"))

    def runfile_create(self):
        with open(os.path.join(self.get_data_path(), self.name + ".run"), "w") as fp:
            fp.write(str(time.time()))

    def runfile_remove(self):
        runfile = os.path.join(self.get_data_path(), self.name + ".run")
        if not os.path.exists(runfile):
            return
        os.remove(runfile)

    def start(self, timeout=30):
        """
            Starts the server

            @param time: Duration in seconds to wait for the server to start
        """

        if self.is_running():
            raise ServerRunningError()

        #-- test if the ip address is in use, this is no guarantee but better check it now before starting the server process
        server_address = self.get_address()
        if is_address_in_use(server_address):
            raise ServerAddressInUseError(server_address)

        #-- same as above but for the RCon address
        rcon_port = self.cfg["rcon"].get_int("port")
        if is_address_in_use((server_address[0], rcon_port), protocol=socket.SOCK_STREAM):
            raise RConServerAddressInUseError("the rcon server address '%s:%s' is allready in use" % (server_address[0], rcon_port))

        server_path = self.get_data_path()
        exec_path = self.get_exec_path()
        LOG.debug("server_path = %s", server_path)
        LOG.debug("exec_path = %s", exec_path)

        #-- test for the runfile and give a warning message
        if self.runfile_exists():
            LOG.warn("the server runfile allready exists, this could mean the server crashed or was terminated by user")

        #-- test for the ./Zomboid/Server folder and create the _spawregions.lua file if it not exists
        ini_path = os.path.join(self.get_data_path(), "Zomboid", "Server")
        if not os.path.exists(ini_path):
            #-- seems we starting a new server for the first time

            LOG.debug("server path dont exist, creating it now")
            if not os.path.exists(ini_path):
                os.makedirs(ini_path)

            write_spawnregions_lua(os.path.join(ini_path, "%s_spawnregions.lua"%self.name))

        #-- update the server ini file
        self._update_server_ini()

        #-- update the sandbox vars
        self._update_sandbox_vars()

        #-- pick some config values for easy use
        admin_password = self.cfg.get_value("adminpassword")
        enable_steam = self.cfg["steam"].get_bool("enable", False)
        vm_xms = self.cfg["vm"].get_value("xms")
        vm_xmx = self.cfg["vm"].get_value("xmx")

        log_path = os.path.join(server_path, "logs")
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        log_file = os.path.join(log_path, "%s.log"%datetime.now().strftime("%Y-%m-%d-%H-%M"))

        LOG.info("starting server '%s'. depending on if you using steam workshop mods the start can take a while." % self.name)

        if os.name == "nt":
            args = [
                os.path.join(exec_path, "jre64" if platform.machine().endswith("64") else "jre", "bin", "java.exe"),

                "1>", log_file, "2>&1",

                "-Xms" + vm_xms,
                "-Xms" + vm_xmx,

                "-Dzomboid.steam=" + ("1" if enable_steam else "0"),
                "-Dzomboid.znetlog=1",
                "-Duser.home=" + server_path,

                "-Djava.library.path=natives/;.",
                "-cp",
                    "java/jinput.jar;java/lwjgl.jar;java/lwjgl_util.jar;java/sqlite-jdbc-3.8.10.1.jar;java/uncommons-maths-1.2.3.jar;java/",

                "zombie.network.GameServer",
            ]

            if admin_password != "":
                args.extend(["-adminpassword", admin_password])

            args.extend(["-servername", self.name])

            args = [ str(a) for a in args ]

            #-- write zoid.cmd with given args
            with open(os.path.join(exec_path, "zoid.cmd"), "w") as fp:
                fp.write("@setlocal enableextensions\n")
                fp.write(" ".join(args) + "\n")
                fp.write("exit 0\n")

            #-- start zoid.cmd
            #subprocess.Popen(["start", "zoid.cmd"], cwd=exec_path, shell=True, creationflags=8, close_fds=True)

            #-- write a VBScript that is able to hide console window of the spawned process
            with open(os.path.join(exec_path, "zoid.vbs"), "w") as fp:
                fp.write('CreateObject("Wscript.Shell").Run "zoid.cmd", 0, True\n')
            #-- start zoid.vbs
            subprocess.Popen(["start", "zoid.vbs"], cwd=exec_path, shell=True, creationflags=8, close_fds=True)
        elif os.name == "posix":
            self._write_startup_args_json("ProjectZomboid32.json")
            self._write_startup_args_json("ProjectZomboid64.json")

            subprocess.call(
                "cd " + exec_path + ";" +
                "./start-server.sh -adminpassword " + admin_password + " -servername " + self.name +
                " > " + log_file + " 2>&1 &",
                shell=True,
                env=dict(os.environ, HOME=zoid.HOME_PATH)
            )
        else:
            raise NotImplementedError()

        #-- create the runfile
        self.runfile_create()

        #-- wait for the process to appear
        while not self.is_running():
            time.sleep(0.1)

        #-- wait for the logfile to appear
        while not os.path.exists(log_file):
            time.sleep(0.1)

        #-- try to find out if the server could not start correctly
        #-- in detail: wait for RCon server to appear and check if the logfile gets changed
        #-- if no RCon server appears and the logfiles last change is greater then the set timeout
        #-- we can guess there is some problem with the server
        t_start = time.time()
        while True:
            try: #-- run a random RCon command to check if it is accessable
                self.rcon("players", 1.0)
                rcon_reached = True
            except:
                rcon_reached = False

            if rcon_reached:
                #-- the RCon server is open, so the server should be running fine
                break

            if not self.is_running():
                LOG.error("the server process ended before the RCon server was started, this might mean there was some errors during the startup, please take a look into the logfile at: %s", log_file)
                self.runfile_remove()
                return

            last_log = time.time() - os.stat(log_file).st_mtime
            LOG.debug("waiting for rcon server since %i sec., last log activity was before %.01f sec.", time.time()-t_start, last_log)

            if last_log > timeout:
                LOG.error("the logfile last changed before %i sec. and no RCon server is available. There might be a problem, please take a look into the logfile at: %s", last_log, log_file)
                return

        LOG.info("server started successfully")

    def stop(self, timeout=30):
        """
            Stop the server

            @param time: Duration in seconds to wait for the server to stop
        """

        if not self.is_running():
            raise ServerNotRunningError()

        try:
            LOG.info("sending 'quit' command via RCon ...")
            response = self.rcon("quit")

            if not response == "Quit":
                LOG.error("unexpected RCon response: %s", response)
                return False

            LOG.info("waiting for server to quit ...")
            t_start = time.time()
            while True:
                if not self.is_running():
                    LOG.info("server process ended")
                    self.runfile_remove()
                    return True

                if time.time() - t_start > timeout:
                    LOG.warn("timeout: server process still running after 30 sec.")
                    return False
        except:
            return False

    def kill(self):
        """
            Kill the server process
        """

        if not self.is_running():
            raise ServerNotRunningError()

        LOG.info("killing process id %s ...", self.get_pid())
        if os.name == "nt":
            os.system("taskkill /F /PID %s" % self.get_pid())
        elif os.name == "posix":
            os.system("kill -9 %s" % self.get_pid())

        while self.is_running():
            time.sleep(0.1)

        self.runfile_remove()

        LOG.info("done")

    def rcon(self, command, timeout=5.0):
        """
            Send a RCon command to the server
        """

        if not self.is_running():
            raise ServerNotRunningError()

        rcon_port = self.cfg["rcon"].get_int("port", None)
        if rcon_port is None:
            raise Exception("could not get rcon port from config")

        rcon_pass = self.cfg["rcon"].get_value("password", None)
        if rcon_port is None:
            raise Exception("could not get rcon password from config")

        rcon = SourceRcon("127.0.0.1", rcon_port, rcon_pass, timeout=timeout)
        response = rcon.rcon(command)
        rcon.disconnect()

        return response

get = Server.get # == def get(name): return Server.get(name)
