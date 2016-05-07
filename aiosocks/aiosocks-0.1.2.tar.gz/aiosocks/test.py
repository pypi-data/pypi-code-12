import asyncio
import aiohttp
from aiosocks import (
    Socks4Addr, Socks5Addr, Socks4Auth, Socks5Auth
)
from aiosocks.connector import SocksConnector
from aiohttp.resolver import AsyncResolver


async def test():
    resolver = AsyncResolver()

    conn = SocksConnector(proxy=Socks5Addr('127.0.0.1'),
                          proxy_auth=Socks5Auth('proxyuser1', 'password1'),
                          remote_resolve=True, resolver=resolver)

    with aiohttp.ClientSession(connector=conn) as session:
        async with session.get('http://vk.com') as resp:
            if resp.status == 200:
                print(await resp.text())
            else:
                print(resp.status)


loop = asyncio.get_event_loop()
loop.run_until_complete(test())
loop.close()
