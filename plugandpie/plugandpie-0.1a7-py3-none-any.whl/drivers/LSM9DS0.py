"""
This module contains the LSM9DS0 driver implementation
"""
from plugandpie.sensors import Accelerometer, Gyroscope, Magnetometer
from plugandpie.drivers.__model__ import Driver


class LSM9DS0(Driver, Accelerometer, Magnetometer, Gyroscope):
    def activate(self):
        pass

    def standby(self):
        pass

    def reset(self):
        pass

    def set_g_range(self, g_range):
        pass

    def set_output_data_rate(self, output_data_rate):
        pass

    def get_g(self):
        pass

    def get_ms2(self):
        pass

