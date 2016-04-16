#! /usr/bin/env python
#
# Copyright (C) 2014-2015 Jens Kasten <jens@kasten-edv.de>. All Rights Reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
# 

"""
Package.

Copyright (C) Jens Kasten. All Rights Reserved.
"""

__author__  = "Jens Kasten <jens@kasten-edv.de>"
__status__  = "beta"
__date__    = "4 August 2014"
__all__ = []


import os
import sys
import re
from subprocess import Popen, PIPE, call
import logging
import json

logging.basicConfig(format='%(levelname)s:%(name)s:line %(lineno)s: %(message)s')
log = logging.getLogger(__name__)

LEVEL = {
    "battery": 0,
    "ac-adapter": 1,
    "no powersupply": 2,
}

CONFIG_DIR = "/etc/laptop-pm"
CONFIG_FILE = "%s/laptop-pm.json" % CONFIG_DIR

HCI0 = ""
LCD_DRIVER = ""
LCD_BRIGHTNESS_MIN = 0
LCD_BRIGHTNESS_MAX = 0
SND_DRIVER = ""
WIFI_DEVICE = ""
ETH_DEVICE = ""

try:
    with open(CONFIG_FILE) as fd:
        config = json.loads(fd.read())
        HCI0 = config.get("HCI0", HCI0)              
        LCD_DRIVER = config.get("LCD_DRIVER", LCD_DRIVER)
        LCD_BRIGHTNESS_MIN = config.get("LCD_BRIGHTNESS_MIN",
                                        LCD_BRIGHTNESS_MIN)
        LCD_BRIGHTNESS_MAX = config.get("LCD_BRIGHTNESS_MAX",
                                        LCD_BRIGHTNESS_MAX)
        SND_DRIVER = config.get("SND_DRIVER", SND_DRIVER)
        WIFI_DEVICE = config.get("WIFI_DEVICE", WIFI_DEVICE)
        ETH_DEVICE = config.get("ETH_DEVICE", ETH_DEVICE)
except ValueError as error:
    log.warning("%s in %s" %(error, CONFIG_FILE))
    sys.exit(-1)
except IOError as error:
    log.warning("config does not exists: %s" % CONFIG_FILE)
    sys.exit(-1)

def execute(cmd):
    """General function to make a system call."""
    try:
        process = Popen(cmd, stdout=PIPE, stderr=PIPE)
        output, error = process.communicate()
        error = error.decode("utf-8").strip()
        output = output.decode("utf-8").strip()
        if len(error) > 0:
            print(error)
        else:
            return output
    except OSError as error:
        log.error(error)
        
def to_write(to_file, value):
    """General funtion to write value to virtual files.
        Example: echo 0 > /sys/path/to/change
    """
    try:
        with open(to_file, "w") as fd:
            fd.write(value)
    except OSError as error:
        log.error(error)


def is_ac_power():
    """Check with sysfs if AC adapter is present.
        return [0|1|2]
        0 when system is on battery
        1 when system is on ac-adapter
        2 when system does not have an powersupply
    """
    power_supply = "/sys/class/power_supply"
    # guess no laptop
    if not os.path.isdir(power_supply):
        log.error("No dir: %s" % power_supply)
        return 2
    status = 1
    for adapter in os.listdir(power_supply):
        online = os.path.join(power_supply, adapter, "online")
        if os.path.isfile(online):
            status = int(execute(["cat", online]))
            break
    log.info("is_ac_power: %s" % status)
    return status

def show():
    """Return the name from is_ac_power()."""
    status = is_ac_power()
    value = list(LEVEL.values()).index(status)
    key = list(LEVEL.keys())[value]
    print(key)
    sys.exit(status)

class NetDevices(object):

    def __init__(self, action):
        self.devices = []
        self.action = action

    def set_log_level(self, status=False):
        if status:
            log.setLevel(logging.DEBUG)
    
    def get_devices(self):
        pattern = r"\d: (?P<link>[a-z,A-z,0-9]+):.*"
        cmd = ["ip", "link", "show"]
        for i in execute(cmd).split("\n"):
            p = re.compile(pattern)
            device = p.search(i)
            if not device or device.group("link") == "lo":
                continue
            self.devices.append(device.group("link"))
        log.info("net devices: %s" % self.devices)

    def wifi_powersave(self):
        status = ("on", "off")
        cmd = ["iw", "dev", WIFI_DEVICE, "set", "power_save", status[self.action]]
        log.info("command: %s" % cmd)
        execute(cmd)

    def wake_on_lan(self):
        status = ("d", "p")
        cmd = ["ethtool", "-s",ETH_DEVICE, "wol", status[self.action]]
        log.info("command: %s" % cmd)
        execute(cmd)
    
    def net_speed(self):
        status = ("10", "100")
        cmd = ["ethtool", "-s", ETH_DEVICE, "autoneg", "off", "speed", 
            status[self.action]]
        log.info("command: %s" % cmd)
        execute(cmd)

    def bluetooth(self):
        status = ("block", "unblock")
        cmd = ["rfkill", status[self.action], "bluetooth"]
        log.info("command: %s" % cmd)
        execute(cmd)

    def change_status(self):
        self.wifi_powersave()
        self.wake_on_lan()
        self.net_speed()
        self.bluetooth()


