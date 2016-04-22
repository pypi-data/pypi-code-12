"""
This module helps you to :func:`start()` an agent container in a new
subprocess.  The new container will have a :class:`Manager` agent that allows
the master process to spawn other agents in the new container.

The following example demonstrate how you can build a nice CLI with the `click
<http://click.pocoo.org>`_ around this module. The script will start you
a container with an :class:`~aiomas.clocks.ExternalClock` and the
:class:`~aiomas.codecs.MsgPackBlosc` codec:

.. code-block:: python3

   # container.py
   import logging

   import aiomas
   import arrow
   import click


   def validate_addr(ctx, param, value):
       try:
           host, port = value.rsplit(':', 1)
           return (host, int(port))
       except ValueError as e:
           raise click.BadParameter(e)


   def validate_start_date(ctx, param, value):
       try:
           arrow.get(value)  # Check if the date can be parsed
       except arrow.parser.ParserError as e:
           raise click.BadParameter(e)
       return value

   @click.command()
   @click.option('--start-date', required=True,
                 callback=validate_start_date,
                 help='Start date for the agents (ISO-8601 compliant, e.g.: '
                      '2010-03-27T00:00:00+01:00')
   @click.option('--log-level', '-l', default='info', show_default=True,
                 type=click.Choice(['debug', 'info', 'warning', 'error',
                                    'critical']),
                 help='Log level for the MAS')
   @click.argument('addr', metavar='HOST:PORT', callback=validate_addr)
   def main(addr, start_date, log_level):
       logging.basicConfig(level=getattr(logging, log_level.upper()))
       clock = aiomas.ExternalClock(start_date, init_time=-1)
       codec = aiomas.codecs.MsgPackBlosc
       task = aiomas.subproc.start(addr, clock=clock, codec=codec)
       aiomas.run(until=task)


   if __name__ == '__main__':
       main()

Example usage: :command:`python container.py
--start-date=2010-03-27T00:00:00+01:00 localhost:5556`.

.. note::

   You should use ``sys.executable`` instead of just ``'python'`` when you
   start a new subprocess from within a Python script to make sure you use the
   correct (same) interpreter.

"""
import asyncio
import logging

from . import agent, rpc, util


logger = logging.getLogger(__name__)


@asyncio.coroutine
def start(addr, **container_kwargs):
    """`Coroutine
    <https://docs.python.org/3/library/asyncio-task.html#coroutine>`_ that
    starts a container with a :class:`Manager` agent.

    The agent will connect to *addr* ``('host', port)`` and wait for commands
    to spawn new agents within its container.

    The *container_kwargs* will be passed to
    :meth:`aiomas.agent.Container.create()` factory function.

    This coroutine finishes after :meth:`Manager.stop()` was called or when
    a :exc:`KeyboardInterrupt` is raised.

    """
    container_kwargs.update(as_coro=True)
    container = yield from agent.Container.create(addr, **container_kwargs)
    try:
        manager = Manager(container)
        yield from manager.stop_received
    except KeyboardInterrupt:
        logger.info('Execution interrupted by user')
    finally:
        yield from container.shutdown(as_coro=True)


class Manager(agent.Agent):
    """An agent that can start other agents within its container.

    If the container uses an :class:`~aiomas.clocks.ExternalClock`, it can also
    set the time for the container's clock.

    """
    def __init__(self, container):
        super().__init__(container)
        self.stop_received = asyncio.Future()

    @rpc.expose
    @asyncio.coroutine
    def spawn(self, qualname, *args, **kwargs):
        """Create a new instance of an agent and return a proxy to it and its
        address.

        *qualname* is a string defining a class (or factory method/coroutine)
        for instantiating the agent (see :func:`aiomas.util.obj_from_str()` for
        details).  *args* and *kwargs* get passed to this callable as
        positional and keyword arguemnts respectively.

        This is an exposed `coroutine
        <https://docs.python.org/3/library/asyncio-task.html#coroutine>`_.

        """

        callable = util.obj_from_str(qualname)
        if asyncio.iscoroutinefunction(callable):
            agent = yield from callable(self.container, *args, **kwargs)
        else:
            agent = callable(self.container, *args, **kwargs)

        logger.debug('Spawned %s(%s)' % (agent.__class__.__name__, agent))

        return agent, agent.addr

    @rpc.expose
    def set_time(self, time):
        """Set the agent's container's time to *time*.

        This only works if the container uses an
        :class:`~aiomas.clocks.ExternalClock`.

        This is an exposed function.

        """
        self.container.clock.set_time(time)

    @rpc.expose
    def stop(self):
        """Triggers the *stop_received* future of this agent causing its
        container process to shutodwn and terminate.

        This is an exposed function.

        """
        self.stop_received.set_result(True)
