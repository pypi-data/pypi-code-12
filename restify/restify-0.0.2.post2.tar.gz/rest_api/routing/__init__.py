import glob, importlib, malibu, os
from importlib import import_module
from malibu.util import decorators, log

from rest_api.routing import base

modules = glob.glob(os.path.dirname(__file__) + "/*.py")
__all__ = [os.path.basename(f)[:-3] for f in modules if not os.path.basename(f).startswith('_') and not f.endswith('__init__.py') and os.path.isfile(f)]


__ROUTING_MODULES__ = []
routing_module = decorators.function_registrator(__ROUTING_MODULES__)

def load_routing_modules(manager, package = None):

    package = __package__ if not package else package
    package_all = import_module(package)
    if not hasattr(package_all, "__all__"):
        logger.error("Package %s has no __all__ attribute!" % (package))
        return []

    package_all = package_all.__all__

    providers = []

    logger = log.LoggingDriver.find_logger()

    logger.debug("Searching %s for routing providers.." % (package))

    for module in package_all:
        module = import_module("{}.{}".format(package, module))
        if not hasattr(module, "register_route_providers"):
            continue
        for rtcls in module.register_route_providers:
            if not issubclass(rtcls, base.APIRouter):
                continue
            logger.debug("Found provider %s in module %s" % (
                rtcls.__name__, module.__name__))
            providers.append(rtcls)

    # Note that these modules are classes registered via @routing_module.
    for module in __ROUTING_MODULES__:
        if not issubclass(module, base.APIRouter):
            continue
        logger.debug("Provider %s registered with decorator from %s" % (
            module.__name__, module.__module__))
        providers.append(module)

    return [provider(manager) for provider in providers]

