from functools import reduce, wraps


class Pipeline(object):

    """Pipeline(pipeline)

    Resulting object can be called with an iterable. Every function in pipeline will
    be applied in order to every element of the iterable.
    Ex.
    pipe=Pipeline([L(lambda x: x*2), L(lambda x: x+1)])
    results=pipe(range(10))

    Note the helper function L. You could also create generators that yield
    transformed data one by one and use them directly:

    def double(datastream):
        for d in datastream:
            yield 2*datastream

    Pipeline also allows the shorthand

    results=Pipeline([double, L(lambda x: x+1)], range(10))

    :pipeline: list of functions
    :data: list of data to pipe through the line
    """

    def __new__(cls, pipeline=None, data=None):
        if data is not None:
            return cls(pipeline)(data)
        return super().__new__(cls)

    def __init__(self, pipeline=None):
        self.pipeline = pipeline if pipeline is not None else []

    def __call__(self, initial_data):
        yield from reduce(lambda x, y: y(x), self.pipeline, initial_data)

    def __len__(self):
        return len(self.pipeline)

    def __add__(self, other):
        try:
            return type(self)(self.pipeline + other.pipeline)
        except AttributeError:
            return type(self)(self.pipeline + other)
    __radd__ = __add__
    __or__ = __add__
    __ror__ = __or__

    def __iadd__(self, other):
        try:
            self.pipeline += other.pipeline
        except AttributeError:
            self.pipeline += other
        return self
    __ior__ = __iadd__

    def __mul__(self, other):
        return type(self)(self.pipeline * other)
    __rmul__ = __mul__

    def __imul__(self, other):
        self.pipeline *= other
        return self

    def __getitem__(self, index):
        return type(self)(self.pipeline[index])


def L(func):
    """L(func)


    Returns a generator like the original function, but that can act on a list of inputs,
    instead of just one.

    Ex.
    @L
    def double(n):
        return n*2
    for i in double([1,2,3,4]):
        print(i)

    This is meant to be used as a helper function for Pipeline if you want to use
    simple lambda functions, or integrate existing functions that operate on
    individual items.

    When decorating recursive functions, care has to be taken to call the original
    function in __wrapped__.

    :func: function to modify
    :returns: vectorised function as generator
    """
    @wraps(func)
    def wrapped(x):
        for i in x:
            yield func(i)
    return wrapped
