def simple_decorator(decorator):
    """This decorator can be used to turn simple functions
    into well-behaved decorators, so long as the decorators
    are fairly simple. If a decorator expects a function and
    returns a function (no descriptors), and if it doesn't
    modify function attributes or docstring, then it is
    eligible to use this. Simply apply @simple_decorator to
    your decorator and it will automatically preserve the
    docstring and function attributes of functions to which
    it is applied."""
    def new_decorator(f):
        g = decorator(f)
        g.__name__ = f.__name__
        g.__doc__ = f.__doc__
        g.__dict__.update(f.__dict__)
        return g

    # Now a few lines needed to make simple_decorator itself
    # be a well-behaved decorator.
    new_decorator.__name__ = decorator.__name__
    new_decorator.__doc__ = decorator.__doc__
    new_decorator.__dict__.update(decorator.__dict__)
    return new_decorator


@simple_decorator
def bufferize(iterator, with_context='center', context=1):
    def buffered_iterator(*args, **kwargs):

        timestamps = deque([], context)
        things = deque([], context)

        for timestamp, thing in iterator(*args, **kwargs):
            timestamps.append(timestamp)
            things.append(thing)
            if len(timestamps) < context:
                continue

            if with_context is 'center':
                yield timestamps[context / 2], things
            elif with_context is 'left':
                yield timestamp, things
            else:
                yield timestamps[0], things

        return buffered_iterator
