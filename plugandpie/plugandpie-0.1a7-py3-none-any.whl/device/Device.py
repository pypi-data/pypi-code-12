""" This module contains the Device class and the Sensor enumeration
"""
from enum import Enum

Sensor = Enum(
    'Sensor',
    [
        'ACCELEROMETER',
        'PHOTOSENSOR',
        'POSITIOMETER',
        'THERMOMETER'
    ]
)


class Device(object):
    """ Class representing any kind of device.
    The device should have a list of sensor tags that define its purpose
    and the dictionary of registers.
    """
    sensors = []

    def __init__(self, interface, address):
        self.interface = interface
        self.address = address
        self.register = {}


class Register(object):
    def __init__(self, device, register_address):
        self.device = device
        self.register_address = register_address
        self._cached_value = None

    def set(self, v):
        self.device.interface.write_byte(self.device.address, self.register_address, v)
        self._cached_value = v

    def get(self, cached=False):
        if cached and self._cached_value is not None:
            return self._cached_value
        self._cached_value = self.device.interface.read_byte(self.device.address, self.register_address)
        return self._cached_value
