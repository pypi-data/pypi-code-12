"""
This module contains the Proxy class implementation.
"""
import time


class Proxy(object):
    """
    Implementation of the Proxy Design Pattern.
    Forwards attribute access to wrapped device object.
    """
    MAX_TRIES = 5
    TRY_INTERVAL = 0.2
    RESOLVE = None

    def wrap(self, device):
        """ Set the internal object to proxy link

        :param device:
        :return:
        """
        self._device = device

    def __init__(self, sensor):
        self.wanted_sensor = sensor
        self._device = None
        self._tries = 0

    def __getattr__(self, name):
        if self._device is not None:
            return getattr(self._device, name)
        else:
            self._tries += 1
            if self._tries > 5:
                self._tries = 0
                raise AttributeError("Proxy's target device not configured")
            else:
                time.sleep(Proxy.TRY_INTERVAL)
                Proxy.RESOLVE(self)
                return getattr(self, name)
