"""
Support for eq3 Bluetooth Smart thermostats.

All temperatures in Celsius.

To get the current state, update() has to be called for powersaving reasons.
"""

import struct
from datetime import datetime
from ..lib.connection import BTLEConnection

PROP_WRITE_HANDLE = 0x411
PROP_NTFY_HANDLE = 0x421

PROP_ID_QUERY = 0
PROP_ID_RETURN = 1
PROP_INFO_QUERY = 3
PROP_INFO_RETURN = 2
PROP_SCHEDULE_QUERY = 0x20
PROP_SCHEDULE_RETURN = 0x21

PROP_TEMPERATURE_WRITE = 0x41


# pylint: disable=too-many-instance-attributes
class EQ3BTSmartThermostat:
    """Representation of a EQ3 Bluetooth Smart thermostat."""

    def __init__(self, _mac):
        """Initialize the thermostat."""

        self._targetTemperature = -1
        self._mode = -1
        
        self._conn = BTLEConnection(_mac)
        
        self._conn.setCallback(PROP_NTFY_HANDLE, self.handleNotification)
        self._conn.connect()

        self._setTime()

    def __str__(self):
        return "MAC: " + self._conn.mac + " Mode: " + str(self.mode) + " = " + self.readableMode + " T: " + str(self.targetTemperature)

    def handleNotification(self, data):
        """Handle Callback from a Bluetooth (GATT) request."""
        if data[0] == PROP_INFO_RETURN:
            self._mode = data[2] & 1
            self._targetTemperature = data[5] / 2.0

# TO BE TESTED
    def _setTime(self):
        """Set the correct time into the thermostat."""
        time = datetime.now()
        value = struct.pack('BBBBBB', int(time.strftime("%y")),
                            time.month, time.day, time.hour,
                            time.minute, time.second)
        self._conn.writeCommandRaw(PROP_WRITE_HANDLE, value)

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def targetTemperature(self):
        """Return the temperature we try to reach."""
        return self._targetTemperature

    @targetTemperature.setter
    def targetTemperature(self, temperature):
        """Set new target temperature."""
        value = struct.pack('BB', PROP_TEMPERATURE_WRITE, int(temperature*2))
        # Returns INFO_QUERY, so use that
        self._conn.writeRequestRaw(PROP_WRITE_HANDLE, value)

    @property
    def mode(self):
        """Return the mode (auto / manual)."""
        return self._mode

    @property
    def readableMode(self):
        """Return a readable representation of the mode.."""
        return self.decodeMode(self._mode)

    @property
    def minTemp(self):
        """Return the minimum temperature."""
        return 4.5

    @property
    def maxTemp(self):
        """Return the maximum temperature."""
        return 30.5

    @staticmethod
    def packByte(byte):
        """Pack a byte."""
        return struct.pack('B', byte)

    @staticmethod
    def decodeMode(mode):
        """Convert the numerical mode to a human-readable description."""
        ret = ""
        if mode & 1:
            ret = "manual"
        else:
            ret = "auto"

        if mode & 2:
            ret = ret + " holiday"
        if mode & 4:
            ret = ret + " boost"
        if mode & 8:
            ret = ret + " dst"
        if mode & 16:
            ret = ret + " window"

        return ret

    def update(self):
        """Update the data from the thermostat."""
        self._conn.writeRequestRaw(PROP_WRITE_HANDLE, self.packByte(PROP_INFO_QUERY))


