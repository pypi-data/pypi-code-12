#!/usr/bin/python
# -*- coding:utf-8 -*-

# @Author: fsxchen
# @Date:   2016-04-19T11:21:46+08:00
# @Last modified by:   fsxchen
# @Last modified time: 2016-04-19T11:24:18+08:00
"""
产生ip地址
"""

import sys
import os
import re
import socket
import struct

#ip address Reg
ipReg = "^(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[0-9]{1,2})(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[0-9]{1,2})){3}$"
pattern = re.compile(ipReg)


def is_ip(ip):  # is a ip?
    return True if re.match(pattern, ip) else False


def is_net_mask(netmask):  #  like 192.168.1.0/24
    if "/" in netmask:
        try:
            ip, netmask = netmask.split("/")
        except Exception, e:
            print e
        if re.match(pattern, ip) is not None and int(netmask) <= 32 and int(netmask) >= 0:
            return True
        else:
            return False
    else:
        return False


def is_ip_range(ipRange):  # is ip range?
    if "-" in ipRange:
        try:
            ipStart, end = ipRange.split("-")
        except Exception, e:
            print e

        if re.match(pattern, ipStart) is not None:
            try:
                return "reage_A" if 0 < int(end) and int(end) <= 255 else False  #like 192.168.1-255
            except ValueError:
                return "range_B" if re.match(pattern, end) else False  # like 192.168.1.0-192.168.1.255
            except Exception, e:
                print e
        else:
            return False
    else:
        return False


def ip_create(line):  #create ip address
    if is_ip(line):
        yield line.strip()
    elif is_net_mask(line):  # if it likes  192.168.1.0/24
        ip, netmask = line.split("/")
        netmask = int(netmask)
        hoip = socket.ntohl(struct.unpack("i", socket.inet_aton(ip))[0])
        for i in range(1, 2**(32 - netmask) - 1):
            hoip = int(hoip) + 1
            ip = socket.inet_ntoa(struct.pack('I', socket.ntohl(hoip)))
            yield ip

    elif is_ip_range(line) == "reage_A":
        ipstart, end = line.split("-")
        point = [int(ipstart.split(".")[-1]), int(end)] if (
            int(end) > int(ipstart.split(".")[-1])) else [int(end), int(ipstart.split(".")[-1])]
        interval = point[1] - point[0]

        ipstartlist = ipstart.split(".")
        ipstartlist[-1], ste = [str(point[0]), interval] if point[0] == 0 else [str(point[0] - 1), interval + 1]
        ipstart = ".".join(ipstartlist)
        hoip = socket.ntohl(struct.unpack("I", socket.inet_aton(ipstart))[0])

        ste = ste - 1 if point[1] == 255 else ste
        slist = range(ste)
        for i in slist:
            hoip = int(hoip) + 1
            ip = socket.inet_ntoa(struct.pack('I', socket.ntohl(hoip)))
            yield ip

    elif is_ip_range(line) == "range_B":
        ipstart, ipend = line.split("-")
        IipStart = socket.ntohl(struct.unpack("I", socket.inet_aton(ipstart))[0])
        IipEnd = socket.ntohl(struct.unpack("I", socket.inet_aton(ipend))[0])
        ipArry = [IipStart, IipEnd] if IipStart < IipEnd else [IipEnd, IipStart]
        interval = ipArry[1] - ipArry[0]
        for i in range(interval - 1):
            ipArry[0] = ipArry[0] + 1
            ip = socket.inet_ntoa(struct.pack('I', socket.ntohl(ipArry[0])))
            yield ip


def ip2cidrip(ip):  #change ip to cidr
    if isIP(ip):
        A, B, C, D = ip.split(".")
        if int(A) <= 127:
            cidrIP = A + ".0.0.0/8"
            return cidrIP
        elif int(A) <= 191 and int(A) > 127:
            cidrIP = A + '.' + B + '.0.0/16'
            return cidrIP
        elif int(A) < 224 and int(A) > 191:
            cidrIP = A + '.' + B + '.' + C + '.0/24'
            return cidrIP
    else:
        return "Error, the ip is not right!"


def ip_handle(filename):
    """
	handle a ip or a file about ips
    """
    if type(filename) is str:
        if os.path.isfile(filename):
            with open(filename, 'r') as fd:
                for line in fd.readlines():
                    yield ip_create(line)
        else:
            yield ip_create(filename)

    elif type(filename) is list:
        for ip in filename:
            if isIP(ip) or isNetMask(ip) or isIpRange(ip):
                yield ip_create(ip)
    elif type(filename) is tuple:
        for a in filename:
            for ip in a:
                if isIP(ip) or isNetMask(ip) or isIpRange(ip):
                    yield ip_create(ip)
    else:
        pass


if __name__ == "__main__":
    for ip in ip_handle(sys.argv[1]):
        for a in ip:
            print a
