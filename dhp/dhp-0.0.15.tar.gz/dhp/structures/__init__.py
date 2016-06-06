'''dhp data structures'''


class DictDot(dict):
    """A subclass of Python's dictionary that provides dot-style access.

    Nested dictionaries are recursively converted to DictDot.  There are a
    number of similar libraries on PyPI.  However, I feel this one does just
    enough to make things work as expected without trying to do too much.

    Example::

        dicdot = DictDot({
            'foo': {
                'bar': {
                    'baz': 'hovercraft',
                    'x': 'eels'
                }
            }
        })
        assert dicdot.foo.bar.baz == 'hovercraft'
        assert dicdot['foo'].bar.x == 'eels'
        assert dicdot.foo['bar'].baz == 'hovercraft'
        dicdot.bouncy = 'bouncy'
        assert dictdot['bouncy'] == 'bouncy'

    DictDot raises an AttributeError when you try to read a non-existing
    attribute while also allowing you to create new key/value pairs using
    dot notation.

    DictDot also supports keyword arguments on instantiation and is built to
    be subclass'able.
    """
    def __init__(self, *args, **kwargs):
        if args:
            dct = args[0]
        else:
            dct = {}
        if kwargs:
            dct.update(kwargs)
        for key in dct:
            if isinstance(dct[key], dict):
                dct[key] = self.__class__(dct[key])
        super(DictDot, self).__init__(dct)

    def __getattr__(self, key):
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            try:
                return self[key]
            except KeyError:
                raise AttributeError(key)

    def __setattr__(self, key, val):
        if isinstance(val, dict):
            val = self.__class__(val)
        try:
            object.__getattribute__(self, key)
        except AttributeError:
            # try:
            self[key] = val
            # except:
            #     raise AttributeError(key)
        # else:
        #     object.__setattr__(self, key, val)

    def __delattr__(self, key):
        try:
            object.__getattribute__(self, key)
        except AttributeError:
            try:
                del self[key]
            except KeyError:
                raise AttributeError(key)
        # else:
        #     object.__delattr__(self, key)


class ComparableMixin(object):      # pylint:disable=r0903
    """Mixin to give proper comparisons.

    Example::

        class Comparable(ComparableMixin):
            def __init__(self, value):
                self.value = value

            def _cmpkey(self):
                return self.value

    Returns NotImplemented if the object being compared doesn't support the
    comparison.

    Raises NotImplementedError if you have not overridden the _cmpkey method.

    Code is from Lennart Regebro
    https://regebro.wordpress.com/2010/12/13/python-implementing-rich-comparison-the-correct-way/

 """
    def _cmpkey(self):
        """return the key to be used for the _compare"""
        raise NotImplementedError

    def _compare(self, other, method):
        """compare this object to another using method"""
        try:
            # pylint:disable=w0212
            return method(self._cmpkey(), other._cmpkey())
        except (AttributeError, TypeError):
            # _cmpkey not implemented, or return different type,
            # so we can't compare with "other".
            return NotImplemented

    def __lt__(self, other):
        return self._compare(other, lambda slf, oth: slf < oth)

    def __le__(self, other):
        return self._compare(other, lambda slf, oth: slf <= oth)

    def __eq__(self, other):
        return self._compare(other, lambda slf, oth: slf == oth)

    def __ge__(self, other):
        return self._compare(other, lambda slf, oth: slf >= oth)

    def __gt__(self, other):
        return self._compare(other, lambda slf, oth: slf > oth)

    def __ne__(self, other):
        return self._compare(other, lambda slf, oth: slf != oth)
