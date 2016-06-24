# external imports
import asyncio
import consul
from nautilus.auth import random_string
from concurrent.futures import CancelledError

def get_services():
    ''' Return a list of the active services. '''
    return consul_session.agent.services()


def service_location_by_name(key):
    ''' Return the service entry matching the given key '''
    # grab the registry of services
    # todo: go through service proxy service for more efficient loadbalancing
    services = ["localhost:{}".format(service['Port']) \
                                for service in get_services().values() \
                                                if service['Service'] == key]
    # return a random entry from the possibilities
    return random.choice(services)



class RegisterMixin:
    """
        This service mixin adds the necessary functionalities to
        interact with a central service register including regiration,
        registration, and keep-alives.
    """

    ttl = 10
    register_timer = 5


    def __init__(self, *args, **kwds):
        # bubble up first
        super().__init__(*args, **kwds)
        # create a consul agent
        self.consul = consul.Consul()
        # the name of service on the registry
        self._consul_name = None


    def run(self, *args, **kwds):
        # start running the keep alive loop
        self.keep_alive = self.loop.create_task(self._keep_alive)
        # bubble up (blocking)
        super().run(*args, **kwds)


    def cleanup(self, *args, **kwds):
        # bubble up
        super().cleanup(*args, **kwds)
        # cancel the keep_alive loop
        self.keep_alive.cancel()


    async def _keep_alive(self):
        """
            This function registers with the centralized service registry.
        """
        # register the service with consul
        self._register()

        # we could cancel at any time
        try:
            # continuously
            while True:
                # tell the agent that we are passing the ttl check
                consul_session.agent.check.ttl_pass(self.consul_name, 'Agent alive and reachable.')
                # wait 5 seconds before running again
                asyncio.sleep(self.register_timer)

        # if we cancelled this coroutine
        except CancelledError:
            # cleanup
            self._deregister()


    def _register(self):
        """
            This function regsiters the service with the
        """

        # compute and save the consul identifier for the service
        self.consul_name = "{}-{}".format(self.name, random_string(6))\
                                     .replace('_', '-')

        # the consul service entry
        consul_session.agent.service.register(
            name=self.name,
            service_id=self.consul_name,
            port=self.config.port
        )

        # add a ttl check for self in case we die
        consul_session.agent.check.register(
            name=self.consul_name,
            check=consul.Check.ttl(str(self.ttl) + 's'),
        )


    def _deregister(self):
        """
            This method deregisters the service with the registry.
        """
        # if this service has been successfully regsitered with consul
        if self.consul_name:
            # deregister it
            consul_session.agent.service.deregister(self.consul_name)
            consul_session.agent.check.deregister(self.consul_name)
