# Collections
class ImmutableDict(dict):
    def __setitem__(self, key, value):
        raise ForbiddenSetItem('__setitem__ method is forbidden for ImmutableDict objects')
    def __setattr__(self, attr, value):
        raise ForbiddenSetAttr('__setattr__ method is forbidden for ImmutableDict objects')
    def __getattr__(self, item):
        try:
            return self.__getitem__(item)
        except KeyError:
            raise AttributeError(item)

class LockableDict(dict):
    is_locked = False

    def __setitem__(self, key, value):
        if self.is_locked == False:
            return dict.__setitem__(self, key, value)
        else:
            raise DictIsLocked("'__setitem__' method is forbidden " \
                "for type '{}' while the value of the instance attribute " \
                "'is_locked' is False".format(self.__class__.__name__))

    def __setattr__(self, attr, value):
        if attr == 'is_locked':
            return dict.__setattr__(self, attr, value)
        elif self.is_locked == False:
            return dict.__setitem__(self, attr, value)
        else:
            raise DictIsLocked("'__setattr__' method is forbidden " \
                "for type '{}' while the value of the instance attribute " \
                "'is_locked' is False".format(self.__class__.__name__))

    def __getattr__(self, attr):
        if attr == 'is_locked':
            return dict.__getattr__(self, attr)
        else:
            return dict.__getitem__(self, attr)

# Exceptions
class ForbiddenSetItem(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)

class ForbiddenSetAttr(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)

class DictIsLocked(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)
