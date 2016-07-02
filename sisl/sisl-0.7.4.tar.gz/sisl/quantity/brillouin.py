"""
Define helper routines for interacting with the Brillouin
zone
"""

import numpy as np


class BrillouinZone(object):
    """ Class to hold k-points and associated weights """

    def __init__(self, args):
        """
        Initialize the `BrillouinZone` object.
        """
