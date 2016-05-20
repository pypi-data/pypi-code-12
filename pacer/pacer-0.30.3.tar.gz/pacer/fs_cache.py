# encoding: utf-8

import datetime
import functools
import glob
import hashlib
import inspect
import json
import multiprocessing
import os
import sys
import time
import weakref

from collections import namedtuple

import dill
import jsonpickle


from .std_logger import get_logger

join = os.path.join


def try_to_rename(from_, to):
    if os.path.exists(to):
        os.remove(to)
    for attempt in range(10):
        try:
            os.rename(from_, to)
            break
        except EnvironmentError:
            time.sleep(.1)
    else:
        raise IOError("can not rename %s to %s" % (from_, to))


def atomic_write(save_function):

    # save_function might need some time for bigger objects and stopping the workflow
    # might result in corrupt files, so we use write-replace for hopefully atomic
    # results:

    @functools.wraps(save_function)
    def inner(what, where):
        result = save_function(what, where + ".incomplete")
        try_to_rename(where + ".incomplete", where)
        return result
    return inner


def json_pretty_encode(obj):
    json_str = jsonpickle.encode(obj)
    pretty_json_str = json.dumps(json.loads(json_str), indent=4)
    return pretty_json_str


def _fallback_save_function():
    ext = ".pickled"

    def save_function(what, path):
        with open(path, "wb") as fp:
            dill.dump(what, fp)
            fp.flush()
            os.fsync(fp.fileno())
    return ext, save_function


def _fallback_load_function():

    def load_function(path):
        with open(path, "rb") as fp:
            return dill.load(fp)
    return load_function


def rel_to_cache_root(p):
    """keep parentf folder + file given for file path p, eg /abc/cde/xdf/x.table -> xdf/x.table"""
    return join(os.path.basename(os.path.split(p)[0]), os.path.split(p)[1])


class CacheLoadError(Exception):

    pass


class CacheItemLoadError(Exception):

    pass


class InvalidCacheException(Exception):

    pass


class CacheItem(object):

    __slots__ = ["annotation", "hash_code_args", "hash_code_result", "rel_path", "loaded", "value",
                 "last_path", "injected"]

    def __init__(self, hash_code_args, hash_code_result, annotation, injected):
        self.hash_code_args = hash_code_args
        self.hash_code_result = hash_code_result
        self.annotation = annotation.copy()
        self.injected = injected
        self.rel_path = None
        self.loaded = False
        self.value = None
        self.last_path = None

    def __eq__(self, other):
        for name in self.__slots__:
            if getattr(self, name) != getattr(other, name):
                return False
        return True

    def __str__(self):
        return "<CachedItem annotation=%s rel_path=%s value=%r loaded=%s hash_code_args=%s hash_code_result=%s>" % (
            self.annotation, self.rel_path, self.value, self.loaded, self.hash_code_args, self.hash_code_result)

    def print_(self, fh=sys.stdout):
        print >> fh, json_pretty_encode(self)

    def load_result(self, cb):
        __, f_ext = os.path.splitext(self.rel_path)
        load_function = cb.tr.lookup_load_function_for(f_ext)
        used_customized_load_function = load_function is not None
        if load_function is None:
            load_function = _fallback_load_function()
        path = join(cb.root_folder, self.rel_path)
        try:
            obj = load_function(path)
        except Exception:
            used = "used %s load function" % (
                "customized" if used_customized_load_function else "fallback")
            raise CacheLoadError("could not load cache content from %s, %s" % (path, used))
        return obj

    def dump(self, path):
        self.last_path = rel_to_cache_root(path)

        def _write(self, path):
            with open(path, "wb") as fh:
                fh.write(json_pretty_encode(self))
                fh.flush()
                os.fsync(fh.fileno())
        atomic_write(_write)(self, path)

    def _check_attributes(self):
        missing = [name for name in self.__slots__ if not hasattr(self, name)]
        if missing:
            msg = ", ".join(missing)
            raise InvalidCacheException("attributes %s are missing. Better clean the cache" % msg)

    @staticmethod
    def load(path):
        try:
            with open(path, "rb") as fh:
                data = fh.read()
        except IOError, e:
            raise IOError(str(e) + "\nreading from %s failed" % path)
        try:
            item = jsonpickle.decode(data)
        except ValueError:
            raise CacheItemLoadError("data in %s is not valid JSON format, maybe your cache is "
                                     "invalid to a pacer update, deleting the cache might help" % fh.name)
        item._check_attributes()
        item.last_path = rel_to_cache_root(fh.name)
        return item


