

class Interface:
    def open(self):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()

    def write_byte(self, device_address, register_address, byte):
        raise NotImplementedError()

    def write_bytes(self, device_address, register_address, byte_sequence):
        raise NotImplementedError()

    def read_byte(self, device_address, register_address):
        raise NotImplementedError()

    def read_bytes(self, device_address, register_address, number_of_bytes):
        raise NotImplementedError()
