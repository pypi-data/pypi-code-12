

import asyncio



class PeriodicTask:

    def __init__(self, loop, interval, callback):
        self._loop = loop if loop else asyncio.get_event_loop()
        self._interval = interval
        self._callback = callback
        self._num_executed = 0
        self._running = False
        self._tasks = []

    @asyncio.coroutine
    def wrapped(self):
        yield from self._callback()
        self._num_executed += 1
        if self._running:
            yield from asyncio.sleep(self._interval)
            self._tasks.append(asyncio.ensure_future(self.wrapped()))

    @asyncio.coroutine
    def start(self):
        self._running = True
        self._tasks.append(asyncio.ensure_future(self.wrapped()))

    @asyncio.coroutine
    def stop(self):
        self._running = False
        tasks = asyncio.gather(*self._tasks)
        tasks.cancel()

    @property
    def num_executed(self):
        return self._num_executed

@asyncio.coroutine
def test():
    print('wtf!')

@asyncio.coroutine
def run_test():
    p = PeriodicTask(loop=None, interval=1, callback=test)
    yield from p.start()
    yield from asyncio.sleep(3)
    yield from p.stop()
    print(p.num_executed)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test())
    loop.close()


if __name__ == '__main__':
    main()
