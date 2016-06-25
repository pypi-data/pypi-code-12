# external imports
import threading
import time
import random
import consul
import asyncio

# create a consul session
consul_session = consul.Consul()


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

