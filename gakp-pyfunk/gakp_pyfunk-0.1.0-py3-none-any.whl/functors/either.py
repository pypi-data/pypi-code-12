from pyfunk.functors.container import Container
from pyfunk.combinators import curry


class Either(object):

    @staticmethod
    @curry
    def either(f, g, e):
        '''
        Extracts the values from either for transformation there f is for
        Left and g for Right
        @sig either :: Either a b => (a -> c) -> (b -> c) -> Either a b -> c
        '''
        if isinstance(e, Left):
            return f(e._value)
        elif isinstance(e, Right):
            return g(e._value)


class Left(object):

    def __init__(self, x):
        '''
        Create new Left monad
        @sig a -> Left
        '''
        self._value = x

    @classmethod
    def of(cls, x):
        '''
        Factory for creating new Left monad
        @sig of :: a -> Left
        '''
        return cls(x)

    def fmap(self, fn):
        '''
        Does nothing
        @sig map :: Left => (a -> b) -> Left
        '''
        return self

    def join(self):
        '''
        Lifts a Left monad out of another
        @sig join :: Left l => _ -> Left
        '''
        return self

    def chain(self, fn):
        '''
        Does the same as join
        @sig chain :: Left -> (a -> Left) -> Left
        '''
        return self.fmap(fn).join()


Right = Container