class AnnotatedItem(object):

    def __init__(self, value, **annotation):
        self.value = value
        self.annotation = annotation


class CacheListItem(CacheItem):

    __slots__ = CacheItem.__slots__ + ["sub_items"]

    def __init__(self, *a):
        super(CacheListItem, self).__init__(*a)
        self.sub_items = []

    def __str__(self):
        return "<CacheListItem annotation=%s rel_path=%s value=%r loaded=%s hash_code_args=%s hash_code_result=%s>" % (
            self.annotation, self.rel_path, self.value, self.loaded, self.hash_code_args, self.hash_code_result)

    def create_save_function(self, cb):
        """
        We want to keep CacheItems very minimal for pickling, which is the reason that they have
        no _CacheBuilder attributes.
        Instead we create here the save function depending on cb on the fly.
        """

        def save(what, path):
            self.sub_items = []
            for i, item in enumerate(what):
                ext, save_function, is_atomic = cb.tr.lookup_ext_and_save_function_for(item)
                if ext is None or save_function is None:
                    ext, save_function = _fallback_save_function()
                    is_atomic = False
                full_path = path + "_%d" % i + ext
                if not is_atomic:
                    save_function = atomic_write(save_function)
                save_function(item, full_path)

                hash_code = cb.tr.compute_hash(item)
                sub_item = CacheItem(self.hash_code_args, hash_code, self.annotation, self.injected)
                sub_item.rel_path = rel_to_cache_root(full_path)
                self.sub_items.append(sub_item)
            self.rel_path = rel_to_cache_root(path)

        return save

    def load_result(self, cb):
        items = []
        for p in glob.glob(join(cb.root_folder, self.rel_path + "_*.*")):
            __, f_ext = os.path.splitext(p)
            load_function = cb.tr.lookup_load_function_for(f_ext)
            if load_function is None:
                load_function = _fallback_load_function()
            obj = load_function(p)
            items.append(obj)
        return items

    def __iter__(self):
        return iter(self.sub_items)


_TypeHandler = namedtuple("_TypeHandler", ("type_ hash_data_extractor file_extension "
                                           "load_function save_function info_getter "
                                           "write_is_atomic"))


class TypeHandler(_TypeHandler):

    """pickles all Attributes so we can instances always transmit over wire.
    """

    def __new__(cls, *a):
        args_pickled = map(dill.dumps, a)
        return _TypeHandler.__new__(cls, *args_pickled)

    def __iter__(self):
        for arg in super(TypeHandler, self).__iter__():
            yield dill.loads(arg)

    def __getitem__(self, what):
        item = super(TypeHandler, self).__getitem__(what)
        return dill.loads(item)


class AllAtributesAreNone(object):

    def __getattr__(self, name):
        return None