class Proc(object):
    
    def __init__(self, action):
        self.action = action

    def set_log_level(self, status=False):
        if status:
            log.setLevel(logging.DEBUG)
    
    def laptop_mode(self):
        status = ("5", "0")
        to_file = "/proc/sys/vm/laptop_mode"
        value = status[self.action]        
        log.info("write %s to %s" % (value, to_file))
        to_write(to_file, value)

    def dirty_writebacks_centisecs(self):
        status = ("1500", "0")
        value = status[self.action]
        to_file = "/proc/sys/vm/dirty_writeback_centisecs"
        log.info("write %s to %s" % (value, to_file))
        to_write(to_file, value)

    def change_status(self):
        self.laptop_mode()
        self.dirty_writebacks_centisecs()


class HardDevices(object):

    def __init__(self, action):
        self.action = action

    def set_log_level(self, status=False):
        if status:
            log.setLevel(logging.DEBUG)

    def scsi_host(self):
        status = ("min_power", "max_performance")
        value = status[self.action]
        for host in os.listdir("/sys/class/scsi_host"):
            to_file = "/sys/class/scsi_host/%s/link_power_management_policy" % host
            log.info("write %s to %s" % (value, to_file))
            to_write(to_file, value)
   
    def pci(self):
        status = ("auto", "on")
        value = status[self.action]
        for device in os.listdir("/sys/bus/pci/devices"):
            to_file = "/sys/bus/pci/devices/%s/power/control" % device
            log.info("write %s to %s" % (value, to_file))
            to_write(to_file, value)

    def pcie(self):
        status = ("powersave", "performance")
        value = status[self.action]
        to_file = "/sys/module/pcie_aspm/parameters/policy"
        log.info("write %s to %s" % (value, to_file))
        to_write(to_file, value)

    def change_status(self):
        self.scsi_host()
        self.pcie()
        self.pci()


class UsbDevices(object):

    def __init__(self, action):
        self.devices = []
        self.action = action

    def set_log_level(self, status=False):
        if status:
            log.setLevel(logging.DEBUG)

    def get_devices(self):
        pattern = r"^\d-\d(|.\d)$"
        p = re.compile(pattern)
        if os.path.isdir("/sys/bus/usb/devices"):
            for device in os.listdir("/sys/bus/usb/devices"):
                if p.search(device):
                    self.devices.append(device)

    def control(self, device):
        status = ("auto", "on")
        value = status[self.action]
        to_file = "/sys/bus/usb/devices/%s/power/control" % device
        log.info("write %s to %s" % (value, to_file))
        to_write(to_file, value)

    def autosuspend(self, device):
        status = ("5", "0")
        value = status[self.action]
        to_file = "/sys/bus/usb/devices/%s/power/autosuspend" % device
        log.info("write %s to %s" % (value, to_file))
        to_write(to_file, value)

    def change_status(self):
        for device in self.devices:
            self.control(device)
            self.autosuspend(device)


class LcdDevice(object):
    """Set the brightness of the monitor."""

    def __init__(self, action):
        self.action = action

    def set_log_level(self, status=False):
        if status:
            log.setLevel(logging.DEBUG)

    def change_status(self):
        status = (LCD_BRIGHTNESS_MIN, LCD_BRIGHTNESS_MAX)
        value = status[self.action]
        to_file = "/sys/class/backlight/%s/brightness" % LCD_DRIVER
        log.info("write %s to %s" % (value, to_file))
        to_write(to_file, value)
    

class SoundDevices(object):
    """Set powersave to sound device."""

    def __init__(self, action):
        self.action = action

    def set_log_level(self, status=False):
        if status:
            log.setLevel(logging.DEBUG)

    def power_save(self):
        status = ("1", "0")
        value = status[self.action]
        to_file = "/sys/module/%s/parameters/power_save" % SND_DRIVER
        log.info("write %s to %s" % (value, to_file))
        to_write(to_file, value)

    def power_save_controller(self):
        status = ("Y", "N")
        value = status[self.action]
        to_file = "/sys/module/%s/parameters/power_save_controller" % SND_DRIVER
        log.info("write %s to %s" % (value, to_file))
        to_write(to_file, value)

    def change_status(self):
        self.power_save()
        self.power_save_controller()

class General(object):
    """Different powersave options"""

    def __init__(self, action):
        self.action = action

    def set_log_level(self, status=False):
        if status:
            log.setLevel(logging.DEBUG)

    def nmi(self):
        status = ("0", "1")
        value = status[self.action]
        to_file = "/proc/sys/kernel/nmi_watchdog"
        log.info("write %s to %s" % (value, to_file))
        to_write(to_file, value)

    def change_status(self):
        self.nmi() 
