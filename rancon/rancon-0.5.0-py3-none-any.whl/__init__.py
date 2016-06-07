"""
Crawl through all available rancher services and look for a label with
the following format:

    rancon.routing: true / on / yes / 1

If a service with this tag is found, it will be published as service
"SERVICE_NAME" in Consul, and the service will get the tag TAG_NAME (if
set).

If "rancon.consul.tag" is not found, the tag "rancher_service" is used.
The tag "rancon" is applied every time.

*All* services created by rancon will be tagged "rancon" in consul, so that
rancon is able to remove services which are no longer available in rancher.

"""

from rancon import settings
from rancon import tools

import sys
from time import sleep, ctime


def route_services():
    backend = settings.backend
    source = settings.source
    routed_services = source.get_services()
    registered_services = []
    for service in routed_services:
        rv = backend.register(service)
        if rv:
            registered_services.append(rv)
        else:
            print("Failed to register service: {}"
                  .format(service))
    backend.cleanup(registered_services)


def start(sys_argv):
    print("RANCON: start @ {}".format(ctime()))
    settings.parse_params(sys_argv)
    route_services()
    while settings.args.continuous:
        sleep(settings.args.wait)
        route_services()
    print("RANCON: Done.")

def console_entrypoint():
    start(sys.argv[1:])