class DistributedTypeRegistry(object):

    def __init__(self):
        self.reset_handlers()

    def reset_handlers(self):
        self._type_handlers = list()

    def register_handler(self, type_, hash_data_extractor, file_extension, load_function,
                         save_function, info_getter, write_is_atomic=False):
        self._type_handlers.append(TypeHandler(type_,
                                               hash_data_extractor,
                                               file_extension,
                                               load_function,
                                               save_function,
                                               info_getter,
                                               write_is_atomic,
                                               )
                                   )

    def lookup_load_function_for(self, ext):
        for h in self._type_handlers:
            if h.file_extension == ext:
                return h.load_function
        return None

    def _lookup_for_type_of(self, obj):
        for h in self._type_handlers:
            if isinstance(obj, h.type_):
                return h
        return AllAtributesAreNone()

    def lookup_hash_data_extractor_for(self, key):
        return self._lookup_for_type_of(key).hash_data_extractor

    def lookup_ext_and_save_function_for(self, what):
        h = self._lookup_for_type_of(what)
        ext = h.file_extension
        save_function = h.save_function
        is_atomic = h.write_is_atomic
        return ext, save_function, is_atomic

    def lookup_info_getter(self, what):
        return self._lookup_for_type_of(what).info_getter

    def compute_hash(self, key):
        return self._compute_hash(key, set(), [])

    def _compute_hash(self, key, seen, keep):
        """we use see to handle recursive data strucutres, which might happen for example
        for namedtuples sometimes...
        further we keep local data in a list so that the id() calls are unique (we had
        different tuples here with same id because they were created temporarily and
        when recursing they were destroyed and other tuples occupied the same memory
        location, thus resulted in the same id)
        """
        if isinstance(key, CacheItem):
            return key.hash_code_result
        keep.append(key)
        extractor = self.lookup_hash_data_extractor_for(key)
        if extractor is not None:
            key = extractor(key)
            keep.append(key)
        if id(key) in seen and not isinstance(key, (int, float, bool, long, str, tuple)):
            # stop recursion here, return a placeholder which is unique for the item:
            # len() is a good choide because it correspondst to the current state of the
            # stack:
            data = "___memo_%s" % len(seen)
        else:
            seen.add(id(key))
            if isinstance(key, str):
                data = key
            elif isinstance(key, unicode):
                data = key.encode("utf-8")
            elif isinstance(key, (bool, int, long, float,)):
                data = dill.dumps(key)
            elif key is None:
                data = "__None__"
            elif isinstance(key, (tuple, list)):
                data = []
                for item in key:
                    keep.append(item)
                    data.append(self._compute_hash(item, seen, keep))
                data = "".join(data)
            elif isinstance(key, set):
                data = []
                for item in sorted(key):
                    keep.append(item)
                    data.append(self._compute_hash(item, seen, keep))
                data = "".join(data)
            elif isinstance(key, dict):
                data = []
                for item in key.items():
                    keep.append(item[0])
                    keep.append(item[1])
                    keep.append(item)
                    data.append(self._compute_hash(item, seen, keep))
                data = "".join(data)
            elif isinstance(key, datetime.datetime):
                # to float is more complicated than to int using toordinal:
                data = str(time.mktime(key.timetuple()))
            elif hasattr(key, "__dict__"):
                data = self._compute_hash(key.__dict__, seen, keep)
            elif hasattr(key, "__slots__"):
                values = [getattr(key, name) for name in key.__slots__]
                data = self._compute_hash(values, seen, keep)
            else:
                # fallback for all numeric types in old numpy (isinstance fails for int64...):
                try:
                    key + key
                    key - key
                    key * key
                    key / key
                except ZeroDivisionError:
                    pass
                except Exception:
                    raise Exception("can not compute hash for %s %r" % (type(key), key))
                data = dill.dumps(key)
            if not isinstance(data, basestring):
                raise RuntimeError(
                    "implementation error: data should be str, but is %s" % type(data))
        muncher = hashlib.sha1()
        muncher.update(data)
        hash_ = muncher.hexdigest()
        return hash_


class LocalTypeRegistry(DistributedTypeRegistry):

    pass


class _CacheBuilder(object):

    def __init__(self, root_folder=None):
        self.root_folder = root_folder
        self._logger = get_logger(self)
        self._functions = []

    def register_handler(self, *a, **kw):
        self.tr.register_handler(*a, **kw)

    def _setup_folder(self, function):
        folder = function.__name__
        if self.root_folder is not None:
            folder = join(self.root_folder, folder)
        return folder

    def __call__(self, function):
        # folder = self._setup_folder(function)
        cache, lock, counter = self._setup_cache_internals()

        clz = self._cache_function_class()
        c = clz(function, self.root_folder, lock, cache, counter, self.tr)

        self._functions.append(c)
        return c

    def inject_result(self, item, value):
        for f in self._functions:
            new_item = f.inject_result(item, value)
            if new_item is not None:  # hit !
                return new_item

    def remove_injected_result(self, item):
        for f in self._functions:
            f.remove_injected_result(item)

    def _cache_function_class(self):
        return _CachedFunction

    def create_dict(self):
        return dict()

    def remove_unused_entries(self, keep_extensions=()):
        to_keep = set()
        for path in glob.glob(join(self.root_folder, "[!_]*", "__*")):
            to_keep.add(os.path.basename(path)[2:])
        for path in glob.glob(join(self.root_folder, "[!_]*", "*.cache_entry")):
            # we look for proper cache entries, we might have other files in the cache
            # folder...
            hash_value = os.path.splitext(os.path.basename(path))[0]
            if hash_value not in to_keep:
                try:
                    os.remove(path)
                except IOError, e:
                    self._logger.error("could not remove %s: %s" % (path, e.message))

        used_refs = set()
        for path in glob.glob(join(self.root_folder, "[!_]*", "*.cache_entry")):
            item = CacheItem.load(path)
            referenced_path = join(self.root_folder, item.rel_path)
            used_refs.add(referenced_path)
            if isinstance(item, CacheListItem):
                for sub_item in item:
                    referenced_path = join(self.root_folder, sub_item.rel_path)
                    used_refs.add(referenced_path)

        for path in glob.glob(join(self.root_folder, "[!_]*", "*")):
            basename = os.path.basename(path)
            if any(path.endswith(ext) for ext in keep_extensions):
                continue
            if not basename.startswith("__") and not path.endswith(".cache_entry"):
                if path not in used_refs:
                    try:
                        os.remove(path)
                    except IOError, e:
                        self._logger.error("could not remove %s: %s" % (path, e.message))

    def remove_use_markers(self):
        for path in glob.glob(join(self.root_folder, "*", "__*")):
            try:
                os.remove(path)
            except IOError, e:
                self._logger.error("could not remove %s: %s" % (path, e.message))


