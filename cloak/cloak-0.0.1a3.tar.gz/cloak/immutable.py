class ImmutableMeta(type):
    """
    This metaclass sets a _locked attribute on an object after it is
    first instantiated. This is used to initialize, then lock the class
    it is applied to.
    """
    def __call__(cls, *args, **kwargs):
        obj = type.__call__(cls, *args, **kwargs)
        obj._locked = True
        return obj


def with_metaclass(mcls):
    """
    Apply a metaclass in a manner that's compatible with both Python 2 and Python 3.
    :param mcls: The metaclass to apply.
    :type mcls: type
    :return: A decorator closure.
    """
    def decorator(cls):
        body = vars(cls).copy()
        # clean out class body
        body.pop('__dict__', None)
        body.pop('__weakref__', None)
        return mcls(cls.__name__, cls.__bases__, body)
    return decorator


@with_metaclass(ImmutableMeta)
class Immutable(object):
    """
    Any class inheriting from ImmutableSlotted will not allow modification of instance
    attributes after the initialization of the object is completed (i.e. the __init__ call completes).

    This class provides shallow immutability (immutability of the child attributes is not enforced),
    much like a tuple object would. This class does not inherit from tuple, however, so that the occasionally
    awkward/incorrect iterator and element access behaviors are not inherited (though in general, inheriting from
    tuple is another valid approach to shallow immutability).

    The difference between this and Immutable is that the _locked attribute is specified in the __slots__ definition,
    thus this will work correctly with child classes that specify __slots__.
    """

    def __setattr__(self, *args):
        if getattr(self, '_locked', False):
            raise TypeError("Instance is immutable!")
        object.__setattr__(self, *args)

    def __delattr__(self, *args):
        if getattr(self, '_locked', False):
            raise TypeError("Instance is immutable!")
        object.__delattr__(self, *args)

    def __setitem__(self, *args):
        if getattr(self, '_locked', False):
            raise TypeError("Instance is immutable!")
        object.__setitem__(self, *args)

    def __delitem__(self, *args):
        if getattr(self, '_locked', False):
            raise TypeError("Instance is immutable!")
        object.__delitem__(self, *args)


class ImmutableSlotted(object):
    """
    Any class inheriting from ImmutableSlotted will not allow modification of instance
    attributes after the initialization of the object is completed (i.e. the __init__ call completes).

    This class provides shallow immutability (immutability of the child attributes is not enforced),
    much like a tuple object would. This class does not inherit from tuple, however, so that the occasionally
    awkward/incorrect iterator and element access behaviors are not inherited (though in general, inheriting from
    tuple is another valid approach to shallow immutability).

    The difference between this and Immutable is that the _locked attribute is specified in the __slots__ definition,
    thus this will work correctly with child classes that specify __slots__.
    """

    __slots__ = []

    def __setattr__(self, attribute, value):
        if hasattr(self, attribute):
            raise TypeError("Instance is immutable")
        else:
            super(ImmutableSlotted, self).__setattr__(attribute, value)

    def __delattr__(self, *args):
        raise TypeError("Instance is immutable!")

    def __setitem__(self, attribute, value):
        if hasattr(self, attribute):
            raise TypeError("Instance is immutable")
        else:
            super(ImmutableSlotted, self).__setitem__(attribute, value)

    def __delitem__(self, *args):
        raise TypeError("Instance is immutable!")