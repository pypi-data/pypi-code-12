class CachedAttr(object):
    '''Computes attribute value and caches it in instance.

    Example:
        class MyClass(object):
            def myMethod(self):
                # ...
            myMethod = Cached(myMethod)
    Use "del inst.myMethod" to clear cache.
    http://code.activestate.com/recipes/276643/
    '''
    def __init__(self, method, name=None):
        self.method = method
        self.name = name or method.__name__

    def __get__(self, inst, cls):
        if inst is None:
            return self
        result = self.method(inst)
        setattr(inst, self.name, result)
        return result


def resolve_name(name, module_name=None, raise_exc=False):
    '''Given a name string and module prefix, try to import the name.
    '''
    if not isinstance(name, str):
        raise TypeError('Need a stringy name to import.')
    if module_name is None:
        module_name, _, name = name.rpartition('.')
    try:
        module = __import__(module_name, globals(), locals(), [name], 0)
    except ImportError as exc:
        if raise_exc:
            raise exc
    else:
        return getattr(module, name)