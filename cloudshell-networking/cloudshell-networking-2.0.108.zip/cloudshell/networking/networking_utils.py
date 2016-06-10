__author__ = 'oei'

import re
import socket
import struct
import math

def normalizePath(path):
    """
    :param path:
    :return:
    """
    ret_path = re.sub('#', '%23', path)
    ret_path = re.sub(' ', '%20', ret_path)

    return ret_path

ip2int = lambda ipstr: struct.unpack('!I', socket.inet_aton(ipstr))[0]
int2ip = lambda n: socket.inet_ntoa(struct.pack('!I', n))

def isInteger(s):
    try:
        int(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


def normalizeStr(tmpStr):
    tmpStr = str(tmpStr)
    tmpStr = tmpStr.replace(' ', '')
    tmpStr = tmpStr.replace(',', '.')
    tmpStr = tmpStr.replace('N/A', '')
    tmpStr = tmpStr.replace('Future', '')
    tmpStr = tmpStr.replace('', '')

    return tmpStr

def getNewIP(ipaddress, wMask):
    '''Ip calculator to generate masked Ip address from received params

    :param ipaddress: ip address to mask
    :param wMask: wild card mask
    :return:
    '''
    ip_octets = ipaddress.split('.')
    mask_octets = wMask.split('.')
    new_ip = []
    for i in range(len(ip_octets)):
        new_ip.append(str(int(ip_octets[i]) + int(mask_octets[i])))

    return '.' . join(new_ip)

def validateIP(str):
    """Validate if provided string matches IPv4 with 4 decimal parts
    """

    octets = str.strip('\"\r').split('.')
    if len(octets) != 4:
        return False

    for x in octets:
        if not x.isdigit():
            return False

    for octet in octets:
        i = int(octet)
        if i < 0 or i > 255:
            return False
    return True

def validateVlanNumber(number):
    try:
        if int(number) > 4000 or int(number) < 1:
            return False
    except ValueError:
        return False
    return True

def validateVlanRange(vlan_range):
    for vlan in vlan_range.split(','):
        if '-' in vlan:
            for vlan_range_border in vlan.split('-'):
                result = validateVlanNumber(vlan_range_border)
        else:
            result = validateVlanNumber(vlan)
        if not result:
            return False
    return True

def validateSpanningTreeType(data):
    spanningTreeTypes = ['bridge', 'domain', 'lc-issu', 'loopguard', 'mode', 'mst',
                         'pathcost', 'port', 'pseudo-information', 'vlan']
    if data in spanningTreeTypes:
        return True
    return False

def verifyIpInRange(ip_address, start_addr, end_addr):
    """Validate if provided IP address matches provided network range

    :return: True/False
    """

    start_list = map(int, start_addr.split('.'))
    end_list = map(int, end_addr.split('.'))
    ip_list = map(int, ip_address.split('.'))

    for i in range(len(ip_list)):
        if (ip_list[i] < start_list[i]) or (ip_list[i] > end_list[i]):
            return False

    return True


def validateMAC(str):
    """Validate if provided string matches MAC address pattern
    """
    return re.match ('^([0-9A-F]{2}[:-]){5}([0-9A-F]{2})$', str.upper())

def getBroadCastAddress(ip, mask):
    """Calculate broadcast IP address for provided IP and subnet
    """
    #fixme need lib
    #network = ipcalc.Network(ip, mask)
    #return str(network.broadcast())

def getIpInfo(ipStr):
    """Get IANA allocation information for the current IP address.
    """
    #fixme need lib
    #ip = ipcalc.IP(ipStr)
    #return ip.info()

def getSubnetCidr(ip, mask):
    """Get subnet in CIDR format, ex: 255.255.255.0 - 24
    """
    #fixme need lib
    #return ipcalc.Network('{}/{}'.format(ip, mask)).subnet()

def getNetworkAddress(ip, mask):
    """Network slice calculations.

    :param ip: network address
    :param mask: netmask

    :return networkAddress: string

    """
    #fixme need lib
    #return str(ipcalc.Network(ip, mask).network())


#fixme add comments
def getMatrixFromString(data_str):
    lines = data_str.split('\n')

    lines = filter(
        lambda value:
        value != '',
        lines)

    if len(lines) <= 1:
        return {}

    del lines[-1]
    del lines[0]

    pattern_def_line = re.compile('-{2,}')

    columns_count = 0
    column_lens = []

    for line in lines:
        data = pattern_def_line.findall(line)
        if data:
            lines.remove(line)
            for element in data:
                column_lens.append(len(element))
            break

    data_matrix = {}

    data_index_names = {}

    pattern_not_space = re.compile('\S+')

    for line in lines:
        index = 0
        position = 0
        for column_len in column_lens:
            column_line = line[position : position + column_len]

            column_line_list = pattern_not_space.findall(column_line)
            column_line = ''
            for col_index in range(0, len(column_line_list) - 1):
                column_line += column_line_list[col_index] + ' '
            column_line += column_line_list[len(column_line_list) - 1]

            column_data = []
            if index < len(data_matrix):
                column_data = data_matrix[data_index_names[index]]

                column_data.append(column_line)
            else:
                data_index_names[index] = column_line.lower()
                data_matrix[column_line.lower()] = column_data

            position += column_len + 1
            index += 1

    return data_matrix


def shieldString(data_str):
    iter_object = re.finditer('[\{\}\(\)\[\]\|]', data_str)

    list_iter = list(iter_object)
    iter_size = len(list_iter)
    iter_object = iter(list_iter)

    new_data_str = ''
    current_index = 0

    if iter_size == 0:
        new_data_str = data_str

    for match in iter_object:
        match_range = match.span()

        new_data_str += data_str[current_index:match_range[0]] + '\\'
        new_data_str += data_str[match_range[0]:match_range[0] + 1]

        current_index = match_range[0] + 1

    return new_data_str

def normalize_buffer(input_buffer):
    """
    Method for clear color fro input_buffer and special characters
    """

    color_pattern = re.compile('\[[0-9]+;{0,1}[0-9]+m|\[[0-9]+m|\b|' + chr(27))            # 27 - ESC character

    result_buffer = ''

    match_iter = color_pattern.finditer(input_buffer)

    current_index = 0
    for match_color in match_iter:
        match_range = match_color.span()
        result_buffer += input_buffer[current_index:match_range[0]]
        current_index = match_range[1]

    result_buffer += input_buffer[current_index:]

    return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', result_buffer)

def getDictionaryData(source_dictionary, forbidden_keys):
    destination_dictionary = {}
    for key, value in source_dictionary.iteritems():
        if key in forbidden_keys:
            continue

        destination_dictionary[key] = value

    return destination_dictionary

def getBitSize(bandwidth):
    bandwidth = bandwidth.lower()
    multiplier = 1
    if re.search('kbit/sec', bandwidth):
        multiplier = 2**10
    elif re.search('mbit/sec', bandwidth):
        multiplier = 2**20
    elif re.search('gbit/sec', bandwidth):
        multiplier = 2**30

    bits = int(re.search('\d+', bandwidth).group()) * multiplier

    return math.log10(bits)
