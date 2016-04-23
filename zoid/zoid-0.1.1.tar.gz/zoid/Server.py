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
import xml.etree.ElementTree as ET
import subprocess
import socket
import shutil
from datetime import datetime

import zoid
from zoid.IS import ServerConfiguration
from zoid.SourceRcon import SourceRcon

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

def get_processes():
    if os.name == "nt":
        #-- just to say: I HATE WINDOWS!!! I REALY DO! just look at this mess only for getting a process listing oO
        xml = os.popen("wmic path win32_process get Caption,ProcessId,CommandLine /format:rawxml").read()
    
        root = ET.fromstring( xml )
        for xn_instance in root.findall("RESULTS")[0].findall("CIM")[0].findall("INSTANCE"):
    
            instance_properties = {}
            for xn_prop in xn_instance.findall("PROPERTY"):
                name = xn_prop.attrib["NAME"]
                values = xn_prop.findall("VALUE")
                if len(values) == 0:
                    instance_properties[name] = ""
                else:
                    instance_properties[name] = values[0].text
            
            yield {"pid": int(instance_properties["ProcessId"]), "cmd": instance_properties["CommandLine"]}
    elif os.name == "posix":
        for pid in [pid for pid in os.listdir('/proc') if pid.isdigit()]:
            try:
                cmd = open(os.path.join('/proc', pid, 'cmdline'), 'rb').read()
                if cmd.endswith("\x00"):
                    cmd = cmd[:-1]
                yield {"pid": int(pid), "cmd": cmd.replace("\x00", " ")}
            except IOError: # proc has already terminated
                continue
    else:
        raise NotImplementedError()

def get_server_processes():
    """
        yields (server_name, pid) for all running servers
    """

    for e in get_processes():
        if "zombie.network.GameServer" in e["cmd"]:
            a = e["cmd"].split(" ")
            if "cmd.exe" in a[0]:
                continue
            yield a[-1], e["pid"]

class ServerValidationError(Exception):
    pass
class ServerConfigValidationError(ServerValidationError):
    pass

class ServerRunningError(Exception):
    def __init__(self, msg="Server is allready running"):
        Exception.__init__(self, msg)

class ServerNotRunningError(Exception):
    def __init__(self, msg="Server is not running"):
        Exception.__init__(self, msg)

