import posix
from fcntl import ioctl

from plugandpie.common.i2c import *
from plugandpie.interfaces.Interface import Interface

DEFAULT_BUS = 1


class I2CInterface(Interface):
    """Performs I2C I/O transactions on an I2C bus.

    Transactions are performed by passing one or more I2C I/O messages
    to the transaction method of the I2CMaster.  I2C I/O messages are
    created with the reading, reading_into, writing and writing_bytes
    functions.

    An I2CMaster acts as a context manager, allowing it to be used in a
    with statement.  The I2CMaster's file descriptor is closed at
    the end of the with statement and the instance cannot be used for
    further I/O.

    For example:

        with I2CMaster() as i2c:
            i2c.transaction(
                writing(0x20, bytes([0x01, 0xFF])))
    """

    def __init__(self, bus=DEFAULT_BUS):
        """
        :param bus:   the number of the bus
        """
        self.bus = bus
        self.fd = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self):
        self.close()

    def open(self, extra_open_flags=0):
        """Opens the bus device.

        Arguments:
        extra_open_flags -- extra flags passed to posix.open when
                            opening the I2C bus device file (default 0;
                            e.g. no extra flags).
        """
        self.fd = posix.open("/dev/i2c-{}".format(self.bus),
                             posix.O_RDWR | extra_open_flags)

    def close(self):
        """
        Closes the I2C bus device.
        """
        posix.close(self.fd)

    def transaction(self, *msgs):
        """
        Perform an I2C I/O transaction.

        Arguments:
        *msgs -- I2C messages created by one of the reading, reading_into,
                 writing or writing_bytes functions.

        Returns: a list of byte sequences, one for each read operation
                 performed.
        """

        msg_count = len(msgs)
        msg_array = (i2c_msg*msg_count)(*msgs)
        ioctl_arg = i2c_rdwr_ioctl_data(msgs=msg_array, nmsgs=msg_count)

        ioctl(self.fd, I2C_RDWR, ioctl_arg)

        return [i2c_msg_to_bytes(m) for m in msgs if (m.flags & I2C_M_RD)]
