from woodstove import log
from woodstove import exceptions

__setup__ = False
__handlers__ = {}


def register_handler(extype, handler):
    __handlers__[extype] = handler


def generic_handler(code, message=None, log_msg=None, callback=None):
    def handler(req):
        req.ret = message if message else req.exception.message
        lmsg = log_msg if log_msg else "%s: %s" % (req.exception.__class__.__name__,
                req.exception.message)
        log.get_logger(__name__).error(lmsg)
        req.response.status = code

        if callback is not None:
            callback(req)

    return handler


def run_handler(req):
    if not __setup__:
        exc_setup()

    handler = __handlers__.get(req.exception.__class__, default_handler)
    return handler(req)


default_handler = generic_handler(500, 'Internal Error',
                                  callback=lambda r: log.log_traceback(__name__))


def exc_setup():
    global __setup__
    __setup__ = True
    register_handler(exceptions.ArgumentException,
                     generic_handler(400))
    register_handler(exceptions.AuthException,
                     generic_handler(401, "Not Authorized"))
    register_handler(exceptions.NotFoundException,
                     generic_handler(404, 'Not found'))
    register_handler(exceptions.RequestException,
                     generic_handler(400))
    register_handler(exceptions.InternalException,
                     generic_handler(500, 'Internal Error'))
