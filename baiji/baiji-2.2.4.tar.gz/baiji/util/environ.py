def getenvpath(env_var, default=None):
    '''
    A version of os.getenv that handles paths a bit better
    '''
    import os
    path = os.getenv(env_var, default)
    return os.path.realpath(os.path.expanduser(path))
