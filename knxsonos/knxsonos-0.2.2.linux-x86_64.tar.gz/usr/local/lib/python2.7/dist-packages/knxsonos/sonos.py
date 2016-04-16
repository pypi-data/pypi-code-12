#
#     Copyright 2010 Trond Kjeldaas
#
#     This file is part of KnxSonos
#
#     KnxSonos is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     KnxSonos is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
#
from soco import discover
from time import sleep
from threading import Thread, Lock
import logging

#
#
# To join group: SetAvTransportURI,
#                current URI ==x-rincon:RINCON_000E58334AF601400
#
# To leave group: BecomeCoordinatorOfStandaloneGroup
#
#


#
# Just a wrapper class for the SoCo controller class...
#
class SonosCtrl():

    def __init__(self, zone_names):

        self.logger = logging.getLogger('knxsonos')

        self.zones = {}
        self.needed_zones = zone_names
        self.quit = False
        self.zlock = Lock()

    def getCmdDict(self):
        """Return a dictionary that can be used to map commans to methods"""

        return {"play": self.play,
                "pause": self.pause,
                "next": self.next,
                "previous": self.prev,
                "volume+": self.volumeUp,
                "volume-": self.volumeDown,
                "volumeSet": self.volumeSet,
                "setURI": self.setURI}

    def start(self):
        self.logger.info("Starting.")
        self.quit = False

        t = Thread(target=self.discoverer, name="knxsonos discoverer")
        t.start()

    def stop(self):
        self.logger.info("Stopping.")
        self.quit = True

    def discoverer(self):

        def addOrReplaceZone(zone):

            if zone.player_name in self.zones:
                with self.zlock:
                    self.zones.pop(zone.player_name)
                self.logger.debug("Replacing: %s"%zone.player_name)
            else:
                self.logger.info("Adding: %s"%zone.player_name)

            with self.zlock:
                self.zones[zone.player_name] = zone

        def removeZone(zone_name):
            if zone_name in self.zones:
                with self.zlock:
                    self.zones.pop(zone_name)
                self.logger.info("Expiring: %s"%zone_name)

        while not self.quit:

            zones_needed = list(self.needed_zones)
            self.logger.debug("Need to find these zones: %s" %zones_needed)

            zones_discovered = discover(10)

            for z in list(zones_discovered):

                addOrReplaceZone(z)

                try:
                    zones_needed.remove(z.player_name)
                except ValueError:
                    self.logger.debug("Did not want: %s" %z.player_name)

            for z in zones_needed:
                removeZone(z)

            if len(zones_needed) > 0:
                self.logger.warning("Missing zones: %s" % zones_needed)
                self.logger.warning("New attempt in 5 sec...")
                sleep(5)
            else:
                self.logger.debug("Found all needed zones: %s" %self.zones.keys())
                self.logger.debug("New check in 60 sec...")
                sleep(60)

    #
    # Sonos commands
    #

    def pause(self, zn):
        self.zones[zn].group.coordinator.pause()

    def play(self, zn):
        self.zones[zn].group.coordinator.play()

    def next(self, zn):
        self.zones[zn].group.coordinator.next()

    def prev(self, zn):
        self.zones[zn].group.coordinator.previous()

    def volumeSet(self, zn, value):

        value = int(value)
        if value < 0 or value > 100:
            self.logger.warning("Zone(%s): Illegal volume value: %d" % (zn, value))
            return

        self.zones[zn].group.coordinator.volume = value

    def volumeUp(self, zn):
        if self.zones[zn].group.coordinator.volume < 100:
            self.zones[zn].group.coordinator.volume += 1

    def volumeDown(self, zn):
        if self.zones[zn].group.coordinator.volume > 0:
            self.zones[zn].group.coordinator.volume -= 1

    def setURI(self, zn, value):

        self.logger.info("Setting URI: %s" % value)
        self.zones[zn].group.coordinator.play_uri(value, start=True)
