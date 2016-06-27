"""
Module to fetch and parse regional NIC delegation data
"""
import urllib.parse
import ftplib
import os
from functools import lru_cache
import socket
import ipaddress
from binascii import hexlify
import tempfile

TWD = tempfile.gettempdir()

DELEGATES = [
    # America (non-latin)
    "ftp://ftp.arin.net/pub/stats/arin/delegated-arin-extended-latest",
    # Europe
    "ftp://ftp.ripe.net/ripe/stats/delegated-ripencc-extended-latest",
    # Africa
    "ftp://ftp.afrinic.net/pub/stats/afrinic/delegated-afrinic-extended-latest",
     # Asia & Pacific
    "ftp://ftp.apnic.net/pub/stats/apnic/delegated-apnic-extended-latest",
    # Latin-America
    "ftp://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-extended-latest",]


@lru_cache(None)
def _split_url(url):
    "Split delegate url into host, file_path and file_name."
    url = urllib.parse.urlparse(url)
    host = url.netloc
    file_path, file_name = url.path.rsplit('/', 1)
    return (host, file_path, file_name)

def _file_details(ftp, file_name):
    "Retrieve details of the file."
    details = None
    print('# Retrieving file details')
    try:
        listing = list(ftp.mlsd())
        print('# Server support mlsd, extracting details ...')
        for entry in listing:
            name, facts = entry
            if name.lower() == file_name.lower():
                details = facts
                details['name_local'] = name
                details['name_remote'] = name
                break

    except ftplib.error_perm:
        print('# Server does not support mlsd, falling back.')
        tmp = list()
        ftp.retrlines('LIST %s' % file_name, callback=tmp.append)
        if '->' in tmp[0]:
            print('# Fall back: entry is a symbolic link, following ...')
            link2name = tmp[0].split('->')[1].strip()
            tmp = list()
            ftp.retrlines('LIST %s' % link2name, callback=tmp.append)

        details = dict()
        tmp = tmp[0]
        tmp = tmp.rsplit(' ', 1)[0]
        details['name_local'] = file_name
        details['name_remote'] = link2name
        tmp, details['size'], month, day, time = tmp.rsplit(' ', 4)
        details['modify'] = '_'.join([month, day, time.replace(':', '')])

    return details

def download(url):
    "Download the url."
    host, file_path, file_name = _split_url(url)

    print('# Connecting to: %s' % host)
    ftp = ftplib.FTP(host)

    print('# Logging in ...')
    ftp.login()

    print('# Changing cwd to: %s' % file_path)
    ftp.cwd(file_path)

    details = _file_details(ftp, file_name)

    file_cache = '_'.join([details['name_local'],
                           details['size'],
                           details['modify']])
    file_cache += '.csv'

    if file_cache in os.listdir(TWD):
        print('# File is already downloaded !')
        return

    print('# Downloading ...')

    retr = 'RETR %s' % details['name_remote']
    local_file = os.path.join(TWD, file_cache)
    ftp.retrbinary(retr, open(local_file, 'wb').write)

    print('# Downloaded!')


# The parsing part of the program
def _address_range_ipv4(address, width):
    "Convert IPv4 address and amount to integer range."
    # The width of ipv4 addresses is given in number of addresses which
    # are not bounded by exact netmasks for example a width of 640 addresses.
    blocks = address.split('.')
    for index, block in enumerate(blocks):
        blocks[index] = bin(int(block, 10))[2::].zfill(8)
    blocks = ''.join(blocks)
    network = int(blocks, 2)
    broadcast = network + int(width) - 1
    return(network, broadcast)

def _ipv6_to_int(ipv6_address):
    "Convert an IPv6 address to an integer"
    packed_string = socket.inet_pton(socket.AF_INET6, ipv6_address.exploded)
    return int(hexlify(packed_string), 16)

def _address_range_ipv6(address, width):
    "Convert IPv6 address and broadcast to integer range."
    network = ipaddress.ip_network(address+'/'+width)
    broadcast = _ipv6_to_int(network.broadcast_address)
    network = _ipv6_to_int(network.network_address)
    return(network, broadcast)

def _address_range(ipv, address, width):
    "From an IP address create integers for the network and broadcast IP"
    # This is essentially the range which in between an IP address is.
    if ipv == 4:
        # IPv4, the width is given as the number of IPs
        network, broadcast = _address_range_ipv4(address, width)
    else:
        # IPv6, width is given by a netmask.
        network, broadcast = _address_range_ipv6(address, width)

    return (network, broadcast)

