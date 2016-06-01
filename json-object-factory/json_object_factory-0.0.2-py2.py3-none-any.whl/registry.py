import types


class FactoryWrapper(object):
    def __init__(self, obj, mode=None, obj_id=None,
                 encode_func=None, decode_func=None):
        self.factory_obj = obj
        if encode_func is None:
            encode_func = getattr(obj, 'default', getattr(obj, 'encode', None))
        if decode_func is None:
            decode_func = getattr(obj, 'object_hook', getattr(obj, 'decode', None))
        self.encode_func = encode_func
        self.decode_func = decode_func
        self.mode = mode
        if obj_id is None:
            obj_id = id(obj)
        self.id = obj_id
    def encode(self, o):
        if self.mode == 'encode':
            return self.factory_obj(o)
        elif self.mode != 'decode' and self.encode_func is not None:
            return self.encode_func(o)
    def decode(self, d):
        if self.mode == 'decode':
            return self.factory_obj(d)
        elif self.mode != 'encode' and self.decode_func is not None:
            return self.decode_func(d)
        return d
    def __repr__(self):
        return 'Wrapper for %r' % (self.factory_obj)


class Registry_(object):
    def __init__(self):
        self.objects = {}
    def register(self, obj, mode=None):
        if not isinstance(obj, FactoryWrapper):
            obj = _build_wrapper(obj, mode)
        self.objects[obj.id] = obj
    def unregister(self, obj):
        obj_id = id(obj)
        if obj_id not in self.objects:
            return
        del self.objects[obj_id]
    def encode(self, o):
        for w in self.objects.values():
            r = w.encode(o)
            if r is not None:
                return r
    def decode(self, d):
        for w in self.objects.values():
            d = w.decode(d)
            if not isinstance(d, dict):
                return d
        return d

Registry = Registry_()

def _build_wrapper(obj, mode):
    inst = None
    if isinstance(obj, types.FunctionType):
        f = obj
        wrapper = None
        w = FactoryWrapper(f, mode=mode)
    elif isinstance(obj, type):
        inst = obj()
        wrapper = None
        w = FactoryWrapper(inst, mode=mode, obj_id=id(obj))
    elif isinstance(obj.__class__, type):
        inst = obj
        wrapper = None
        w = FactoryWrapper(obj, mode=mode)
    return w
