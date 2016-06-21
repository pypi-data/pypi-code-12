"""
This module implements the Interface and Register base classes for communication with
the devices through any standard (I2C/SMBus and SPI).
"""


class InterfaceAdapter(object):
    def open(self):
        """Opens bus for communication"""
        raise NotImplementedError()

    def close(self):
        """Closes bus for communication"""
        raise NotImplementedError()

    def write_byte(self, device_address, register_address, byte):
        """
        Writes a single byte
        :param device_address: I2C address of the device
        :param register_address: register address inside the device
        :param byte: data to be written
        :return:
        """
        raise NotImplementedError()

    def write_bytes(self, device_address, register_address, byte_sequence):
        """
        Writes a sequence of bytes
        :param device_address: I2C address of the device
        :param register_address: initial address inside the device
        :param byte_sequence: list of bytes to be written
        :return:
        """
        raise NotImplementedError()

    def read_byte(self, device_address, register_address):
        """
        Reads a single byte
        :param device_address: I2C address of the device
        :param register_address: register address inside the device
        :return:
        """
        raise NotImplementedError()

    def read_bytes(self, device_address, register_address, number_of_bytes):
        """
        Reads a sequence of bytes
        :param device_address: I2C address of the device
        :param register_address: initial address inside the device
        :param number_of_bytes: number of bytes requested
        :return:
        """
        raise NotImplementedError()
