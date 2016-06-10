import time
from woodstove import hooks, log

@hooks.hook('route', 'exit')
def duration_exit_hook(req):
    ''' Log request duration '''
    log.get_logger(__name__).debug("Request handled in %f seconds",
                                   time.time()-req.start)
