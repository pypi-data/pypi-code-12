import asyncio
import shlex

import tsuru_router_tailer.dealer as dealer
import tsuru_router_tailer.sender as sender


class Runner(object):
    def __init__(self, log_path, logstash):
        self.log_path = log_path
        dealer.sender = sender.Sender(logstash)

    def run(self):
        loop = asyncio.get_event_loop()

        @asyncio.coroutine
        def setup():
            transport, protocol = yield from loop.subprocess_shell(
                dealer.Dealer,
                'tail -n0 -F -q {}'.format(shlex.quote(self.log_path)),
            )
            yield from protocol.complete

        loop.run_until_complete(setup())