class CacheBuilder(_CacheBuilder):

    def __init__(self, root_folder=None):
        super(CacheBuilder, self).__init__(root_folder)
        self.tr = DistributedTypeRegistry()
        self._manager = multiprocessing.Manager()

        # shutdown manager if object is deleted, this has less impact to garbage collector
        # than implementing __del__:
        def on_die(ref, manager=self._manager, logger=get_logger()):
            logger.info("try to shutdown multiprocessings manager process")
            manager.shutdown()
            logger.info("finished shutdown multiprocessings manager process")
        self._del_ref = weakref.ref(self, on_die)

    def _setup_cache_internals(self):
        cache = self._manager.dict()
        lock = self._manager.Lock()
        counter = self._manager.Value('d', 0)
        return cache, lock, counter

    def __str__(self):
        return "<CacheBuilder(%s)>" % self.root_folder

    def create_dict(self):
        return self._manager.dict()


class LazyCacheBuilder(CacheBuilder):

    def _cache_function_class(self):
        return _LazyCachedFunction

    def __str__(self):
        return "<LazyCacheBuilder(%s)>" % self.root_folder


class LocalCounter(object):

    def __init__(self):
        self.value = 0


class NoOpContextManager(object):

    def __enter__(self, *a, **kw):
        pass

    __exit__ = __enter__


class LocalCacheBuilder(_CacheBuilder):

    """Cache which only resists in current process, can not be used with pacerd distributed
    computation capabilities ! Use CacheBuilder instead.
    """

    def __init__(self, root_folder=None):
        super(LocalCacheBuilder, self).__init__(root_folder)
        self.tr = LocalTypeRegistry()
        self._manager = None

    def _setup_cache_internals(self):
        cache = dict()
        lock = NoOpContextManager()
        counter = LocalCounter()
        return cache, lock, counter  # , handlers

    def __str__(self):
        return "<LocalCacheBuilder(%s)>" % self.root_folder


