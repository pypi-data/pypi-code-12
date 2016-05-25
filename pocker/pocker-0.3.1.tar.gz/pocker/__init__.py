from .pocker import Docker

def version():
    from .version import __version__
    return __version__
