import asyncio
import aiohttp
import logging
import aiosocks
from aiosocks import (
    Socks4Addr, Socks5Addr, Socks4Auth, Socks5Auth,
    HttpProxyAddr, HttpProxyAuth
)
from aiosocks.connector import SocksConnector

logger = logging.getLogger('asyncio')
logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)


@asyncio.coroutine
def test():
    conn = SocksConnector(proxy=Socks5Addr('127.0.0.1'),
                          proxy_auth=Socks5Auth('proxyuser1', 'password1'),
                          remote_resolve=False, fingerprint=b'\xfc\xeb\xf8\t\xabg\xfd\xee\xae\xf2OY\xa6z\xcc,_\xa8\x84\xf2')
    #conn = None
    # conn = ProxyConnector(HttpProxyAddr('http://localhost:8080'),
    #                       proxy_auth=HttpProxyAuth('proxyuser1', 'password1'))

    with aiohttp.ClientSession(connector=conn) as session:
        resp = yield from session.get('https://habrahabr.ru')
        if resp.status == 200:
            print((yield from resp.text()))
        else:
            print(resp.status)
        resp.release()

    # transport, protocol = yield from aiosocks.create_connection(
    #     None, Socks5Addr('127.0.0.1'), Socks5Auth('proxyuser1', 'password1'),
    #     dst=('habrahabr.ru', 80), remote_resolve=False
    # )
    # protocol.pause_writing()


loop = asyncio.get_event_loop()
loop.set_debug(1)
loop.run_until_complete(test())
loop.close()
