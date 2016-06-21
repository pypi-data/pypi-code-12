""" This module is responsible for device detection and Proxy configuration
"""
import time
from plugandpie.common.utils import i2c_addresses
from plugandpie.devices.mapping import DRIVER_MAP


class Proxy(object):
    """ Implementation of the Proxy Design Pattern.
    Forwards attribute access to wrapped object.
    """
    MAX_TRIES = 5
    TRY_INTERVAL = 0.2

    def proxify(self, obj):
        """ Set the internal object to proxy link

        :param obj:
        :return:
        """
        self._obj = obj

    def __init__(self, target):
        self._target = target
        self._obj = None
        self._tries = 0

    def __getattr__(self, name):
        if self._obj is not None:
            return getattr(self._obj, name)
        else:
            self._tries += 1
            if self._tries > 5:
                self._tries = 0
                raise AttributeError("Proxy has no wrapped object")
            else:
                time.sleep(Proxy.TRY_INTERVAL)
                plug(self, self._target)
                return getattr(self, name)


DEVICES = {}


def plug(proxy, sensor):
    """ Finds a sensor to plug in the specified proxy.
    """
    addresses = i2c_addresses()
    # Update devices list
    for address in addresses:
        if address not in DEVICES.keys():
            device = DRIVER_MAP[address]()
            DEVICES[address] = device
    # Plug any device that has the required sensor
    for device in DEVICES.values():
        if sensor in device.sensors:
            proxy.proxify(device)
