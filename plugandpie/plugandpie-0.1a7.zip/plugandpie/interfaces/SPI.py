"""
This module implements the SPI(Interface) class
"""
from plugandpie.interfaces.__model__ import InterfaceAdapter


class SPIAdapter(InterfaceAdapter):
    def close(self):
        pass

    def open(self):
        pass

    def write_bytes(self, device_address, register_address, byte_sequence):
        pass

    def read_bytes(self, device_address, register_address, number_of_bytes):
        pass

    def read_byte(self, device_address, register_address):
        pass

    def write_byte(self, device_address, register_address, byte):
        pass
