__author__ = 'warior'
__date__ = '01.06.16'


class Dict(dict):
    def __init__(self, *args, parent=None, mkey=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._parent = parent
        self._key = mkey

    def __missing__(self, key):
        value = self[key] = type(self)(parent=self, mkey=key)
        return value

    def append(self, elem):
        self._parent[self._key] = [elem]

    def extend(self, elem):
        self._parent[self._key] = elem

    def __delitem__(self, key):
        super().__delitem__(key)
        if len(self) == 0 and self._parent:
            del self._parent[self._key]

    def __setitem__(self, key, value):
        if isinstance(value, self.__class__) or value not in (None, "", {}, []):
            super().__setitem__(key, value)

    def __iadd__(self, other):
        value = self._parent[self._key] = other
        return value

    def __isub__(self, other):
        value = self._parent[self._key] = other
        return value

    def __imul__(self, other):
        value = self._parent[self._key] = other
        return value

    def __ifloordiv__(self, other):
        value = self._parent[self._key] = other
        return value

    def __idiv__(self, other):
        value = self._parent[self._key] = other
        return value

    def __imod__(self, other):
        value = self._parent[self._key] = other
        return value

    def __ipow__(self, other):
        value = self._parent[self._key] = other
        return value

    def __ilshift__(self, other):
        value = self._parent[self._key] = other
        return value

    def __irshift__(self, other):
        value = self._parent[self._key] = other
        return value

    def __iand__(self, other):
        value = self._parent[self._key] = other
        return value

    def __ior__(self, other):
        value = self._parent[self._key] = other
        return value

    def __ixor__(self, other):
        value = self._parent[self._key] = other
        return value
