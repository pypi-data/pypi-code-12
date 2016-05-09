from .datadog_backend import Datadog as datadog

KNOWN_MODULES = {
    'datadog': datadog,
}

def get_backend(backend_name):

    try:
        return KNOWN_MODULES[backend_name]
    except KeyError:
        raise NotImplementedError("backend %s is not supported" % backend_name)