def _parse_row(row):
    "Parse and modify the row."
    columns = row.strip().split('|')
    # If there isn't more then 6 columns I can't parse it, so skipping it.
    if len(columns) > 6:
        tmp = columns[:5]

        if len(tmp[1].strip()) == 0:
            # This is the country it is assigned to, if there is no country
            # I am not interested in it.
            return None

        if tmp[2].strip().lower() not in ['ipv4', 'ipv6']:
            # If the protocol is not an IP protocol (such as asn), I am not
            # interested.
            return None

        if '6' in tmp[2]:
            tmp[2] = 6
        else:
            tmp[2] = 4

        # Convert the IP address and netmask/number of IP's to an IP range where
        # the IPs are converted to a numerical value.
        tmp[3], tmp[4] = _address_range(tmp[2], tmp[3], tmp[4])
        return tmp


class CompactRanges(object):
    "Try to compact the ranges."
    def __init__(self):
        self.ranges = list()

    def add(self, *newer):
        "Add a line to the ranges, compacting where possible."
        # nic, tld, ipv, network, broadcast = *newer
        newer = list(newer)

        if len(self.ranges) == 0:
            self.ranges.append(newer)
            return

        # Testing if current range is a continuation of the previous one
        older = self.ranges[-1]
        if older[0] == newer[0] and \
           older[1] == newer[1] and \
           older[2] == newer[2] and \
           older[4] == newer[3] - 1:
            # The older broadcast is the same as newer network - 1, thus is is a
            # continuation, so extending the range of the older one.
            self.ranges[-1][4] = newer[4]
        else:
            self.ranges.append(newer)

    def length(self):
        "return length of ranges"
        return len(self.ranges)


def _local_file_from_url(url):
    "Open the file, if available from the url"
    file_name = _split_url(url)[2]
    candidates = list()

    for candidate in os.listdir(TWD):
        if file_name.lower() in candidate.lower():
            candidates.append(candidate)

    candidates.sort(reverse=True)
    if len(candidates) == 0:
        print('# No files to parse')
        return None

    file_full = os.path.join(TWD, candidates[0])
    return file_full

def parse_latest(url):
    "Parse a file as it has been retrieved from the url."
    file_name = _local_file_from_url(url)
    if file_name is None:
        print('# No files available to parse !')
        return

    print('# Opening file: %s' % file_name)

    compacted = CompactRanges()
    count_linesall = 0
    count_relevant = 0
    with open(file_name, 'r') as file_open:
        for row in file_open:
            count_linesall += 1
            parsed = _parse_row(row)
            if parsed is None:
                continue

            count_relevant += 1
            compacted.add(*parsed)

    print('# Parsed %s lines' % count_linesall)
    print('#  - of which relevant: %s' % count_relevant)
    print('#  - reduced to ranges: %s' % compacted.length())
    return compacted.ranges

def _compact_string(text):
    "try making text compacter"
    # we go through the text and try to replace repeated characters with:
    # _c_n_  where c is the character and n is the amount of if. The underscore
    # in this context is guaranteed to not occur in text. As such we can use
    # it as an escape character.
    # Also we do not collapse if repeated character is below 5.
    tmp = list()
    last = ''
    count = 0
    for character in text+'_':
        # Add the underscore so we make sure not to miss the last bit of the
        # string if it happens to end on more then 4 identical characters.
        count += 1
        if character != last:
            if count > 4:
                tmp = tmp[:len(tmp)-count]
                tmp.append('_%s_%s_' % (last, count))

            count = 0

        last = character
        tmp.append(character)

    # Remove the appended underscore before returning.
    return ''.join(tmp)[:-1]

def get():
    "Fetch and parse data"
    print('#'*79)
    print('# Fetching data from regional NICs.')
    print('#'*79)
    tmp = list()
    for delegate in DELEGATES:
        print('# Using: %s' % delegate)
        download(delegate)
        tmp += parse_latest(delegate)
        print('#' * 79)
    print('# A total of %s IP ranges have been defined.' % len(tmp))

    for nic, country, ipv, network, broadcast in tmp:
        hex_network = hex(network)[2::].zfill(32)
        hex_broadcast = hex(broadcast)[2::].zfill(32)
        rid = nic[:2]+country+str(ipv)+hex_broadcast+hex_network
        rid = rid.lower()
        rid = _compact_string(rid)
        yield rid, nic, country, ipv, hex_network, hex_broadcast
