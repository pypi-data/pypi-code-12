import bottle
import copy


def ctx_push(ctx):
    '''
    Push a new cotext dict to the current request context stack.
    '''
    try:
        bottle.request.ws_context.append(ctx)
    except AttributeError:
        bottle.request.ws_context = [ctx]


def ctx_pop():
    '''
    Pop a context dict from the current requests context stack.
    '''
    try:
        return bottle.request.ws_context.pop()
    except (AttributeError, IndexError):
        pass


def ctx_get():
    '''
    Get the top of the context stack without removing it.
    '''
    try:
        return bottle.request.ws_context[-1]
    except (AttributeError, IndexError):
        pass


def ctx_copy():
    '''
    Copy the current context stack
    '''
    try:
        return copy.deepcopy(bottle.request.ws_context)
    except AttributeError:
        pass


class Context(object):
    def __init__(self, **ctx):
        self.ctx = ctx

    def __enter__(self):
        ctx_push(self.ctx)

    def __exit__(self, *_):
        ctx_pop()
