__version__ = '0.13.1'
__commit__ = 'g10568ea'

def getVersion():
    """
    Returns a descriptive string for the version of the RSBag client API.
    """
    return "%s-%s" % (__version__, __commit__)
