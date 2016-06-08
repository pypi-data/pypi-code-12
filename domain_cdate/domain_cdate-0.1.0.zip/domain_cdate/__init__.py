import asyncio
from dateutil import parser
from .data import SERVERS, CODE_PAGES, CREATION_DATE_REX

__version__ = '0.1.0'
__all__ = ('creation_date', 'WhoisConnectionError', 'WhoisError')


class WhoisConnectionError(OSError):
    pass


class WhoisError(Exception):
    pass


@asyncio.coroutine
def creation_date(domain, loop=None):
    loop = loop or asyncio.get_event_loop()
    domain = domain.encode('idna').decode()
    tld_chunks = domain.rsplit('.', 2)
    tld = tld_chunks[-1].upper()

    if len(tld_chunks) > 2:
        c_tld = (tld_chunks[-2] + '.' + tld_chunks[-1]).upper()
        if c_tld in SERVERS:
            tld = c_tld

    whois_host = SERVERS.get(tld)
    if not whois_host:
        raise WhoisError('Unsupported tld %s' % tld)

    try:
        reader, writer = yield from asyncio.open_connection(
            host=whois_host, port=43, loop=loop
        )
    except OSError as exc:
        raise WhoisConnectionError(
            '[Errno %s] Can not connect to whois server %s [%s]' %
            (exc.errno, whois_host, exc.strerror)) from exc
    try:
        writer.write((domain + "\r\n").encode())
        yield from writer.drain()
        response = yield from reader.read()
    except asyncio.IncompleteReadError as e:
        raise WhoisError(str(e))
    finally:
        writer.close()

    response = response.decode(CODE_PAGES.get(whois_host, 'utf-8'))
    response = response.replace("\r\n", "\n")

    for line in response.split("\n"):
        for pattern in CREATION_DATE_REX:
            match = pattern.match(line)
            if match:
                return parser.parse(match.group(1), fuzzy=True).date()

    raise WhoisError('Can not find creation date')
