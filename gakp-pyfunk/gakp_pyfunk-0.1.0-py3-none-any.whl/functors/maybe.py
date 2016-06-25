from pyfunk.combinators import curry, compose


class Maybe(object):

    def __init__(self, x):
        '''
        Create new Maybe Monad
        @sig a -> Maybe a
        '''
        self._value = x

    @classmethod
    def of(cls, x):
        '''
        Factory for creating new Maybe monad
        @sig of :: a -> Maybe a
        '''
        return cls(x)

    @staticmethod
    @curry
    def maybe(x, fn, mb):
        '''
        Extract a Maybe's value providing a default if Nothing
        @sig maybe :: b -> (a -> b) -> Maybe a -> b
        '''
        return x if mb.nothing() else fn(mb._value)

    @staticmethod
    @curry
    def maybify(nullify, f):
        '''
        Creates a function that returns Maybe. Also accepts a Nonifier
        that checks that transforms falsy value to None. One can use
        misc.F if there is no need to nonify.
        @sig maybify :: (a -> Bool) -> (a -> b) -> (a -> Maybe b)
        '''
        return compose(lambda a: Maybe.of(None if nullify(a) else a), f)

    def nothing(self):
        '''
        Checks if the value of this Maybe is None.
        @sig nothing :: Maybe a => _ -> Bool
        '''
        return self._value is None

    def fmap(self, fn):
        '''
        Transforms the value of the Maybe monad using the given function
        @sig map :: Maybe a => (a -> b) -> Maybe b
        '''
        return Maybe.of(None) if self.nothing() \
            else Maybe.of(fn(self._value))

    def join(self):
        '''
        Lifts an Maybe monad out of another
        @sig join :: Maybe i => i (i a) -> c a
        '''
        return Maybe.of(None) if self.nothing() \
            else self._value

    def chain(self, fn):
        '''
        Transforms the value of the Maybe monad using a function to a monad
        @sig chain :: Maybe a -> (a -> Maybe b) -> Maybe b
        '''
        return self.fmap(fn).join()
