from pyfunk.collections import fmap
from pyfunk.combinators import compose, curry


def join(m):
    '''
    Unbound version of join
    @sig join :: Monad m => m (m a) -> m a
    '''
    return m.join()


@curry
def chain(fn, m):
    '''
    Unbound version of chain
    @sig chain :: Monad m => (a -> m b) -> m a -> m b
    '''
    return m.chain(fn)


def mcompose(*fns):
    '''
    Composes functions that produce monads
    @sig mcompose :: Monad m => ((b -> m c), (a -> m b)) -> (a -> m c)
    '''
    first = fns[-1:]
    rest = fmap(fns[:-1], chain)
    return compose(*(rest + (first,)))
