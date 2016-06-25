from pyfunk.combinators import compose


class Task(object):

    def __init__(self, fn):
        '''
        Create new Container
        @sig a -> Task a b
        '''
        self.fork = fn

    @classmethod
    def of(cls, x):
        '''
        Factory for creating new resolved task
        @sig of :: b -> Task _ b
        '''
        return Task(lambda _, resolve: resolve(x))

    @classmethod
    def rejected(cls, x):
        '''
        Factory for creating a rejected task
        @sig rejected :: a -> Task a _
        '''
        return Task(lambda reject, _: reject(x))

    def fmap(self, fn):
        '''
        Transforms the resolved value of the task using the given function
        @sig map :: Task a b => (b -> c) -> Task a c
        '''
        return Task(lambda rej, res: self.fork(rej, compose(res, fn)))

    def join(self):
        '''
        Lifts a Task out of another
        @sig join :: Task a b => Task a Task b c -> Task a c
        '''
        return Task(lambda rej, res: self.fork(rej,
                    lambda x: x.fork(rej, res)))

    def chain(self, fn):
        '''
        Transforms the resolved value of the Task using a function to a monad
        @sig chain :: Task a -> (a -> Container b) -> Container b
        '''
        return self.fmap(fn).join()

    def or_else(self, fn):
        '''
        Helps the use of making task even when dealing with rcover
        @sig or_else :: Task [a b] => (a -> Task [c b]) -> Task [c b]
        '''
        return Task(lambda rej, res: self.fork(
                    lambda x: x.fork(rej, res), res))
