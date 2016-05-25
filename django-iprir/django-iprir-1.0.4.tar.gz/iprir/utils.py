"""
utils for ip registry (iprir) project

easily convert an ip address to a number and back,
functions are used in models.py views and helpers
"""

import socket
import struct


def ip2int(addr):

    """
    Turns an IP address into a number
    """

    return struct.unpack("!I", socket.inet_aton(addr))[0]


def int2ip(addr):

    """
    Turns a number into an IP address
    """

    return socket.inet_ntoa(struct.pack("!I", addr))
