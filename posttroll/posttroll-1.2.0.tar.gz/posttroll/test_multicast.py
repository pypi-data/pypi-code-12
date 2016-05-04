#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013 Martin Raspaud

# Author(s):

#   Martin Raspaud <martin.raspaud@smhi.se>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Test multicasting.

Bits from http://pymotw.com/2/socket/multicast.html
"""

#### Send

from posttroll.message_broadcaster import broadcast_port


import socket
import struct
import sys

MC_GROUP = "225.0.0.212" # was '224.3.29.71'

def send():

    message = 'very important data'
    multicast_group = (MC_GROUP, 10000)

    # Create the datagram socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Set a timeout so the socket does not block indefinitely when trying
    # to receive data.
    sock.settimeout(0.2)

    # Set the time-to-live for messages to 1 so they do not go past the
    # local network segment.
    ttl = struct.pack('b', 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    print >>sys.stderr, 'sending "%s"' % message
    sent = sock.sendto(message, multicast_group)

    sock.close()

def recv():

    import socket
    import struct
    import sys

    multicast_group = MC_GROUP
    server_address = ('', 10000)

    # Create the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Bind to the server address
    sock.bind(server_address)

    # Tell the operating system to add the socket to the multicast group
    # on all interfaces.
    group = socket.inet_aton(multicast_group)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    print >>sys.stderr, '\nwaiting to receive message'
    data, address = sock.recvfrom(1024)

    print >>sys.stderr, 'received %s bytes from %s' % (len(data), address)
    print >>sys.stderr, data

    sock.close()


from posttroll.bbmcast import mcast_sender, mcast_receiver, MulticastSender, MulticastReceiver

def send2():
    sock, group = mcast_sender()
    message = 'very important data'
    
    print >>sys.stderr, 'sending "%s"' % message
    sent = sock.sendto(message, (group, broadcast_port))

    sock.close()


def recv2():
    sock, group = mcast_receiver(broadcast_port)
    
    
    print >>sys.stderr, '\nwaiting to receive message'
    data, address = sock.recvfrom(1024)

    print >>sys.stderr, 'received %s bytes from %s' % (len(data), address)
    print >>sys.stderr, data

    sock.close()

def send3():
    message = 'very important data'
    ms = MulticastSender(broadcast_port)
    print >>sys.stderr, 'sending "%s"' % message
    ms(message)
    ms.close()


def recv3():
    mr = MulticastReceiver(broadcast_port)
    print >>sys.stderr, '\nwaiting to receive message'
    data, address = mr()
    print >>sys.stderr, 'received %s bytes from %s' % (len(data), address)
    print >>sys.stderr, data
    mr.close()