class Server(object):
    instances = {}

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
            zoid.validate_server_files(branch, password)

        if not os.path.exists( os.path.join(p, "validated.dat") ):
            raise ServerValidationError("could not find the 'validated.dat' file, please run '--validate-server %s'" % self.name)

        self.validate_config()

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
        if not self.is_running():
            return []
        
        return [ [ d.split("=",1) for d in c.split(" ") ] for c in self.rcon("connections").split("\n")[:-1] ]
    
    def update_server_ini(self):
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

        reset_id = self.cfg.get_int("reset_id", 0)
        if reset_id != 0:
            ini["ResetID"]                     = reset_id

        player_id = self.cfg.get_int("server_player_id", 0)
        if player_id != 0:
            ini["ServerPlayerID"]              = player_id

        with open(ini_file, "wb") as fp:
            ini.write(fp)
   
    def start(self):
        if self.is_running():
            raise ServerRunningError()

        server_address = self.get_address()
        
        #-- test if the ip address is in use, this is no guarantee but better check it now before starting the server process
        if is_address_in_use(server_address):
            raise Exception("the server address '%s:%s' is allready in use" % server_address)
        
        rcon_port = self.cfg["rcon"].get_int("port")
        if is_address_in_use((server_address[0], rcon_port), protocol=socket.SOCK_STREAM):
            raise Exception("the rcon server address '%s:%s' is allready in use" % (server_address[0], rcon_port))

        server_path = self.get_data_path()
        exec_path = self.get_exec_path()
        
        log_file = os.path.join(server_path, "%s.log"%datetime.now().strftime("%Y-%m-%d-%H-%M"))

        ini_path = os.path.join(self.get_data_path(), "Zomboid", "Server")        
        if not os.path.exists(ini_path):
            #-- seems we starting a new server for the first time

            LOG.debug("server path dont exist, creating it now from skeleton")
            if not os.path.exists(ini_path):
                #LOG.debug("server ini path dont exist, creating it now")
                os.makedirs(ini_path)

            skel_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "skel")
            for entry in os.listdir(skel_path):
                shutil.copy(os.path.join(skel_path, entry), os.path.join(ini_path, "%s_%s"%(self.name, entry)))

        LOG.debug("server_path = %s", server_path)
        LOG.debug("exec_path = %s", exec_path)

        #-- update the server ini file
        self.update_server_ini()
        
        #----

        admin_password = self.cfg.get_value("adminpassword")
        vm_xms = self.cfg["vm"].get_value("xms")
        vm_xmx = self.cfg["vm"].get_value("xmx")
        enable_steam = self.cfg["steam"].get_bool("enable", False)

        args = []
        if os.name == "nt":        
            args.extend([
                os.path.join(exec_path, "jre64\\bin\\java.exe"),

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
            ])
        elif os.name == "posix":
            args.extend([
                "java",

                "-Xms" + vm_xms,
                "-Xms" + vm_xmx,

                "-Dzomboid.steam=" + ("1" if enable_steam else "0"),
                "-Dzomboid.znetlog=1",                
                "-Duser.home=" + server_path,

                '-Djava.library.path="' + exec_path + '/natives:' + exec_path + '/linux64"',
                "-cp",
                    "java/:java/lwjgl.jar:java/lwjgl_util.jar:java/sqlite-jdbc-3.8.10.1.jar:java/uncommons-maths-1.2.3.jar",
                "-XX:-UseSplitVerifier",

                "zombie.network.GameServer"
            ])
        else:
            raise NotImplementedError()

        if admin_password != "":
            args.extend(["-adminpassword", admin_password])

        args.extend(["-servername", self.name])

        args = [ str(a) for a in args ]
        LOG.debug("executing: %s", " ".join(args))

        LOG.info("starting server '%s'" % self.name)
        if os.name == "nt":
            with open(os.path.join(exec_path, "zoid.cmd"), "w") as fp:
                fp.write(" ".join(args) + "\n")
                fp.write("exit 0")
            subprocess.Popen(["start", "zoid.cmd"], cwd=exec_path, shell=True, creationflags=8, close_fds=True)
            pid = 0
        elif os.name == "posix":
            subprocess.call("cd " + exec_path + ";" + " ".join(args) + " > " + log_file + " 2>&1 &", shell=True)
            pid = 0

        return pid
    
    def stop(self):
        if not self.is_running():
            raise ServerNotRunningError()

        LOG.info("sending 'quit' command via RCon ...")

        response = self.rcon("quit")

        if not response == "Quit":
            LOG.error("unexpected RCon response: %s", response)

        LOG.info("waiting for server to quit ...")    
        t_start = time.time()
        while True:
            if not self.is_running():
                LOG.info("server process ended")
                break
            if time.time() - t_start > 30:
                LOG.warn("timeout: server process still running after 30 sec.")
                break

    def rcon(self, command):
        if not self.is_running():
            raise ServerNotRunningError()
        
        rcon_port = self.cfg["rcon"].get_int("port", None)
        if rcon_port is None:
            raise Exception("could not get rcon port from config")
        
        rcon_pass = self.cfg["rcon"].get_value("password", None)
        if rcon_port is None:
            raise Exception("could not get rcon password from config")
        
        rcon = SourceRcon("127.0.0.1", rcon_port, rcon_pass, timeout=5.0)
        response = rcon.rcon(command)
        rcon.disconnect()
        
        return response
        
get = Server.get # == def get(name): return Server.get(name)