"""
"""
import logging
import struct

from bluepy import btle

REQUIREMENTS = ['bluepy>=1.0.4']

DEFAULT_TIMEOUT = 1

_LOGGER = logging.getLogger(__name__)

# pylint: disable=too-many-instance-attributes
class BTLEConnection(btle.DefaultDelegate):
    """Representation of a BTLE Connection."""

    def __init__(self, mac):
        """Initialize the connection."""
        btle.DefaultDelegate.__init__(self)
        
        self._mac = mac
        self._conn = btle.Peripheral()
        
        self._callback = {}

    def __del__(self):
        """Destructor - make sure the connection is disconnected."""
        self.disconnect()

    def handleNotification(self, handle, data):
        """Handle Callback from a Bluetooth (GATT) request."""
        if (handle in self._callback):
            self._callback[handle](data)

    def connect(self, error = False):
        """Connect to the Bluetooth thermostat."""
        _LOGGER.info("BTLEConnection: connecting to " + self._mac)
        try:
            self._conn.connect(self._mac)
            self._conn.withDelegate(self)
        except btle.BTLEException:
            if (error):
                raise
            else:
                self.disconnect()
                self.connect(True)

    def disconnect(self):
        """Close the Bluetooth connection."""
        self._conn.disconnect()

    @property
    def mac(self):
        """Return the MAC address of the connected device."""
        return self._mac

    def setCallback(self, handle, function):
        """Set the callback for a Notification handle. It will be called with the parameter data, which is binary."""
        self._callback[handle] = function

    def writeRequest(self, handle, value, timeout=DEFAULT_TIMEOUT):
        """Write a GATT Command with callback."""
        self.writeCommand(handle, value, timeout, True)

    def writeRequestRaw(self, handle, value, timeout=DEFAULT_TIMEOUT):
        """Write a GATT Command with callback - no utf-8."""
        self.writeCommandRaw(handle, value, timeout, True)

    def writeCommand(self, handle, value, timeout=DEFAULT_TIMEOUT, waitForIt=False):
        """Write a GATT Command without callback."""
        self.writeCommandRaw(handle, value.encode('utf-8'), timeout, waitForIt)

    def writeCommandRaw(self, handle, value, timeout=DEFAULT_TIMEOUT, waitForIt=False, exception=False):
        """Write a GATT Command without callback - not utf-8."""
        from bluepy import btle

        try:
            self._conn.writeCharacteristic(handle, value, waitForIt)
            if waitForIt:
                while self._conn.waitForNotifications(timeout):
                    continue
        except btle.BTLEException:
            if exception is False:
                self.disconnect()
                self.connect()
                self.write_command_raw(handle, value, waitForIt, True)
