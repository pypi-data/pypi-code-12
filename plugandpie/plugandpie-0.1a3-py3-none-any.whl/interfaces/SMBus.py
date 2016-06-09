from plugandpie.interfaces.Interface import Interface
import smbus


class SMBusInterface(Interface):
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


class SMBusRegister:
    def __init__(self, interface,  device_address, register_address):
        self.interface = interface
        self.device_address = device_address
        self.register_address = register_address
        self._cached_value = None

    def set(self, v):
        self.interface.write_byte(self.device_address, self.register_address, v)
        self._cached_value = v

    def get(self, cached=False):
        if cached and self._cached_value is not None:
            return self._cached_value
        self._cached_value = self.interface.read_byte(self.device_address, self.register_address)
        return self._cached_value
