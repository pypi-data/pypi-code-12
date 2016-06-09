import re
from subprocess import check_output


def i2c_addresses():
    address_map = check_output(["i2cdetect", "-y", "1"]).decode("utf-8")
    return [address.strip() for address in re.findall("[0-9A-Fa-f]{2} ", address_map)]


def twos_complement(value, bits):
    """Signs a value with an arbitrary number of bits."""
    if value >= (1 << (bits - 1)):
        value = -((~value + 1) + (1 << bits))
    return value
