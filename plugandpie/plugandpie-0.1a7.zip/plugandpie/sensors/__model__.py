""" This module contains the Device class and the Sensor enumeration
"""
from enum import Enum


class SENSOR(Enum):
    """Enumeration of sensors that can be found in a device"""
    ACCELEROMETER = ()
    MAGNETOMETER = ()
    THERMOMETER = ()

    def __new__(cls, *args, **kwargs):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj


class Device(object):
    """ Interface that represents any kind of device.
    """
