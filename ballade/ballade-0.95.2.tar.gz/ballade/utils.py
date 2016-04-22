import socket
import ipaddress
import logging
import os
import sys
import shutil
import socket


def get_config_dir():
    if sys.platform == 'win32':
        home = os.environ['HOMEPATH']
    else:
        home = os.environ['HOME']
    try:
        config_dir = os.path.join(os.path.join(home, '.config'), 'ballade')
    except KeyError:
        config_dir = ''
    return config_dir


def init_config_dir(config_dir):
    sample_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sample')
    # os.mkdir(config_dir) # copytree need the dst doesn't exist
    shutil.copytree(os.path.join(os.path.join(sample_path, '.config'), 'ballade'), config_dir)


def is_ipv6_accessible(config):
    host = config['ipv6_test']['host']
    port = config['ipv6_test']['port']
    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
        s.close()
        return True
    except:
        return False


def has_ipv6_address(host):
    try:
        addrinfo_list = socket.getaddrinfo(host, 'http')
    except socket.gaierror:
        return False
    for addrinfo in addrinfo_list:
        addr = addrinfo[-1][0]
        if isinstance(ipaddress.ip_address(addr), ipaddress.IPv6Address):
            return True
    return False


def omega_converter(config, source, destination):
    proxy_dict = config['proxy']['profile']
    for k, v in config['proxy']['virtual'].items():
        if v in proxy_dict.keys():
            proxy_dict[k] = proxy_dict[v]
    with open(source, 'r') as s:
        head, _ = os.path.split(destination)
        if not os.path.exists(head):
            os.makedirs(head)
        with open(destination, 'w') as d:
            for line in s:
                line = line.replace('\n', '')
                result = line.split(' +')
                if len(result) == 2:
                    host, proxy = result
                    host = host.replace('.', r'\.')
                    host = host.replace('*', '.*')
                    # 因为Omega实际上是把 "*." 看作可出现零次或者一次处理的
                    if host[:4] == ".*\.":
                        host = "(.*\.)?" + host[4:]
                    proxy = proxy_dict[proxy]
                    d.write(host + ' ' + proxy + "\n")
    logging.debug("Convert complete")


def hostport_parser(hostport, default_port):
    i = hostport.find(b':' if isinstance(hostport, bytes) else ':')
    if i >= 0:
        return hostport[:i], int(hostport[i + 1:])
    else:
        return hostport, default_port


def header_parser(headers):
    for header in headers.split(b'\r\n'):
        i = header.find(b':')
        if i >= 0:
            yield header[:i], header[i + 2:]


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