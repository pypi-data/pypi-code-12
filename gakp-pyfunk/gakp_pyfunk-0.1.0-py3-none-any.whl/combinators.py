from functools import reduce


def curry(f):
    '''
    Returns the curried equivalent of the given function.
    @sig curry :: * -> b -> * -> b
    '''
    def curried(*args):
        if len(args) == f.__code__.co_argcount:
            return f(*args)
        return lambda *args2: curried(*(args + args2))
    return curried


def compose(*fns):
    '''
    Performs right-to-left function composition. The rightmost function may have
    any arity, the remaining functions must be unary.
    @sig compose :: (b -> c)...(* -> b) -> (* -> c)
    '''
    return reduce(lambda f, g:
                  lambda *args: f(g(*args)), fns)


def fnot(f):
    '''
    Creates a function that negates the result of the predicate.
    @sig fnot :: (a -> Bool) -> * -> Bool
    '''
    return lambda *args: not f(*args)
