import asyncio
import logging
import sys
import ZEO.asyncio

[port] = sys.argv[1:]

logging.basicConfig(level='INFO')

p = ZEO.asyncio.ClientProtocol(('127.0.0.1', int(port)))
print(p.loop.run_until_complete(p.connect()))
print(p.loop.run_until_complete(p.call('loadEx', b'\0'*8)))


