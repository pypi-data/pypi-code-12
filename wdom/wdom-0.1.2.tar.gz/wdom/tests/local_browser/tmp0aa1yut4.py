
import sys
import asyncio

from wdom.misc import install_asyncio
from wdom.tag import H1
from wdom.document import get_document
from wdom import server

install_asyncio()
loop = asyncio.get_event_loop()
doc = get_document()
server.exclude_patterns.append(r'test.css')
doc.body.appendChild(H1('FIRST', id='h1'))
doc.add_cssfile('testdir/test.css')
server.add_static_path('testdir', '/home/takagi/Projects/wdom/wdom/tests/local_browser/testdir')
server.start_server(loop=loop, check_time=10)
loop.run_forever()