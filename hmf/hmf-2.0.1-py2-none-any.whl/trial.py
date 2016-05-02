
from functools import update_wrapper


def cached_property(f, *children):
    name = f.__name__

    prop_ext = '__%s' % name

    def _get_property(self):
        prop = "_" + self.__class__.__name__ + prop_ext
        try:
            value = getattr(self, prop)
        except AttributeError:
            value = f(self)
            setattr(self, prop, value)

        return value

    update_wrapper(_get_property, f)

    def _del_property(self):
        try:
            delattr(self, "_" + self.__class__.__name__ + prop_ext)
        except AttributeError:
            pass

        for child in children:
            delattr(self, child)

    return property(_get_property, None, _del_property)


class A(object):

    def __init__(self, a):
        self.a = a

    @cached_property
    def amethod(self):
        return 3 * self.a


class B(A):

    def amethod(self):
        return super(B, self).amethod()


if __name__ == "__main__":
    ins = A(4)
    print ins.amethod
