''' CORS plugin '''
from woodstove import hooks


def cors_route(*args, **kwargs):
    ''' '''
    return


@hooks.hook('route', 'setup')
def cors_setup_hook(robj):
    ''' '''


@hooks.hook('route', 'exit')
def cors_exit_hook(req):
    ''' '''
    req.response.headers['Access-Control-Allow-Origin'] = '*'
    #req.response.headers['Access-Control-Allow-Methods'] = conf.methods
    #req.response.headers['Access-Control-Allow-Headers'] = conf.headers