class _CachedFunction(object):

    """ Instances of this class can be used to decorate function calls for caching their
    results, even if the functions are executed across different processes started by Python
    multiprocessing modules Pool class.

    The cache is backed up on disk, so that cache entries are persisted over different
    runs.
    """

    def __init__(self, function, root_folder, _lock, _cache, _counter, tr):

        self.function = function
        self.__name__ = function.__name__

        self._cache = _cache
        self._lock = _lock
        self._hit_counter = _counter

        self.root_folder = root_folder

        self.tr = tr

        self._logger = get_logger(self)
        self._setup_cache()
        self._arg_processor = None

    def folder(self):
        return join(self.root_folder, self.function.__name__)

    def __getstate__(self):
        dd = self.__dict__.copy()
        if "_logger" in dd:
            del dd["_logger"]
        return dd

    def register_handler(self, *a, **kw):
        self.tr.register_handler(*a, **kw)

    def __setstate__(self, dd):
        self.__dict__.update(dd)
        self._logger = get_logger(self)

    def get_number_of_hits(self):
        return self._hit_counter.value

    def set_cache_key_preprocessor(self, **kw):
        self._arg_processor = kw

    def _setup_cache(self):
        folder = join(self.root_folder, self.function.__name__)
        if not os.path.exists(folder):
            os.makedirs(folder)
        for file_name in os.listdir(folder):
            path = join(folder, file_name)
            stem, ext = os.path.splitext(file_name)
            if ext == ".cache_entry":
                self._cache[stem] = CacheItem.load(path)

    def clear(self):
        self._cache.clear()

    def _contains(self, hash_code):
        return hash_code in self._cache.keys()

    def _get(self, hash_code):
        item = self._cache[hash_code]
        if not item.loaded:
            value = item.load_result(self)
            item.value = value
            item.loaded = True
        self._cache[hash_code] = item
        return item.value

    def _put(self, hash_code_args, result, annotation, injected):
        assert isinstance(annotation, dict)
        item = self._store(result, hash_code_args, annotation, injected)
        self._cache[hash_code_args] = item
        self._set_use_marker(hash_code_args)
        return item

    def inject_result(self, item, value):
        ci = self._cache.get(item.hash_code_args)
        if ci is not None:
            new_item = self._put(ci.hash_code_args, value, item.annotation, True)
            return new_item

    def remove_injected_result(self, item):
        ci = self._cache.get(item.hash_code_args)
        if ci is not None:
            os.remove(join(self.root_folder, ci.last_path))
            del self._cache[ci.hash_code_args]

    def _store(self, result, hash_code_args, annotation, injected):

        hash_code_result = self.tr.compute_hash(result)

        # create cache entry
        if isinstance(result, list):
            item = CacheListItem(hash_code_args, hash_code_result, annotation, injected)
            save_function = item.create_save_function(self)
            ext = ""
        else:
            item = CacheItem(hash_code_args, hash_code_result, annotation, injected)
            ext, save_function, is_atomic = self.tr.lookup_ext_and_save_function_for(result)
            if ext is None or save_function is None:
                ext, save_function = _fallback_save_function()
                is_atomic = False
            if not is_atomic:
                save_function = atomic_write(save_function)

        # write result if not known
        path = join(self.root_folder, self.function.__name__, hash_code_result + ext)
        if not os.path.exists(path):
            save_function(result, path)
            self._logger.info("stored %s" % path)
        else:
            self._logger.info("no need to store item to %s" % path)

        item.rel_path = rel_to_cache_root(path)
        self._write_cache_item(hash_code_args, item)
        return item

    def _write_cache_item(self, hash_code_args, item):
        name = hash_code_args + ".cache_entry"
        path = join(self.root_folder, self.function.__name__, name)
        item.dump(path)
        return item

    def _get_names(self, args):
        for arg in args:
            if isinstance(arg, CacheItem):
                yield arg.name
            else:
                getter = self.tr.lookup_info_getter(arg)
                if getter is not None:
                    yield getter(arg)

    def _setup_args(self, args):
        if self._arg_processor is None:
            return args
        arg_names = inspect.getargspec(self.function).args
        result = []
        for arg, name in zip(args, arg_names):
            if not isinstance(arg, CacheItem):
                if name in self._arg_processor:
                    arg_processor = self._arg_processor.get(name)
                    if hasattr(arg_processor, "__call__"):
                        arg = arg_processor(arg)
                    else:
                        arg = arg_processor
            result.append(arg)
        return result

    def cached_call(self, args, kw):
        self._logger.info("cached call for %s" % self.function.__name__)
        all_args = list(args) + list(sorted(kw.items()))
        try:
            args_for_hash = self._setup_args(all_args)
            hash_code_args = self.tr.compute_hash(args_for_hash)
        except RuntimeError:
            raise Exception("could not compute hash for %r. maybe you should register your own "
                            "handler" % (all_args,))
        if self._contains(hash_code_args):
            with self._lock:
                self._hit_counter.value += 1
            self._logger.info("cache hit for %s" % hash_code_args)
            ci = self._get(hash_code_args)
            # ci.print_()
            self._set_use_marker(hash_code_args)
            return ci, ci

        args = self.resolve_inputs(args)
        result = self.function(*args, **kw)

        annotation = {}
        if isinstance(result, AnnotatedItem):
            annotation = result.annotation
            result = result.value

        self._logger.info("store new result for %s" % hash_code_args)
        item = self._put(hash_code_args, result, annotation, False)
        self._logger.info("stored new result for %s" % hash_code_args)
        return result, item

    def _set_use_marker(self, hash_code):
        sub_folder = join(self.root_folder, self.function.__name__)
        marker_path = join(sub_folder, "__" + hash_code)
        try:
            with open(marker_path, "w"):
                pass
        except IOError, e:
            self._logger.error("could not write to %s: %s" % (marker_path, e.message))
            raise

    def __call__(self, *args, **kw):
        result, item = self.cached_call(args, kw)
        return result

    def resolve_inputs(self, i):
        return i

    def __str__(self):
        return "<_CachedFunction(%s)>" % self.function.__name__


class _LazyCachedFunction(_CachedFunction):

    def _get(self, hash_code):
        item = self._cache[hash_code]
        # item ist multiple + modues is "beak lists" ?
        # aufliösen zu liste von cacheitems
        return item

    def __call__(self, *args, **kw):
        result, item = self.cached_call(args, kw)
        return item

    def __str__(self):
        return "<_LazyCachedFunction(%s)>" % self.function.__name__

    def resolve_inputs(self, args):
        if isinstance(args, (list, tuple)):
            loaded = [a.load_result(self) if isinstance(
                a, CacheItem) else self.resolve_inputs(a) for a in args]
            if isinstance(args, (tuple,)):
                loaded = tuple(loaded)
            return loaded
        if isinstance(args, CacheItem):
            return args.load_result(self)
        return args
