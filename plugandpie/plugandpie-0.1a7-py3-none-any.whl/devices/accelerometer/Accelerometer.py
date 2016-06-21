""" This module contains the Accelerometer(Device) interface definition.
"""
from plugandpie.devices.Device import Device


class Accelerometer(Device):
    """ This class represents a device with accelerometer capabilities.
    """
    def __init__(self, interface):
        super(Accelerometer, self).__init__(['accelerometer'], interface)

    def standby(self):
        raise NotImplementedError()

    def activate(self):
        raise NotImplementedError()

    def reset(self):
        raise NotImplementedError()

    def set_g_range(self, g_range):
        """
        Sets the g range in which acceleration will be measured.
        :param g_range: the gravity multiplier that defines the 1.0 in the acceleration scale
        :return:
        """
        raise NotImplementedError()

    def set_output_data_rate(self, output_data_rate):
        """
        Sets the rate of measurements that should be made by the device.
        :param output_data_rate: frequency (in Hz) of measurements
        :return:
        """
        raise NotImplementedError()

    def get_ms2(self):
        """
        Converts the g range scaled acceleration into SI units (ms^2)
        :return: a dictionary with acceleration on each axis
        """
        raise NotImplementedError()

    def get_g(self):
        """
        Consult the most recent acceleration measurement in the g range scale
        :return: a dictionary with acceleration on each axis
        """
        raise NotImplementedError()
