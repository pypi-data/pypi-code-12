#!/usr/bin/python3

import argparse
import asyncio
import logging
import pylinkbotd
import traceback

#asyncio.get_event_loop().set_debug(True)
logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("--host", help="specify the hostname the server should bind to")
parser.add_argument("--port", help="spcefiy the port the server should bind to", type=int)

args = parser.parse_args()

if args.host:
    hostname = args.host
else:
    hostname = 'localhost'

if args.port:
    port = args.port
else:
    port = 42000

@asyncio.coroutine
def task(hostname, port):
    server = yield from pylinkbotd.DaemonListenServer.create(hostname, port)

num_retries = 0
max_retries = 10
while True:
    try:
        asyncio.get_event_loop().run_until_complete(task(hostname, port))
        asyncio.get_event_loop().run_forever()
        asyncio.get_event_loop().close()
    except KeyboardInterrupt:
        break
    except Exception as e:
        traceback.print_exc()
        if num_retries > max_retries:
            break
        num_retries += 1
        logging.warning('Caught unhandled exception. Restarting daemon...')
        loop = asyncio.get_event_loop()
        loop.close()
        newloop = asyncio.new_event_loop()
        asyncio.set_event_loop(newloop)
