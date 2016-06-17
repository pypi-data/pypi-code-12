
import sys
import types
from importlib import import_module
import marshal
import pickle

PY3 = sys.version_info[0] >= 3

if PY3:
    def get_func_closure(f): return f.__closure__
    # (code, globals[, name[, argdefs[, closure]]])
    def get_func_tuple(f):
        return (
            f.__code__,
            f.__globals__,
            f.__name__,
            f.__defaults__,
            f.__closure__,
        )
else:
    def get_func_closure(f): return f.func_closure
    def get_func_tuple(f):
        return (
            f.func_code,
            f.func_globals,
            f.func_name,
            f.func_defaults,
            f.func_closure,
        )


Unpickler = pickle.Unpickler
_closure = (lambda x: lambda: x)(0)
# noinspection PyUnresolvedReferences
_cell = get_func_closure(_closure)[0]
CellType = type(_cell)
ModuleType = type(sys)
# noinspection PyUnresolvedReferences
DictType = dict if PY3 else types.DictionaryType


if PY3:
    class BufferType: "Dummy"
    def make_buffer(*args): assert False
else:
    # noinspection PyUnresolvedReferences
    make_buffer = buffer
    # noinspection PyUnresolvedReferences
    BufferType = types.BufferType
    def bytes(x, *args): return str(x)


if PY3:
    _old_style_class = None
    class OldStyleClass: "Dummy"
    class _new_style_class: pass
    NewStyleClass = type
else:
    class _old_style_class: pass
    class _new_style_class(object): pass
    OldStyleClass = type(_old_style_class)  # == types.ClassType (classobj)
    NewStyleClass = type(_new_style_class)  # (type)


try:
    import numpy
    numpy_ndarray = numpy.ndarray
except ImportError:
    numpy = None
    class numpy_ndarray: "Dummy"


def makeFuncCell(value):
    return get_func_closure((lambda: value))[0]


def getModuleDict(modname):
    mod = import_module(modname)
    return mod.__dict__


def getModNameForModDict(obj):
    """
    :type obj: dict
    :rtype: str | None
    :returns The module name or None. It will not return '__main__' in any case
    because that likely will not be the same in the unpickling environment.
    """
    mods = {id(mod.__dict__): modname for (modname, mod) in sys.modules.items() if mod and modname != "__main__"}
    modname = mods.get(id(obj), None)
    return modname


def getNormalDict(d):
    """
    :type d: dict[str] | dictproxy
    :rtype: dict[str]
    It also removes getset_descriptor. New-style classes have those.
    """
    r = {}
    for k, v in d.items():
        if isinstance(v, types.GetSetDescriptorType): continue
        r[k] = v
    return r


def make_numpy_ndarray_fromstring(s, dtype, shape):
    import numpy
    return numpy.fromstring(s, dtype=dtype).reshape(shape)


_BasePickler = getattr(pickle, "_Pickler", pickle.Pickler)

