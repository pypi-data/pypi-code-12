from pyfunk.combinators import compose


class IO(object):

    def __init__(self, fn):
        '''
        Create new IO Monad
        @sig a -> IO a
        '''
        self.unsafeIO = fn

    @classmethod
    def of(cls, x):
        '''
        Factory for creating new IO monad
        @sig of :: a -> IO a
        '''
        return cls(lambda: x)

    def fmap(self, fn):
        '''
        Transforms the value of the IO monad using the given function
        @sig map :: IO a => (a -> b) -> IO b
        '''
        return IO(compose(fn, self.unsafeIO))

    def join(self):
        '''
        Lifts an IO monad out of another
        @sig join :: IO i => i (i a) -> c a
        '''
        return IO(lambda: self.unsafeIO().unsafeIO())

    def chain(self, fn):
        '''
        Transforms the value of the IO monad using a function to a monad
        @sig chain :: IO a -> (a -> IO b) -> IO b
        '''
        return self.fmap(fn).join()
