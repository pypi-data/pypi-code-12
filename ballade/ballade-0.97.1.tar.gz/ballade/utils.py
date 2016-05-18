import sys
import socket
import ipaddress


def set_socket(s, keep_alive=True):
    # TCP socket保活
    if keep_alive and sys.platform == 'linux':
        s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        s.setsockopt(socket.SOL_TCP, socket.TCP_KEEPIDLE, 30)
        s.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, 5)
        s.setsockopt(socket.SOL_TCP, socket.TCP_KEEPCNT, 3)


def get_socket(ipv6=False, keep_alive=True):
    s = socket.socket(socket.AF_INET6 if ipv6 else socket.AF_INET, socket.SOCK_STREAM, 0)
    set_socket(s, keep_alive=keep_alive)
    return s


def has_ipv6_address(host):
    try:
        socket.getaddrinfo(host, None, family=socket.AF_INET6)
    except socket.gaierror:
        return False
    return True


def is_host_match_ip_list(host, list):
    address_tuple_list = []
    try:
        address_tuple_list = socket.getaddrinfo(host, None, family=socket.AF_INET)
    except socket.gaierror:
        return False
    if address_tuple_list:
        address = ipaddress.IPv4Address(address_tuple_list[0][4][0])
        for list_e in list:
            if address in ipaddress.IPv4Network(list_e):
                    return True
    return False


def hostport_parser(hostport, default_port):
    # Because IPv6 address hostport like "2001:067c:04e8:f004:0000:0000:0000:000a:443"
    # Must use rfind to find ":"
    # RFC2396 Uniform Resource Identifiers (URI): Generic Syntax was updated by
    # RFC2732 Format for Literal IPv6 Addresses in URL's. Specifically, section 3 in RFC2732.
    i = hostport.rfind(b':' if isinstance(hostport, bytes) else ':')
    if i >= 0:
        # Type of bytes' element is int
        if hostport[0] == ord('['):  # If address with bracket
            host = hostport[1:i-1]
        else:
            host = hostport[:i]
        return host, int(hostport[i + 1:])
    else:
        return hostport, default_port


def header_parser(headers):
    for header in headers.split(b'\r\n'):
        i = header.find(b':')
        if i >= 0:
            yield header[:i].lower(), header[i + 2:]  # Lower the case for header comparison


def header_dict_parser(header_dict):
    result = b''
    for k, v in header_dict.items():
        result += k + b': ' + v + b'\r\n'
    result += b'\r\n'
    return result


def netloc_parser(netloc, default_port=-1):
    assert default_port
    i = netloc.rfind(b'@' if isinstance(netloc, bytes) else '@')
    if i >= 0:
        return netloc[:i], netloc[i + 1:]
    else:
        return None, netloc


def write_to(stream):
    def on_data(data):
        if data == b'':
            stream.close()
        else:
            if not stream.closed():
                stream.write(data)

    return on_data


def pipe(stream_a, stream_b):
    writer_a = write_to(stream_a)
    writer_b = write_to(stream_b)
    stream_a.read_until_close(writer_b, writer_b)
    stream_b.read_until_close(writer_a, writer_a)


def subclasses(cls, _seen=None):
    if _seen is None:
        _seen = set()
    subs = cls.__subclasses__()
    for sub in subs:
        if sub not in _seen:
            _seen.add(sub)
            yield sub
            for sub_ in subclasses(sub, _seen):
                yield sub_