class Pickler(_BasePickler):
    """
    We extend the standard Pickler to be able to pickle some more types,
    such as lambdas and functions, code, func cells, buffer and more.
    """

    def __init__(self, *args, **kwargs):
        if not "protocol" in kwargs:
            kwargs["protocol"] = pickle.HIGHEST_PROTOCOL
        _BasePickler.__init__(self, *args, **kwargs)
    dispatch = _BasePickler.dispatch.copy()

    def save_func(self, obj):
        try:
            self.save_global(obj)
            return
        except pickle.PicklingError:
            pass
        assert type(obj) is types.FunctionType
        self.save(types.FunctionType)
        self.save(get_func_tuple(obj))
        self.write(pickle.REDUCE)
        if id(obj) not in self.memo:  # Could be if we recursively landed here. See also pickle.save_tuple().
            self.memoize(obj)
    dispatch[types.FunctionType] = save_func

    def save_method(self, obj):
        try:
            self.save_global(obj)
            return
        except pickle.PicklingError:
            pass
        assert type(obj) is types.MethodType
        self.save(types.MethodType)
        self.save((obj.im_func, obj.im_self, obj.im_class))
        self.write(pickle.REDUCE)
        self.memoize(obj)
    dispatch[types.MethodType] = save_method

    def save_code(self, obj):
        assert type(obj) is types.CodeType
        self.save(marshal.loads)
        self.save((marshal.dumps(obj),))
        self.write(pickle.REDUCE)
        self.memoize(obj)
    dispatch[types.CodeType] = save_code

    def save_cell(self, obj):
        assert type(obj) is CellType
        self.save(makeFuncCell)
        self.save((obj.cell_contents,))
        self.write(pickle.REDUCE)
        self.memoize(obj)
    dispatch[CellType] = save_cell

    # We also search for module dicts and reference them.
    # This is for FunctionType.func_globals.
    def intellisave_dict(self, obj):
        modname = getModNameForModDict(obj)
        if modname:
            self.save(getModuleDict)
            self.save((modname,))
            self.write(pickle.REDUCE)
            self.memoize(obj)
            return
        self.save_dict(obj)
    dispatch[DictType] = intellisave_dict

    def save_module(self, obj):
        modname = getModNameForModDict(obj.__dict__)
        if modname:
            self.save(import_module)
            self.save((modname,))
            self.write(pickle.REDUCE)
            self.memoize(obj)
            return
        # We could maybe construct it manually. For now, just fail.
        raise pickle.PicklingError('cannot pickle module %r' % obj)
    dispatch[ModuleType] = save_module

    def save_buffer(self, obj):
        self.save(make_buffer)
        self.save((str(obj),))
        self.write(pickle.REDUCE)
    dispatch[BufferType] = save_buffer

    def save_ndarray(self, obj):
        # For some reason, Numpy fromstring/tostring is faster than Numpy loads/dumps.
        self.save(make_numpy_ndarray_fromstring)
        self.save((obj.tostring(), str(obj.dtype), obj.shape))
        self.write(pickle.REDUCE)
    dispatch[numpy_ndarray] = save_ndarray

    # Overwrite to avoid the broken pickle.whichmodule() which might return "__main__".
    def save_global(self, obj, name=None):
        assert obj
        assert id(obj) not in self.memo
        if name is None:
            name = obj.__name__

        module = getattr(obj, "__module__", None)
        if module is None or module == "__main__":
            module = pickle.whichmodule(obj, name)
        if module is None or module == "__main__":
            raise pickle.PicklingError(
                "Can't pickle %r: module not found: %s" % (obj, module))

        try:
            __import__(module)
            mod = sys.modules[module]
            klass = getattr(mod, name)
        except (ImportError, KeyError, AttributeError):
            raise pickle.PicklingError(
                "Can't pickle %r: it's not found as %s.%s" % (obj, module, name))
        else:
            if klass is not obj:
                raise pickle.PicklingError(
                    "Can't pickle %r: it's not the same object as %s.%s" % (obj, module, name))

        assert "\n" not in module
        assert "\n" not in name
        self.write(pickle.GLOBAL + bytes(module + '\n' + name + '\n', "utf8"))
        self.memoize(obj)

    def save_type(self, obj):
        try:
            self.save_global(obj)
            return
        except pickle.PicklingError:
            pass
        # Some types in the types modules are not correctly referenced,
        # such as types.FunctionType. This is fixed here.
        for modname in ["types"]:
            moddict = sys.modules[modname].__dict__
            for modobjname, modobj in moddict.items():
                if modobj is obj:
                    self.write(pickle.GLOBAL + bytes(modname + '\n' + modobjname + '\n', "utf8"))
                    self.memoize(obj)
                    return
        # Generic serialization of new-style classes.
        self.save(type)
        self.save((obj.__name__, obj.__bases__, getNormalDict(obj.__dict__)))
        self.write(pickle.REDUCE)
        self.memoize(obj)
    dispatch[NewStyleClass] = save_type

    # This is about old-style classes.
    def save_class(self, cls):
        try:
            # First try with a global reference. This works normally. This is the default original pickle behavior.
            self.save_global(cls)
            return
        except pickle.PicklingError:
            pass
        # It didn't worked. But we can still serialize it.
        # Note that this could potentially confuse the code if the class is reference-able in some other way
        # - then we will end up with two versions of the same class.
        self.save(OldStyleClass)
        self.save((cls.__name__, cls.__bases__, cls.__dict__))
        self.write(pickle.REDUCE)
        self.memoize(cls)
        return
    dispatch[OldStyleClass] = save_class

    # avoid pickling instances of ourself. this mostly doesn't make sense and leads to trouble.
    # however, also doesn't break. it mostly makes sense to just ignore.
    def __getstate__(self): return None
    def __setstate__(self, state): pass
