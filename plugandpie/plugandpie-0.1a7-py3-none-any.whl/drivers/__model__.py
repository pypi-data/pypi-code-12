"""
This module contains the model for the drivers implementation.
Those classes should not be instantiated directly and therefore belong to a private module.
"""


class Register(object):
    """
    This class has direct access to one register in one device.
    It caches values on access, and gives the option to get the cached value preferably.

    This class should not be used directly, but only as an internal structure of a driver.
    """

    def __init__(self, interface, device_address, register_address):
        self.interface = interface
        self.device_address = device_address
        self.register_address = register_address
        self._cached_value = None

    def set(self, value):
        """
        Set the value of the register and updates the cached value.
        :param value: data to be written
        :return:
        """
        self.interface.write_byte(self.device_address, self.register_address, value)
        self._cached_value = value

    def get(self, cached=False):
        """
        Get the value of the register and updates the cached value.
        Optionally gets the cached value only, not making a read request.
        :param cached: True if wanted the cached value, defaults to False
        :return: the register value
        """
        if cached and self._cached_value is not None:
            return self._cached_value
        self._cached_value = self.interface.read_byte(self.device_address, self.register_address)
        return self._cached_value


class Driver(object):
    """
    This class is the basis for any device driver and consists of an interface, addresses
    and a dictionary that maps register names into its Register object instance accessor.
    Some boards have multiple sensors and they occupy different bus addresses, thus address handling
    is done explicitly in the subclasses.

    This class serves mainly as a base class for all drivers and should not be instantiated
    directly, but only through the DriverBuilder module for easier construction.
    """

    def __init__(self, interface):
        self.interface = interface
        self.registers = {}


class GenericDriver(Driver):
    """
    This class is the fallback for devices that have no drivers implemented or
    have no configuration imported from a datasheet. It simply facilitates reading
    registers indexed by number, so they can still be accessed independently.
    """
    def __init__(self, interface, address, n_registers=128):
        super(GenericDriver, self).__init__(interface)
        self.address = address
        for i in range(n_registers):
            self.registers[i] = Register(interface, address, i)
