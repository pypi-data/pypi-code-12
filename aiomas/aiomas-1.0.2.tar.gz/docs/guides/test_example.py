import pytest
import aiomas

#
# Production code (exampleagent.py)
#


class ExampleAgent(aiomas.Agent):
    async def run(self, target_addr, num):
        remote_agent = await self.container.connect(target_addr)
        return (await remote_agent.service(num))

    @aiomas.expose
    async def service(self, val):
        await self.container.clock.sleep(0.001)
        return val


#
# Testing code (test_exampleagent.py)
#


@pytest.yield_fixture
def container(event_loop, unused_tcp_port):
    """This fixture creates a new Container instance for every test and binds
    it to a random port.

    It requires the *event_loop" fixture, so every test will also have a fresh
    event loop.

    """
    # Create container and bind its server socket to a random port:
    c = aiomas.Container.create(('127.0.0.1', unused_tcp_port))

    # Yield the container to the test case:
    yield c

    # Clean-up that is run after the test finished:
    c.shutdown()

    # The "event_loop" fixture closes the event loop after the test, but we
    # need an existing event loop for the following tests, so start a new one:
    import asyncio
    asyncio.set_event_loop(asyncio.new_event_loop())


# The "@pytest.mark.asyncio" decorator allows you do use "await"/"yield from"
# directly within your test case.
#
# The "container" argument tells pytest to pass the return/yield value of the
# corresponding fixture to your test.
@pytest.mark.asyncio
async def test_example_agent(container):
    num = 42
    # Start two agents:
    agents = [ExampleAgent(container) for _ in range(2)]
    # Run the 1st one and let it connect to the 2nd one.  Check the return
    # value of the 1st one's run() task:
    res = await agents[0].run(agents[1].addr, num)
    assert res == num
