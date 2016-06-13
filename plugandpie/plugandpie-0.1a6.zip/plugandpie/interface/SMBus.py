"""
This module implements the SMBus(Interface) class
"""
from plugandpie.interface.Interface import Interface
import smbus


class SMBusInterface(Interface):
    """
    This class implements the SMBus interface for read/write access through the SMBus protocol.
    It is based on I2C and therefore use the same bus, but requires repeated starts on the
    I2C driver from the master.
    """
    def __init__(self, bus_number):
        self.bus = smbus.SMBus(bus_number)
        self.bus_number = bus_number

    def open(self):
        self.bus.open(self.bus_number)

    def close(self):
        self.bus.close()

    def write_byte(self, device_address, register_address, byte):
        self.bus.write_byte_data(device_address, register_address, byte)

    def write_bytes(self, device_address, register_address, byte_sequence):
        self.bus.write_i2c_block_data(device_address, register_address, byte_sequence)

    def read_byte(self, device_address, register_address):
        return self.bus.read_byte_data(device_address, register_address)

    def read_bytes(self, device_address, register_address, number_of_bytes):
        return self.bus.read_i2c_block_data(device_address, register_address, number_of_bytes)
