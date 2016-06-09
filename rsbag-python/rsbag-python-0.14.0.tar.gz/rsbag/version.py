__version__ = '0.14.0'
__commit__ = 'gf5e3698'

def getVersion():
    """
    Returns a descriptive string for the version of the RSBag client API.
    """
    return "%s-%s" % (__version__, __commit__)
