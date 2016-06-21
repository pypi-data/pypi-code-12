"""This module contains the curated map between I2C addresses and device drivers automatically detected."""
from plugandpie.drivers.accelerometers import MMA8452Q

I2C_MAP = {
    "1d": MMA8452Q
}
