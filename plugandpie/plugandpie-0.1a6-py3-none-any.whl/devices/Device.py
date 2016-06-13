""" This module contains the Device class
"""


class Device(object):
    """ Class representing any kind of device.
    The device should have a list of sensor tags that define its purpose,
    an underlying interface of communication and the dictionary of registers.

    """
    def __init__(self, sensors, interface):
        self.sensors = sensors
        self.interface = interface
        self.register = {}

    def standby(self):
        raise NotImplementedError()

    def activate(self):
        raise NotImplementedError()

    def reset(self):
        raise NotImplementedError()
