class Container(object):

    def __init__(self, x):
        '''
        Create new Container
        @sig a -> Container a
        '''
        self._value = x

    @classmethod
    def of(cls, x):
        '''
        Factory for creating new container
        @sig of :: a -> Container a
        '''
        return cls(x)

    def fmap(self, fn):
        '''
        Transforms the value of the container using the given function
        @sig map :: Container a => (a -> b) -> Container b
        '''
        return self.of(fn(self._value))

    def join(self):
        '''
        Lifts a container out of another
        @sig join :: Container c => c (c a) -> c a
        '''
        return self._value

    def chain(self, fn):
        '''
        Transforms the value of the container using a function to a monad
        @sig chain :: Container a -> (a -> Container b) -> Container b
        '''
        return self.fmap(fn).join()
