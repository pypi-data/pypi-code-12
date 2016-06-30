"""Amalgamation of xonsh package, made up of the following modules, in order:

* completer
* lazyasd
* lazyjson
* pretty
* timings
* ansi_colors
* codecache
* openpy
* platform
* teepty
* jobs
* parser
* tokenize
* tools
* vox
* ast
* contexts
* diff_history
* dirstack
* foreign_shells
* inspectors
* lexer
* proc
* xontribs
* commands_cache
* environ
* history
* base_shell
* replay
* tracer
* xonfig
* aliases
* readline_shell
* built_ins
* execer
* imphooks
* shell
* main

"""

from sys import modules as _modules
from types import ModuleType as _ModuleType
from importlib import import_module as _import_module


class _LazyModule(_ModuleType):

    def __init__(self, pkg, mod, asname=None):
        '''Lazy module 'pkg.mod' in package 'pkg'.'''
        self.__dct__ = {
            'loaded': False,
            'pkg': pkg,  # pkg
            'mod': mod,  # pkg.mod
            'asname': asname,  # alias
            }

    @classmethod
    def load(cls, pkg, mod, asname=None):
        if mod in _modules:
            return _modules[pkg]
        else:
            return cls(pkg, mod, asname)

    def __getattribute__(self, name):
        if name == '__dct__':
            return super().__getattribute__(name)
        dct = self.__dct__
        mod = dct['mod']
        if dct['loaded']:
            m = _modules[mod]
        else:
            m = _import_module(mod)
            glbs = globals()
            pkg = dct['pkg']
            asname = dct['asname']
            if asname is None:
                glbs[pkg] = m = _modules[pkg]
            else:
                glbs[asname] = m
            dct['loaded'] = True
        return getattr(m, name)

#
# completer
#
# -*- coding: utf-8 -*-
"""A (tab-)completer for xonsh."""
builtins = _LazyModule.load('builtins', 'builtins')
abc = _LazyModule.load('collections', 'collections.abc', 'abc')
compbash = _LazyModule.load('xonsh', 'xonsh.completers.bash', 'compbash')
class Completer(object):
    """This provides a list of optional completions for the xonsh shell."""
    def __init__(self):
        compbash.update_bash_completion()

    def complete(self, prefix, line, begidx, endidx, ctx=None):
        """Complete the string, given a possible execution context.

        Parameters
        ----------
        prefix : str
            The string to match
        line : str
            The line that prefix appears on.
        begidx : int
            The index in line that prefix starts on.
        endidx : int
            The index in line that prefix ends on.
        ctx : Iterable of str (ie dict, set, etc), optional
            Names in the current execution context.

        Returns
        -------
        rtn : list of str
            Possible completions of prefix, sorted alphabetically.
        lprefix : int
            Length of the prefix to be replaced in the completion
            (only used with prompt_toolkit)
        """
        ctx = ctx or {}
        for func in builtins.__xonsh_completers__.values():
            try:
                out = func(prefix, line, begidx, endidx, ctx)
            except StopIteration:
                return set(), len(prefix)
            if isinstance(out, abc.Sequence):
                res, lprefix = out
            else:
                res = out
                lprefix = len(prefix)
            if res is not None and len(res) != 0:
                def sortkey(s): return s.lstrip(''''"''').lower()
                return tuple(sorted(res, key=sortkey)), lprefix
        return set(), lprefix

#
# lazyasd
#
"""Lazy and self destrctive containers for speeding up module import."""
# Copyright 2015-2016, the xonsh developers. All rights reserved.
os = _LazyModule.load('os', 'os')
sys = _LazyModule.load('sys', 'sys')
time = _LazyModule.load('time', 'time')
types = _LazyModule.load('types', 'types')
# amalgamated builtins
threading = _LazyModule.load('threading', 'threading')
importlib = _LazyModule.load('importlib', 'importlib')
importlib = _LazyModule.load('importlib', 'importlib.util')
# amalgamated collections.abc
class LazyObject(object):

    def __init__(self, load, ctx, name):
        """Lazily loads an object via the load function the first time an
        attribute is accessed. Once loaded it will replace itself in the
        provided context (typically the globals of the call site) with the
        given name.

        For example, you can prevent the compilation of a regular expreession
        until it is actually used::

            DOT = LazyObject((lambda: re.compile('.')), globals(), 'DOT')

        Parameters
        ----------
        load : function with no arguments
            A loader function that performs the actual object construction.
        ctx : Mapping
            Context to replace the LazyObject instance in
            with the object returned by load().
        name : str
            Name in the context to give the loaded object. This *should*
            be the name on the LHS of the assignment.
        """
        self._lasdo = {
            'loaded': False,
            'load': load,
            'ctx': ctx,
            'name': name,
            }

    def _lazy_obj(self):
        d = self._lasdo
        if d['loaded']:
            obj = d['obj']
        else:
            obj = d['load']()
            d['ctx'][d['name']] = d['obj'] = obj
            d['loaded'] = True
        return obj

    def __getattribute__(self, name):
        if name == '_lasdo' or name == '_lazy_obj':
            return super().__getattribute__(name)
        obj = self._lazy_obj()
        return getattr(obj, name)

    def __bool__(self):
        obj = self._lazy_obj()
        return bool(obj)

    def __iter__(self):
        obj = self._lazy_obj()
        yield from obj

    def __getitem__(self, item):
        obj = self._lazy_obj()
        return obj[item]


class LazyDict(abc.MutableMapping):

    def __init__(self, loaders, ctx, name):
        """Dictionary like object that lazily loads its values from an initial
        dict of key-loader function pairs.  Each key is loaded when its value
        is first accessed. Once fully loaded, this object will replace itself
        in the provided context (typically the globals of the call site) with
        the given name.

        For example, you can prevent the compilation of a bunch of regular
        expressions until they are actually used::

            RES = LazyDict({
                    'dot': lambda: re.compile('.'),
                    'all': lambda: re.compile('.*'),
                    'two': lambda: re.compile('..'),
                    }, globals(), 'RES')

        Parameters
        ----------
        loaders : Mapping of keys to functions with no arguments
            A mapping of loader function that performs the actual value
            construction upon acces.
        ctx : Mapping
            Context to replace the LazyDict instance in
            with the the fully loaded mapping.
        name : str
            Name in the context to give the loaded mapping. This *should*
            be the name on the LHS of the assignment.
        """
        self._loaders = loaders
        self._ctx = ctx
        self._name = name
        self._d = type(loaders)()  # make sure to return the same type

    def _destruct(self):
        if len(self._loaders) == 0:
            self._ctx[self._name] = self._d

    def __getitem__(self, key):
        d = self._d
        if key in d:
            val = d[key]
        else:
            # pop will raise a key error for us
            loader = self._loaders.pop(key)
            d[key] = val = loader()
            self._destruct()
        return val

    def __setitem__(self, key, value):
        self._d[key] = value
        if key in self._loaders:
            del self._loaders[key]
            self._destruct()

    def __delitem__(self, key):
        if key in self._d:
            del self._d[lkey]
        else:
            del self._loaders[key]
            self._destruct()

    def __iter__(self):
        yield from (set(self._d.keys()) | set(self._loaders.keys()))

    def __len__(self):
        return len(self._d) + len(self._loaders)


class LazyBool(object):

    def __init__(self, load, ctx, name):
        """Boolean like object that lazily computes it boolean value when it is
        first asked. Once loaded, this result will replace itself
        in the provided context (typically the globals of the call site) with
        the given name.

        For example, you can prevent the complex boolean until it is actually
        used::

            ALIVE = LazyDict(lambda: not DEAD, globals(), 'ALIVE')

        Parameters
        ----------
        load : function with no arguments
            A loader function that performs the actual boolean evaluation.
        ctx : Mapping
            Context to replace the LazyBool instance in
            with the the fully loaded mapping.
        name : str
            Name in the context to give the loaded mapping. This *should*
            be the name on the LHS of the assignment.
        """
        self._load = load
        self._ctx = ctx
        self._name = name
        self._result = None

    def __bool__(self):
        if self._result is None:
            res = self._ctx[self._name] = self._result = self._load()
        else:
            res = self._result
        return res

#
# Background module loaders
#

class BackgroundModuleProxy(types.ModuleType):
    """Proxy object for modules loaded in the background that block attribute
    access until the module is loaded..
    """

    def __init__(self, modname):
        self.__dct__ = {
            'loaded': False,
            'modname': modname,
            }

    def __getattribute__(self, name):
        passthrough = frozenset({'__dct__','__class__', '__spec__'})
        if name in passthrough:
            return super().__getattribute__(name)
        dct = self.__dct__
        modname = dct['modname']
        if dct['loaded']:
            mod = sys.modules[modname]
        else:
            delay_types = (BackgroundModuleProxy, type(None))
            while isinstance(sys.modules.get(modname, None), delay_types):
                time.sleep(0.001)
            mod = sys.modules[modname]
            dct['loaded'] = True
        return getattr(mod, name)


class BackgroundModuleLoader(threading.Thread):
    """Thread to load modules in the background."""

    def __init__(self, name, package, replacements, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.daemon = True
        self.name = name
        self.package = package
        self.replacements = replacements
        self.start()

    def run(self):
        # wait for other modules to stop being imported
        i = 0
        last = -6
        hist = [-5, -4, -3, -2, -1]
        while not all(last == x for x in hist):
            time.sleep(0.001)
            last = hist[i%5] = len(sys.modules)
            i += 1
        # now import pkg_resources properly
        modname = importlib.util.resolve_name(self.name, self.package)
        if isinstance(sys.modules[modname], BackgroundModuleProxy):
            del sys.modules[modname]
        mod = importlib.import_module(self.name, package=self.package)
        for targname, varname in self.replacements.items():
            if targname in sys.modules:
                targmod = sys.modules[targname]
                setattr(targmod, varname, mod)


def load_module_in_background(name, package=None, debug='DEBUG', env=None,
                              replacements=None):
    """Entry point for loading modules in background thread.

    Parameters
    ----------
    name : str
        Module name to load in background thread.
    package : str or None, optional
        Package name, has the same meaning as in importlib.import_module().
    debug : str, optional
        Debugging symbol name to look up in the environment.
    env : Mapping or None, optional
        Environment this will default to __xonsh_env__, if available, and
        os.environ otherwise.
    replacements : Mapping or None, optional
        Dictionary mapping fully qualified module names (eg foo.bar.baz) that
        import the lazily loaded moudle, with the variable name in that
        module. For example, suppose that foo.bar imports module a as b,
        this dict is then {'foo.bar': 'b'}.

    Returns
    -------
    module : ModuleType
        This is either the original module that is found in sys.modules or
        a proxy module that will block until delay attribute access until the
        module is fully loaded.
    """
    modname = importlib.util.resolve_name(name, package)
    if modname in sys.modules:
        return sys.modules[modname]
    if env is None:
        env = getattr(builtins, '__xonsh_env__', os.environ)
    if env.get(debug, None):
        mod = importlib.import_module(name, package=package)
        return mod
    proxy = sys.modules[modname] = BackgroundModuleProxy(modname)
    BackgroundModuleLoader(name, package, replacements or {})
    return proxy

#
# lazyjson
#
# -*- coding: utf-8 -*-
"""Implements a lazy JSON file class that wraps around json data."""
io = _LazyModule.load('io', 'io')
json = _LazyModule.load('json', 'json')
weakref = _LazyModule.load('weakref', 'weakref')
contextlib = _LazyModule.load('contextlib', 'contextlib')
# amalgamated collections.abc
def _to_json_with_size(obj, offset=0, sort_keys=False):
    if isinstance(obj, str):
        s = json.dumps(obj)
        o = offset
        n = size = len(s.encode())  # size in bytes
    elif isinstance(obj, abc.Mapping):
        s = '{'
        j = offset + 1
        o = {}
        size = {}
        items = sorted(obj.items()) if sort_keys else obj.items()
        for key, val in items:
            s_k, o_k, n_k, size_k = _to_json_with_size(key, offset=j,
                                                       sort_keys=sort_keys)
            s += s_k + ': '
            j += n_k + 2
            s_v, o_v, n_v, size_v = _to_json_with_size(val, offset=j,
                                                       sort_keys=sort_keys)
            o[key] = o_v
            size[key] = size_v
            s += s_v + ', '
            j += n_v + 2
        if s.endswith(', '):
            s = s[:-2]
        s += '}\n'
        n = len(s)
        o['__total__'] = offset
        size['__total__'] = n
    elif isinstance(obj, abc.Sequence):
        s = '['
        j = offset + 1
        o = []
        size = []
        for x in obj:
            s_x, o_x, n_x, size_x = _to_json_with_size(x, offset=j,
                                                       sort_keys=sort_keys)
            o.append(o_x)
            size.append(size_x)
            s += s_x + ', '
            j += n_x + 2
        if s.endswith(', '):
            s = s[:-2]
        s += ']\n'
        n = len(s)
        o.append(offset)
        size.append(n)
    else:
        s = json.dumps(obj, sort_keys=sort_keys)
        o = offset
        n = size = len(s)
    return s, o, n, size


def index(obj, sort_keys=False):
    """Creates an index for a JSON file."""
    idx = {}
    json_obj = _to_json_with_size(obj, sort_keys=sort_keys)
    s, idx['offsets'], _, idx['sizes'] = json_obj
    return s, idx


JSON_FORMAT = \
"""{{"locs": [{iloc:>10}, {ilen:>10}, {dloc:>10}, {dlen:>10}],
 "index": {index},
 "data": {data}
}}
"""


def dumps(obj, sort_keys=False):
    """Dumps an object to JSON with an index."""
    data, idx = index(obj, sort_keys=sort_keys)
    jdx = json.dumps(idx, sort_keys=sort_keys)
    iloc = 69
    ilen = len(jdx)
    dloc = iloc + ilen + 11
    dlen = len(data)
    s = JSON_FORMAT.format(index=jdx, data=data, iloc=iloc, ilen=ilen,
                           dloc=dloc, dlen=dlen)
    return s


def ljdump(obj, fp, sort_keys=False):
    """Dumps an object to JSON file."""
    s = dumps(obj, sort_keys=sort_keys)
    fp.write(s)


class LJNode(abc.Mapping, abc.Sequence):
    """A proxy node for JSON nodes. Acts as both sequence and mapping."""

    def __init__(self, offsets, sizes, root):
        """Parameters
        ----------
        offsets : dict, list, or int
            offsets of corresponding data structure, in bytes
        sizes : dict, list, or int
            sizes of corresponding data structure, in bytes
        root : weakref.proxy of LazyJSON
            weakref back to root node, which should be a LazyJSON object.
        """
        self.offsets = offsets
        self.sizes = sizes
        self.root = root
        self.is_mapping = isinstance(self.offsets, abc.Mapping)
        self.is_sequence = isinstance(self.offsets, abc.Sequence)

    def __len__(self):
        # recall that for maps, the '__total__' key is added and for
        # sequences the last element represents the total size/offset.
        return len(self.sizes) - 1

    def load(self):
        """Returns the Python data structure represented by the node."""
        if self.is_mapping:
            offset = self.offsets['__total__']
            size = self.sizes['__total__']
        elif self.is_sequence:
            offset = self.offsets[-1]
            size = self.sizes[-1]
        elif isinstance(self.offsets, int):
            offset = self.offsets
            size = self.sizes
        return self._load_or_node(offset, size)

    def _load_or_node(self, offset, size):
        if isinstance(offset, int):
            with self.root._open(newline='\n') as f:
                f.seek(self.root.dloc + offset)
                s = f.read(size)
            val = json.loads(s)
        elif isinstance(offset, (abc.Mapping, abc.Sequence)):
            val = LJNode(offset, size, self.root)
        else:
            raise TypeError('incorrect types for offset node')
        return val

    def _getitem_mapping(self, key):
        if key == '__total__':
            raise KeyError('"__total__" is a special LazyJSON key!')
        offset = self.offsets[key]
        size = self.sizes[key]
        return self._load_or_node(offset, size)

    def _getitem_sequence(self, key):
        if isinstance(key, int):
            rtn = self._load_or_node(self.offsets[key], self.sizes[key])
        elif isinstance(key, slice):
            key = slice(*key.indices(len(self)))
            rtn = list(map(self._load_or_node, self.offsets[key],
                           self.sizes[key]))
        else:
            raise TypeError('only integer indexing available')
        return rtn

    def __getitem__(self, key):
        if self.is_mapping:
            rtn = self._getitem_mapping(key)
        elif self.is_sequence:
            rtn = self._getitem_sequence(key)
        else:
            raise NotImplementedError
        return rtn

    def __iter__(self):
        if self.is_mapping:
            keys = set(self.offsets.keys())
            keys.discard('__total__')
            yield from iter(keys)
        elif self.is_sequence:
            i = 0
            n = len(self)
            while i < n:
                yield self._load_or_node(self.offsets[i], self.sizes[i])
                i += 1
        else:
            raise NotImplementedError


class LazyJSON(LJNode):
    """Represents a lazy json file. Can be used like a normal Python
    dict or list.
    """

    def __init__(self, f, reopen=True):
        """Parameters
        ----------
        f : file handle or str
            JSON file to open.
        reopen : bool, optional
            Whether new file handle should be opened for each load.
        """
        self._f = f
        self.reopen = reopen
        if not reopen and isinstance(f, str):
            self._f = open(f, 'r', newline='\n')
        self._load_index()
        self.root = weakref.proxy(self)
        self.is_mapping = isinstance(self.offsets, abc.Mapping)
        self.is_sequence = isinstance(self.offsets, abc.Sequence)

    def __del__(self):
        self.close()

    def close(self):
        """Close the file handle, if appropriate."""
        if not self.reopen and isinstance(self._f, io.IOBase):
            self._f.close()

    @contextlib.contextmanager
    def _open(self, *args, **kwargs):
        if self.reopen and isinstance(self._f, str):
            f = open(self._f, *args, **kwargs)
            yield f
            f.close()
        else:
            yield self._f

    def _load_index(self):
        """Loads the index from the start of the file."""
        with self._open(newline='\n') as f:
            # read in the location data
            f.seek(9)
            locs = f.read(48)
            locs = json.loads(locs)
            self.iloc, self.ilen, self.dloc, self.dlen = locs
            # read in the index
            f.seek(self.iloc)
            idx = f.read(self.ilen)
            idx = json.loads(idx)
        self.offsets = idx['offsets']
        self.sizes = idx['sizes']

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


#
# pretty
#
# -*- coding: utf-8 -*-
"""
Python advanced pretty printer.  This pretty printer is intended to
replace the old `pprint` python module which does not allow developers
to provide their own pretty print callbacks.

This module is based on ruby's `prettyprint.rb` library by `Tanaka Akira`.

The following implementations were forked from the IPython project:
* Copyright (c) 2008-2014, IPython Development Team
* Copyright (C) 2001-2007 Fernando Perez <fperez@colorado.edu>
* Copyright (c) 2001, Janko Hauser <jhauser@zscout.de>
* Copyright (c) 2001, Nathaniel Gray <n8gray@caltech.edu>

Example Usage
-------------

To directly print the representation of an object use `pprint`::

    from pretty import pprint
    pprint(complex_object)

To get a string of the output use `pretty`::

    from pretty import pretty
    string = pretty(complex_object)


Extending
---------

The pretty library allows developers to add pretty printing rules for their
own objects.  This process is straightforward.  All you have to do is to
add a `_repr_pretty_` method to your object and call the methods on the
pretty printer passed::

    class MyObject(object):

        def _repr_pretty_(self, p, cycle):
            ...

Here is an example implementation of a `_repr_pretty_` method for a list
subclass::

    class MyList(list):

        def _repr_pretty_(self, p, cycle):
            if cycle:
                p.text('MyList(...)')
            else:
                with p.group(8, 'MyList([', '])'):
                    for idx, item in enumerate(self):
                        if idx:
                            p.text(',')
                            p.breakable()
                        p.pretty(item)

The `cycle` parameter is `True` if pretty detected a cycle.  You *have* to
react to that or the result is an infinite loop.  `p.text()` just adds
non breaking text to the output, `p.breakable()` either adds a whitespace
or breaks here.  If you pass it an argument it's used instead of the
default space.  `p.pretty` prettyprints another object using the pretty print
method.

The first parameter to the `group` function specifies the extra indentation
of the next line.  In this example the next item will either be on the same
line (if the items are short enough) or aligned with the right edge of the
opening bracket of `MyList`.

If you just want to indent something you can use the group function
without open / close parameters.  You can also use this code::

    with p.indent(2):
        ...


:copyright: 2007 by Armin Ronacher.
            Portions (c) 2009 by Robert Kern.
:license: BSD License.
"""
from contextlib import contextmanager
# amalgamated sys
# amalgamated types
re = _LazyModule.load('re', 're')
datetime = _LazyModule.load('datetime', 'datetime')
from collections import deque

#from IPython.utils.py3compat import PY3, cast_unicode, string_types
#from IPython.utils.encoding import get_stream_enc

from io import StringIO


__all__ = ['pretty', 'pprint', 'PrettyPrinter', 'RepresentationPrinter',
    'for_type', 'for_type_by_name']


MAX_SEQ_LENGTH = 1000
_re_pattern_type = type(re.compile(''))

def _safe_getattr(obj, attr, default=None):
    """Safe version of getattr.

    Same as getattr, but will return ``default`` on any Exception,
    rather than raising.
    """
    try:
        return getattr(obj, attr, default)
    except Exception:
        return default

#if PY3:
CUnicodeIO = StringIO
#else:
#    class CUnicodeIO(StringIO):
#        """StringIO that casts str to unicode on Python 2"""
#        def write(self, text):
#            return super(CUnicodeIO, self).write(
#                cast_unicode(text, encoding=get_stream_enc(sys.stdout)))


def pretty(obj, verbose=False, max_width=79, newline='\n', max_seq_length=MAX_SEQ_LENGTH):
    """
    Pretty print the object's representation.
    """
    stream = CUnicodeIO()
    printer = RepresentationPrinter(stream, verbose, max_width, newline, max_seq_length=max_seq_length)
    printer.pretty(obj)
    printer.flush()
    return stream.getvalue()


def pprint(obj, verbose=False, max_width=79, newline='\n', max_seq_length=MAX_SEQ_LENGTH):
    """
    Like `pretty` but print to stdout.
    """
    printer = RepresentationPrinter(sys.stdout, verbose, max_width, newline, max_seq_length=max_seq_length)
    printer.pretty(obj)
    printer.flush()
    sys.stdout.write(newline)
    sys.stdout.flush()

class _PrettyPrinterBase(object):

    @contextmanager
    def indent(self, indent):
        """with statement support for indenting/dedenting."""
        self.indentation += indent
        try:
            yield
        finally:
            self.indentation -= indent

    @contextmanager
    def group(self, indent=0, open='', close=''):
        """like begin_group / end_group but for the with statement."""
        self.begin_group(indent, open)
        try:
            yield
        finally:
            self.end_group(indent, close)

class PrettyPrinter(_PrettyPrinterBase):
    """
    Baseclass for the `RepresentationPrinter` prettyprinter that is used to
    generate pretty reprs of objects.  Contrary to the `RepresentationPrinter`
    this printer knows nothing about the default pprinters or the `_repr_pretty_`
    callback method.
    """

    def __init__(self, output, max_width=79, newline='\n', max_seq_length=MAX_SEQ_LENGTH):
        self.output = output
        self.max_width = max_width
        self.newline = newline
        self.max_seq_length = max_seq_length
        self.output_width = 0
        self.buffer_width = 0
        self.buffer = deque()

        root_group = Group(0)
        self.group_stack = [root_group]
        self.group_queue = GroupQueue(root_group)
        self.indentation = 0

    def _break_outer_groups(self):
        while self.max_width < self.output_width + self.buffer_width:
            group = self.group_queue.deq()
            if not group:
                return
            while group.breakables:
                x = self.buffer.popleft()
                self.output_width = x.output(self.output, self.output_width)
                self.buffer_width -= x.width
            while self.buffer and isinstance(self.buffer[0], Text):
                x = self.buffer.popleft()
                self.output_width = x.output(self.output, self.output_width)
                self.buffer_width -= x.width

    def text(self, obj):
        """Add literal text to the output."""
        width = len(obj)
        if self.buffer:
            text = self.buffer[-1]
            if not isinstance(text, Text):
                text = Text()
                self.buffer.append(text)
            text.add(obj, width)
            self.buffer_width += width
            self._break_outer_groups()
        else:
            self.output.write(obj)
            self.output_width += width

    def breakable(self, sep=' '):
        """
        Add a breakable separator to the output.  This does not mean that it
        will automatically break here.  If no breaking on this position takes
        place the `sep` is inserted which default to one space.
        """
        width = len(sep)
        group = self.group_stack[-1]
        if group.want_break:
            self.flush()
            self.output.write(self.newline)
            self.output.write(' ' * self.indentation)
            self.output_width = self.indentation
            self.buffer_width = 0
        else:
            self.buffer.append(Breakable(sep, width, self))
            self.buffer_width += width
            self._break_outer_groups()

    def break_(self):
        """
        Explicitly insert a newline into the output, maintaining correct indentation.
        """
        self.flush()
        self.output.write(self.newline)
        self.output.write(' ' * self.indentation)
        self.output_width = self.indentation
        self.buffer_width = 0


    def begin_group(self, indent=0, open=''):
        """
        Begin a group.  If you want support for python < 2.5 which doesn't has
        the with statement this is the preferred way:

            p.begin_group(1, '{')
            ...
            p.end_group(1, '}')

        The python 2.5 expression would be this:

            with p.group(1, '{', '}'):
                ...

        The first parameter specifies the indentation for the next line (usually
        the width of the opening text), the second the opening text.  All
        parameters are optional.
        """
        if open:
            self.text(open)
        group = Group(self.group_stack[-1].depth + 1)
        self.group_stack.append(group)
        self.group_queue.enq(group)
        self.indentation += indent

    def _enumerate(self, seq):
        """like enumerate, but with an upper limit on the number of items"""
        for idx, x in enumerate(seq):
            if self.max_seq_length and idx >= self.max_seq_length:
                self.text(',')
                self.breakable()
                self.text('...')
                return
            yield idx, x

    def end_group(self, dedent=0, close=''):
        """End a group. See `begin_group` for more details."""
        self.indentation -= dedent
        group = self.group_stack.pop()
        if not group.breakables:
            self.group_queue.remove(group)
        if close:
            self.text(close)

    def flush(self):
        """Flush data that is left in the buffer."""
        for data in self.buffer:
            self.output_width += data.output(self.output, self.output_width)
        self.buffer.clear()
        self.buffer_width = 0


def _get_mro(obj_class):
    """ Get a reasonable method resolution order of a class and its superclasses
    for both old-style and new-style classes.
    """
    if not hasattr(obj_class, '__mro__'):
        # Old-style class. Mix in object to make a fake new-style class.
        try:
            obj_class = type(obj_class.__name__, (obj_class, object), {})
        except TypeError:
            # Old-style extension type that does not descend from object.
            # FIXME: try to construct a more thorough MRO.
            mro = [obj_class]
        else:
            mro = obj_class.__mro__[1:-1]
    else:
        mro = obj_class.__mro__
    return mro


class RepresentationPrinter(PrettyPrinter):
    """
    Special pretty printer that has a `pretty` method that calls the pretty
    printer for a python object.

    This class stores processing data on `self` so you must *never* use
    this class in a threaded environment.  Always lock it or reinstanciate
    it.

    Instances also have a verbose flag callbacks can access to control their
    output.  For example the default instance repr prints all attributes and
    methods that are not prefixed by an underscore if the printer is in
    verbose mode.
    """

    def __init__(self, output, verbose=False, max_width=79, newline='\n',
        singleton_pprinters=None, type_pprinters=None, deferred_pprinters=None,
        max_seq_length=MAX_SEQ_LENGTH):

        PrettyPrinter.__init__(self, output, max_width, newline, max_seq_length=max_seq_length)
        self.verbose = verbose
        self.stack = []
        if singleton_pprinters is None:
            singleton_pprinters = _singleton_pprinters.copy()
        self.singleton_pprinters = singleton_pprinters
        if type_pprinters is None:
            type_pprinters = _type_pprinters.copy()
        self.type_pprinters = type_pprinters
        if deferred_pprinters is None:
            deferred_pprinters = _deferred_type_pprinters.copy()
        self.deferred_pprinters = deferred_pprinters

    def pretty(self, obj):
        """Pretty print the given object."""
        obj_id = id(obj)
        cycle = obj_id in self.stack
        self.stack.append(obj_id)
        self.begin_group()
        try:
            obj_class = _safe_getattr(obj, '__class__', None) or type(obj)
            # First try to find registered singleton printers for the type.
            try:
                printer = self.singleton_pprinters[obj_id]
            except (TypeError, KeyError):
                pass
            else:
                return printer(obj, self, cycle)
            # Next walk the mro and check for either:
            #   1) a registered printer
            #   2) a _repr_pretty_ method
            for cls in _get_mro(obj_class):
                if cls in self.type_pprinters:
                    # printer registered in self.type_pprinters
                    return self.type_pprinters[cls](obj, self, cycle)
                else:
                    # deferred printer
                    printer = self._in_deferred_types(cls)
                    if printer is not None:
                        return printer(obj, self, cycle)
                    else:
                        # Finally look for special method names.
                        # Some objects automatically create any requested
                        # attribute. Try to ignore most of them by checking for
                        # callability.
                        if '_repr_pretty_' in cls.__dict__:
                            meth = cls._repr_pretty_
                            if callable(meth):
                                return meth(obj, self, cycle)
            return _default_pprint(obj, self, cycle)
        finally:
            self.end_group()
            self.stack.pop()

    def _in_deferred_types(self, cls):
        """
        Check if the given class is specified in the deferred type registry.

        Returns the printer from the registry if it exists, and None if the
        class is not in the registry. Successful matches will be moved to the
        regular type registry for future use.
        """
        mod = _safe_getattr(cls, '__module__', None)
        name = _safe_getattr(cls, '__name__', None)
        key = (mod, name)
        printer = None
        if key in self.deferred_pprinters:
            # Move the printer over to the regular registry.
            printer = self.deferred_pprinters.pop(key)
            self.type_pprinters[cls] = printer
        return printer


class Printable(object):

    def output(self, stream, output_width):
        return output_width


class Text(Printable):

    def __init__(self):
        self.objs = []
        self.width = 0

    def output(self, stream, output_width):
        for obj in self.objs:
            stream.write(obj)
        return output_width + self.width

    def add(self, obj, width):
        self.objs.append(obj)
        self.width += width


class Breakable(Printable):

    def __init__(self, seq, width, pretty):
        self.obj = seq
        self.width = width
        self.pretty = pretty
        self.indentation = pretty.indentation
        self.group = pretty.group_stack[-1]
        self.group.breakables.append(self)

    def output(self, stream, output_width):
        self.group.breakables.popleft()
        if self.group.want_break:
            stream.write(self.pretty.newline)
            stream.write(' ' * self.indentation)
            return self.indentation
        if not self.group.breakables:
            self.pretty.group_queue.remove(self.group)
        stream.write(self.obj)
        return output_width + self.width


class Group(Printable):

    def __init__(self, depth):
        self.depth = depth
        self.breakables = deque()
        self.want_break = False


class GroupQueue(object):

    def __init__(self, *groups):
        self.queue = []
        for group in groups:
            self.enq(group)

    def enq(self, group):
        depth = group.depth
        while depth > len(self.queue) - 1:
            self.queue.append([])
        self.queue[depth].append(group)

    def deq(self):
        for stack in self.queue:
            for idx, group in enumerate(reversed(stack)):
                if group.breakables:
                    del stack[idx]
                    group.want_break = True
                    return group
            for group in stack:
                group.want_break = True
            del stack[:]

    def remove(self, group):
        try:
            self.queue[group.depth].remove(group)
        except ValueError:
            pass

try:
    _baseclass_reprs = (object.__repr__, types.InstanceType.__repr__)
except AttributeError:  # Python 3
    _baseclass_reprs = (object.__repr__,)


def _default_pprint(obj, p, cycle):
    """
    The default print function.  Used if an object does not provide one and
    it's none of the builtin objects.
    """
    klass = _safe_getattr(obj, '__class__', None) or type(obj)
    if _safe_getattr(klass, '__repr__', None) not in _baseclass_reprs:
        # A user-provided repr. Find newlines and replace them with p.break_()
        _repr_pprint(obj, p, cycle)
        return
    p.begin_group(1, '<')
    p.pretty(klass)
    p.text(' at 0x%x' % id(obj))
    if cycle:
        p.text(' ...')
    elif p.verbose:
        first = True
        for key in dir(obj):
            if not key.startswith('_'):
                try:
                    value = getattr(obj, key)
                except AttributeError:
                    continue
                if isinstance(value, types.MethodType):
                    continue
                if not first:
                    p.text(',')
                p.breakable()
                p.text(key)
                p.text('=')
                step = len(key) + 1
                p.indentation += step
                p.pretty(value)
                p.indentation -= step
                first = False
    p.end_group(1, '>')


def _seq_pprinter_factory(start, end, basetype):
    """
    Factory that returns a pprint function useful for sequences.  Used by
    the default pprint for tuples, dicts, and lists.
    """
    def inner(obj, p, cycle):
        typ = type(obj)
        if basetype is not None and typ is not basetype and typ.__repr__ != basetype.__repr__:
            # If the subclass provides its own repr, use it instead.
            return p.text(typ.__repr__(obj))

        if cycle:
            return p.text(start + '...' + end)
        step = len(start)
        p.begin_group(step, start)
        for idx, x in p._enumerate(obj):
            if idx:
                p.text(',')
                p.breakable()
            p.pretty(x)
        if len(obj) == 1 and type(obj) is tuple:
            # Special case for 1-item tuples.
            p.text(',')
        p.end_group(step, end)
    return inner


def _set_pprinter_factory(start, end, basetype):
    """
    Factory that returns a pprint function useful for sets and frozensets.
    """
    def inner(obj, p, cycle):
        typ = type(obj)
        if basetype is not None and typ is not basetype and typ.__repr__ != basetype.__repr__:
            # If the subclass provides its own repr, use it instead.
            return p.text(typ.__repr__(obj))

        if cycle:
            return p.text(start + '...' + end)
        if len(obj) == 0:
            # Special case.
            p.text(basetype.__name__ + '()')
        else:
            step = len(start)
            p.begin_group(step, start)
            # Like dictionary keys, we will try to sort the items if there aren't too many
            items = obj
            if not (p.max_seq_length and len(obj) >= p.max_seq_length):
                try:
                    items = sorted(obj)
                except Exception:
                    # Sometimes the items don't sort.
                    pass
            for idx, x in p._enumerate(items):
                if idx:
                    p.text(',')
                    p.breakable()
                p.pretty(x)
            p.end_group(step, end)
    return inner


def _dict_pprinter_factory(start, end, basetype=None):
    """
    Factory that returns a pprint function used by the default pprint of
    dicts and dict proxies.
    """
    def inner(obj, p, cycle):
        typ = type(obj)
        if basetype is not None and typ is not basetype and typ.__repr__ != basetype.__repr__:
            # If the subclass provides its own repr, use it instead.
            return p.text(typ.__repr__(obj))

        if cycle:
            return p.text('{...}')
        p.begin_group(1, start)
        keys = obj.keys()
        # if dict isn't large enough to be truncated, sort keys before displaying
        if not (p.max_seq_length and len(obj) >= p.max_seq_length):
            try:
                keys = sorted(keys)
            except Exception:
                # Sometimes the keys don't sort.
                pass
        for idx, key in p._enumerate(keys):
            if idx:
                p.text(',')
                p.breakable()
            p.pretty(key)
            p.text(': ')
            p.pretty(obj[key])
        p.end_group(1, end)
    return inner


def _super_pprint(obj, p, cycle):
    """The pprint for the super type."""
    p.begin_group(8, '<super: ')
    p.pretty(obj.__thisclass__)
    p.text(',')
    p.breakable()
    p.pretty(obj.__self__)
    p.end_group(8, '>')


def _re_pattern_pprint(obj, p, cycle):
    """The pprint function for regular expression patterns."""
    p.text('re.compile(')
    pattern = repr(obj.pattern)
    if pattern[:1] in 'uU':
        pattern = pattern[1:]
        prefix = 'ur'
    else:
        prefix = 'r'
    pattern = prefix + pattern.replace('\\\\', '\\')
    p.text(pattern)
    if obj.flags:
        p.text(',')
        p.breakable()
        done_one = False
        for flag in ('TEMPLATE', 'IGNORECASE', 'LOCALE', 'MULTILINE', 'DOTALL',
            'UNICODE', 'VERBOSE', 'DEBUG'):
            if obj.flags & getattr(re, flag):
                if done_one:
                    p.text('|')
                p.text('re.' + flag)
                done_one = True
    p.text(')')


def _type_pprint(obj, p, cycle):
    """The pprint for classes and types."""
    # Heap allocated types might not have the module attribute,
    # and others may set it to None.

    # Checks for a __repr__ override in the metaclass
    if type(obj).__repr__ is not type.__repr__:
        _repr_pprint(obj, p, cycle)
        return

    mod = _safe_getattr(obj, '__module__', None)
    try:
        name = obj.__qualname__
        if not isinstance(name, str):
            # This can happen if the type implements __qualname__ as a property
            # or other descriptor in Python 2.
            raise Exception("Try __name__")
    except Exception:
        name = obj.__name__
        if not isinstance(name, str):
            name = '<unknown type>'

    if mod in (None, '__builtin__', 'builtins', 'exceptions'):
        p.text(name)
    else:
        p.text(mod + '.' + name)


def _repr_pprint(obj, p, cycle):
    """A pprint that just redirects to the normal repr function."""
    # Find newlines and replace them with p.break_()
    output = repr(obj)
    for idx,output_line in enumerate(output.splitlines()):
        if idx:
            p.break_()
        p.text(output_line)


def _function_pprint(obj, p, cycle):
    """Base pprint for all functions and builtin functions."""
    name = _safe_getattr(obj, '__qualname__', obj.__name__)
    mod = obj.__module__
    if mod and mod not in ('__builtin__', 'builtins', 'exceptions'):
        name = mod + '.' + name
    p.text('<function %s>' % name)


def _exception_pprint(obj, p, cycle):
    """Base pprint for all exceptions."""
    name = getattr(obj.__class__, '__qualname__', obj.__class__.__name__)
    if obj.__class__.__module__ not in ('exceptions', 'builtins'):
        name = '%s.%s' % (obj.__class__.__module__, name)
    step = len(name) + 1
    p.begin_group(step, name + '(')
    for idx, arg in enumerate(getattr(obj, 'args', ())):
        if idx:
            p.text(',')
            p.breakable()
        p.pretty(arg)
    p.end_group(step, ')')


#: the exception base
try:
    _exception_base = BaseException
except NameError:
    _exception_base = Exception


#: printers for builtin types
_type_pprinters = {
    int:                        _repr_pprint,
    float:                      _repr_pprint,
    str:                        _repr_pprint,
    tuple:                      _seq_pprinter_factory('(', ')', tuple),
    list:                       _seq_pprinter_factory('[', ']', list),
    dict:                       _dict_pprinter_factory('{', '}', dict),

    set:                        _set_pprinter_factory('{', '}', set),
    frozenset:                  _set_pprinter_factory('frozenset({', '})', frozenset),
    super:                      _super_pprint,
    _re_pattern_type:           _re_pattern_pprint,
    type:                       _type_pprint,
    types.FunctionType:         _function_pprint,
    types.BuiltinFunctionType:  _function_pprint,
    types.MethodType:           _repr_pprint,

    datetime.datetime:          _repr_pprint,
    datetime.timedelta:         _repr_pprint,
    _exception_base:            _exception_pprint
}

try:
    _type_pprinters[types.DictProxyType] = _dict_pprinter_factory('<dictproxy {', '}>')
    _type_pprinters[types.ClassType] = _type_pprint
    _type_pprinters[types.SliceType] = _repr_pprint
except AttributeError: # Python 3
    _type_pprinters[slice] = _repr_pprint

try:
    _type_pprinters[xrange] = _repr_pprint
    _type_pprinters[long] = _repr_pprint
    _type_pprinters[unicode] = _repr_pprint
except NameError:
    _type_pprinters[range] = _repr_pprint
    _type_pprinters[bytes] = _repr_pprint

#: printers for types specified by name
_deferred_type_pprinters = {
}

def for_type(typ, func):
    """
    Add a pretty printer for a given type.
    """
    oldfunc = _type_pprinters.get(typ, None)
    if func is not None:
        # To support easy restoration of old pprinters, we need to ignore Nones.
        _type_pprinters[typ] = func
    return oldfunc

def for_type_by_name(type_module, type_name, func):
    """
    Add a pretty printer for a type specified by the module and name of a type
    rather than the type object itself.
    """
    key = (type_module, type_name)
    oldfunc = _deferred_type_pprinters.get(key, None)
    if func is not None:
        # To support easy restoration of old pprinters, we need to ignore Nones.
        _deferred_type_pprinters[key] = func
    return oldfunc


#: printers for the default singletons
_singleton_pprinters = dict.fromkeys(map(id, [None, True, False, Ellipsis,
                                      NotImplemented]), _repr_pprint)


def _defaultdict_pprint(obj, p, cycle):
    name = obj.__class__.__name__
    with p.group(len(name) + 1, name + '(', ')'):
        if cycle:
            p.text('...')
        else:
            p.pretty(obj.default_factory)
            p.text(',')
            p.breakable()
            p.pretty(dict(obj))

def _ordereddict_pprint(obj, p, cycle):
    name = obj.__class__.__name__
    with p.group(len(name) + 1, name + '(', ')'):
        if cycle:
            p.text('...')
        elif len(obj):
            p.pretty(list(obj.items()))

def _deque_pprint(obj, p, cycle):
    name = obj.__class__.__name__
    with p.group(len(name) + 1, name + '(', ')'):
        if cycle:
            p.text('...')
        else:
            p.pretty(list(obj))


def _counter_pprint(obj, p, cycle):
    name = obj.__class__.__name__
    with p.group(len(name) + 1, name + '(', ')'):
        if cycle:
            p.text('...')
        elif len(obj):
            p.pretty(dict(obj))

for_type_by_name('collections', 'defaultdict', _defaultdict_pprint)
for_type_by_name('collections', 'OrderedDict', _ordereddict_pprint)
for_type_by_name('collections', 'deque', _deque_pprint)
for_type_by_name('collections', 'Counter', _counter_pprint)

if __name__ == '__main__':
    from random import randrange
    class Foo(object):
        def __init__(self):
            self.foo = 1
            self.bar = re.compile(r'\s+')
            self.blub = dict.fromkeys(range(30), randrange(1, 40))
            self.hehe = 23424.234234
            self.list = ["blub", "blah", self]

        def get_foo(self):
            print("foo")

    pprint(Foo(), verbose=True)

#
# timings
#
# -*- coding: utf-8 -*-
"""Timing related functionality for the xonsh shell.

The following time_it alias and Timer was forked from the IPython project:
* Copyright (c) 2008-2014, IPython Development Team
* Copyright (C) 2001-2007 Fernando Perez <fperez@colorado.edu>
* Copyright (c) 2001, Janko Hauser <jhauser@zscout.de>
* Copyright (c) 2001, Nathaniel Gray <n8gray@caltech.edu>
"""
gc = _LazyModule.load('gc', 'gc')
# amalgamated sys
math = _LazyModule.load('math', 'math')
# amalgamated time
timeit = _LazyModule.load('timeit', 'timeit')
# amalgamated builtins
itertools = _LazyModule.load('itertools', 'itertools')
try:
    import resource
    _HAVE_RESOURCE = True
except ImportError:
    # There is no distinction of user/system time under windows, so we
    # just use time.clock() for everything...
    resource = None
    _HAVE_RESOURCE = False

if _HAVE_RESOURCE:
    def clocku():
        """clocku() -> floating point number
        Return the *USER* CPU time in seconds since the start of the process.
        This is done via a call to resource.getrusage, so it avoids the
        wraparound problems in time.clock()."""
        return resource.getrusage(resource.RUSAGE_SELF)[0]

    def clocks():
        """clocks() -> floating point number
        Return the *SYSTEM* CPU time in seconds since the start of the process.
        This is done via a call to resource.getrusage, so it avoids the
        wraparound problems in time.clock()."""
        return resource.getrusage(resource.RUSAGE_SELF)[1]

    def clock():
        """clock() -> floating point number
        Return the *TOTAL USER+SYSTEM* CPU time in seconds since the start of
        the process.  This is done via a call to resource.getrusage, so it
        avoids the wraparound problems in time.clock()."""
        u, s = resource.getrusage(resource.RUSAGE_SELF)[:2]
        return u + s

    def clock2():
        """clock2() -> (t_user,t_system)
        Similar to clock(), but return a tuple of user/system times."""
        return resource.getrusage(resource.RUSAGE_SELF)[:2]
else:
    clocku = clocks = clock = time.clock

    def clock2():
        """Under windows, system CPU time can't be measured.
        This just returns clock() and zero."""
        return time.clock(), 0.0


def format_time(timespan, precision=3):
    """Formats the timespan in a human readable form"""
    if timespan >= 60.0:
        # we have more than a minute, format that in a human readable form
        parts = [("d", 60 * 60 * 24), ("h", 60 * 60), ("min", 60), ("s", 1)]
        time = []
        leftover = timespan
        for suffix, length in parts:
            value = int(leftover / length)
            if value > 0:
                leftover = leftover % length
                time.append('{0}{1}'.format(str(value), suffix))
            if leftover < 1:
                break
        return " ".join(time)
    # Unfortunately the unicode 'micro' symbol can cause problems in
    # certain terminals.
    # See bug: https://bugs.launchpad.net/ipython/+bug/348466
    # Try to prevent crashes by being more secure than it needs to
    # E.g. eclipse is able to print a mu, but has no sys.stdout.encoding set.
    units = ["s", "ms", 'us', "ns"]  # the save value
    if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding:
        try:
            '\xb5'.encode(sys.stdout.encoding)
            units = ["s", "ms", '\xb5s', "ns"]
        except Exception:
            pass
    scaling = [1, 1e3, 1e6, 1e9]

    if timespan > 0.0:
        order = min(-int(math.floor(math.log10(timespan)) // 3), 3)
    else:
        order = 3
    return "{1:.{0}g} {2}".format(precision, timespan * scaling[order],
                                  units[order])


class Timer(timeit.Timer):
    """Timer class that explicitly uses self.inner
    which is an undocumented implementation detail of CPython,
    not shared by PyPy.
    """
    # Timer.timeit copied from CPython 3.4.2
    def timeit(self, number=timeit.default_number):
        """Time 'number' executions of the main statement.
        To be precise, this executes the setup statement once, and
        then returns the time it takes to execute the main statement
        a number of times, as a float measured in seconds.  The
        argument is the number of times through the loop, defaulting
        to one million.  The main statement, the setup statement and
        the timer function to be used are passed to the constructor.
        """
        it = itertools.repeat(None, number)
        gcold = gc.isenabled()
        gc.disable()
        try:
            timing = self.inner(it, self.timer)
        finally:
            if gcold:
                gc.enable()
        return timing


INNER_TEMPLATE = """
def inner(_it, _timer):
    #setup
    _t0 = _timer()
    for _i in _it:
        {stmt}
    _t1 = _timer()
    return _t1 - _t0
"""


def timeit_alias(args, stdin=None):
    """Runs timing study on arguments."""
    # some real args
    number = 0
    quiet = False
    repeat = 3
    precision = 3
    # setup
    ctx = builtins.__xonsh_ctx__
    timer = Timer(timer=clock)
    stmt = ' '.join(args)
    innerstr = INNER_TEMPLATE.format(stmt=stmt)
    # Track compilation time so it can be reported if too long
    # Minimum time above which compilation time will be reported
    tc_min = 0.1
    t0 = clock()
    innercode = builtins.compilex(innerstr, filename='<xonsh-timeit>',
                                  mode='exec', glbs=ctx)
    tc = clock() - t0
    # get inner func
    ns = {}
    builtins.execx(innercode, glbs=ctx, locs=ns, mode='exec')
    timer.inner = ns['inner']
    # Check if there is a huge difference between the best and worst timings.
    worst_tuning = 0
    if number == 0:
        # determine number so that 0.2 <= total time < 2.0
        number = 1
        for _ in range(1, 10):
            time_number = timer.timeit(number)
            worst_tuning = max(worst_tuning, time_number / number)
            if time_number >= 0.2:
                break
            number *= 10
    all_runs = timer.repeat(repeat, number)
    best = min(all_runs) / number
    # print some debug info
    if not quiet:
        worst = max(all_runs) / number
        if worst_tuning:
            worst = max(worst, worst_tuning)
        # Check best timing is greater than zero to avoid a
        # ZeroDivisionError.
        # In cases where the slowest timing is lesser than 10 micoseconds
        # we assume that it does not really matter if the fastest
        # timing is 4 times faster than the slowest timing or not.
        if worst > 4 * best and best > 0 and worst > 1e-5:
            print(('The slowest run took {0:0.2f} times longer than the '
                   'fastest. This could mean that an intermediate result '
                   'is being cached.').format(worst / best))
        print("{0} loops, best of {1}: {2} per loop"
              .format(number, repeat, format_time(best, precision)))
        if tc > tc_min:
            print("Compiler time: {0:.2f} s".format(tc))
    return

#
# ansi_colors
#
"""Tools for helping with ANSI color codes."""
# amalgamated re
string = _LazyModule.load('string', 'string')
warnings = _LazyModule.load('warnings', 'warnings')
# amalgamated xonsh.lazyasd
RE_BACKGROUND = LazyObject(lambda: re.compile('(bg|bg#|bghex|background)'),
                           globals(), 'RE_BACKGROUND')


def partial_color_format(template, style='default', cmap=None, hide=False):
    """Formats a template string but only with respect to the colors.
    Another template string is returned, with the color values filled in.

    Parameters
    ----------
    template : str
        The template string, potentially with color names.
    style : str, optional
        Sytle name to look up color map from.
    cmap : dict, optional
        A color map to use, this will prevent the color map from being
        looked up via the style name.
    hide : bool, optional
        Whether to wrap the color codes in the \\001 and \\002 escape
        codes, so that the color codes are not counted against line
        length.

    Returns
    -------
    A template string with the color values filled in.
    """
    try:
        return _partial_color_format_main(template, style=style, cmap=cmap, hide=hide)
    except:
        return template


def _partial_color_format_main(template, style='default', cmap=None, hide=False):
    if cmap is not None:
        pass
    elif style in STYLES:
        cmap = STYLES[style]
    else:
        msg = 'Could not find color style {0!r}, using default.'.format(style)
        warnings.warn(msg, RuntimeWarning)
        cmap = DEFAULT_STYLE
    formatter = string.Formatter()
    esc = ('\001' if hide else '') + '\033['
    m = 'm' + ('\002' if hide else '')
    bopen = '{'
    bclose = '}'
    colon = ':'
    expl = '!'
    toks = []
    for literal, field, spec, conv in formatter.parse(template):
        toks.append(literal)
        if field is None:
            pass
        elif field in cmap:
            toks.extend([esc, cmap[field], m])
        elif '#' in field:
            field = field.lower()
            pre, _, post = field.partition('#')
            f_or_b = '38' if RE_BACKGROUND.search(pre) is None else '48'
            rgb, _, post = post.partition('_')
            c256, _ = rgb_to_256(rgb)
            color = f_or_b + ';5;' + c256
            mods = pre + '_' + post
            if 'underline' in mods:
                color = '4;' + color
            if 'bold' in mods:
                color = '1;' + color
            toks.extend([esc, color, m])
        elif field is not None:
            toks.append(bopen)
            toks.append(field)
            if conv is not None and len(conv) > 0:
                toks.append(expl)
                toks.append(conv)
            if spec is not None and len(spec) > 0:
                toks.append(colon)
                toks.append(spec)
            toks.append(bclose)
    return ''.join(toks)


RGB_256 = LazyObject(lambda: {
    '000000': '16',
    '00005f': '17',
    '000080': '04',
    '000087': '18',
    '0000af': '19',
    '0000d7': '20',
    '0000ff': '21',
    '005f00': '22',
    '005f5f': '23',
    '005f87': '24',
    '005faf': '25',
    '005fd7': '26',
    '005fff': '27',
    '008000': '02',
    '008080': '06',
    '008700': '28',
    '00875f': '29',
    '008787': '30',
    '0087af': '31',
    '0087d7': '32',
    '0087ff': '33',
    '00af00': '34',
    '00af5f': '35',
    '00af87': '36',
    '00afaf': '37',
    '00afd7': '38',
    '00afff': '39',
    '00d700': '40',
    '00d75f': '41',
    '00d787': '42',
    '00d7af': '43',
    '00d7d7': '44',
    '00d7ff': '45',
    '00ff00': '46',
    '00ff5f': '47',
    '00ff87': '48',
    '00ffaf': '49',
    '00ffd7': '50',
    '00ffff': '51',
    '080808': '232',
    '121212': '233',
    '1c1c1c': '234',
    '262626': '235',
    '303030': '236',
    '3a3a3a': '237',
    '444444': '238',
    '4e4e4e': '239',
    '585858': '240',
    '5f0000': '52',
    '5f005f': '53',
    '5f0087': '54',
    '5f00af': '55',
    '5f00d7': '56',
    '5f00ff': '57',
    '5f5f00': '58',
    '5f5f5f': '59',
    '5f5f87': '60',
    '5f5faf': '61',
    '5f5fd7': '62',
    '5f5fff': '63',
    '5f8700': '64',
    '5f875f': '65',
    '5f8787': '66',
    '5f87af': '67',
    '5f87d7': '68',
    '5f87ff': '69',
    '5faf00': '70',
    '5faf5f': '71',
    '5faf87': '72',
    '5fafaf': '73',
    '5fafd7': '74',
    '5fafff': '75',
    '5fd700': '76',
    '5fd75f': '77',
    '5fd787': '78',
    '5fd7af': '79',
    '5fd7d7': '80',
    '5fd7ff': '81',
    '5fff00': '82',
    '5fff5f': '83',
    '5fff87': '84',
    '5fffaf': '85',
    '5fffd7': '86',
    '5fffff': '87',
    '626262': '241',
    '6c6c6c': '242',
    '767676': '243',
    '800000': '01',
    '800080': '05',
    '808000': '03',
    '808080': '244',
    '870000': '88',
    '87005f': '89',
    '870087': '90',
    '8700af': '91',
    '8700d7': '92',
    '8700ff': '93',
    '875f00': '94',
    '875f5f': '95',
    '875f87': '96',
    '875faf': '97',
    '875fd7': '98',
    '875fff': '99',
    '878700': '100',
    '87875f': '101',
    '878787': '102',
    '8787af': '103',
    '8787d7': '104',
    '8787ff': '105',
    '87af00': '106',
    '87af5f': '107',
    '87af87': '108',
    '87afaf': '109',
    '87afd7': '110',
    '87afff': '111',
    '87d700': '112',
    '87d75f': '113',
    '87d787': '114',
    '87d7af': '115',
    '87d7d7': '116',
    '87d7ff': '117',
    '87ff00': '118',
    '87ff5f': '119',
    '87ff87': '120',
    '87ffaf': '121',
    '87ffd7': '122',
    '87ffff': '123',
    '8a8a8a': '245',
    '949494': '246',
    '9e9e9e': '247',
    'a8a8a8': '248',
    'af0000': '124',
    'af005f': '125',
    'af0087': '126',
    'af00af': '127',
    'af00d7': '128',
    'af00ff': '129',
    'af5f00': '130',
    'af5f5f': '131',
    'af5f87': '132',
    'af5faf': '133',
    'af5fd7': '134',
    'af5fff': '135',
    'af8700': '136',
    'af875f': '137',
    'af8787': '138',
    'af87af': '139',
    'af87d7': '140',
    'af87ff': '141',
    'afaf00': '142',
    'afaf5f': '143',
    'afaf87': '144',
    'afafaf': '145',
    'afafd7': '146',
    'afafff': '147',
    'afd700': '148',
    'afd75f': '149',
    'afd787': '150',
    'afd7af': '151',
    'afd7d7': '152',
    'afd7ff': '153',
    'afff00': '154',
    'afff5f': '155',
    'afff87': '156',
    'afffaf': '157',
    'afffd7': '158',
    'afffff': '159',
    'b2b2b2': '249',
    'bcbcbc': '250',
    'c0c0c0': '07',
    'c6c6c6': '251',
    'd0d0d0': '252',
    'd70000': '160',
    'd7005f': '161',
    'd70087': '162',
    'd700af': '163',
    'd700d7': '164',
    'd700ff': '165',
    'd75f00': '166',
    'd75f5f': '167',
    'd75f87': '168',
    'd75faf': '169',
    'd75fd7': '170',
    'd75fff': '171',
    'd78700': '172',
    'd7875f': '173',
    'd78787': '174',
    'd787af': '175',
    'd787d7': '176',
    'd787ff': '177',
    'd7af00': '178',
    'd7af5f': '179',
    'd7af87': '180',
    'd7afaf': '181',
    'd7afd7': '182',
    'd7afff': '183',
    'd7d700': '184',
    'd7d75f': '185',
    'd7d787': '186',
    'd7d7af': '187',
    'd7d7d7': '188',
    'd7d7ff': '189',
    'd7ff00': '190',
    'd7ff5f': '191',
    'd7ff87': '192',
    'd7ffaf': '193',
    'd7ffd7': '194',
    'd7ffff': '195',
    'dadada': '253',
    'e4e4e4': '254',
    'eeeeee': '255',
    'ff0000': '196',
    'ff005f': '197',
    'ff0087': '198',
    'ff00af': '199',
    'ff00d7': '200',
    'ff00ff': '201',
    'ff5f00': '202',
    'ff5f5f': '203',
    'ff5f87': '204',
    'ff5faf': '205',
    'ff5fd7': '206',
    'ff5fff': '207',
    'ff8700': '208',
    'ff875f': '209',
    'ff8787': '210',
    'ff87af': '211',
    'ff87d7': '212',
    'ff87ff': '213',
    'ffaf00': '214',
    'ffaf5f': '215',
    'ffaf87': '216',
    'ffafaf': '217',
    'ffafd7': '218',
    'ffafff': '219',
    'ffd700': '220',
    'ffd75f': '221',
    'ffd787': '222',
    'ffd7af': '223',
    'ffd7d7': '224',
    'ffd7ff': '225',
    'ffff00': '226',
    'ffff5f': '227',
    'ffff87': '228',
    'ffffaf': '229',
    'ffffd7': '230',
    'ffffff': '231',
    }, globals(), 'RGB_256')

RE_RGB3 = LazyObject(lambda: re.compile(r'(.)(.)(.)'), globals(), 'RE_RGB3')
RE_RGB6 = LazyObject(lambda: re.compile(r'(..)(..)(..)'), globals(), 'RE_RGB6')

def rgb_to_ints(rgb):
    """Converts an RGB string into a tuple of ints."""
    if len(rgb) == 6:
        return tuple([int(h, 16) for h in RE_RGB6.split(rgb)[1:4]])
    else:
        return tuple([int(h*2, 16) for h in RE_RGB3.split(rgb)[1:4]])


def rgb_to_256(rgb):
    """Find the closest ANSI 256 approximation to the given RGB value.
    Thanks to Micah Elliott (http://MicahElliott.com) for colortrans.py
    """
    rgb = rgb.lstrip('#')
    if len(rgb) == 0:
        return '0', '000000'
    incs = (0x00, 0x5f, 0x87, 0xaf, 0xd7, 0xff)
    # Break 6-char RGB code into 3 integer vals.
    parts = rgb_to_ints(rgb)
    res = []
    for part in parts:
        i = 0
        while i < len(incs)-1:
            s, b = incs[i], incs[i+1]  # smaller, bigger
            if s <= part <= b:
                s1 = abs(s - part)
                b1 = abs(b - part)
                if s1 < b1: closest = s
                else: closest = b
                res.append(closest)
                break
            i += 1
    res = ''.join([('%02.x' % i) for i in res])
    equiv = RGB_256[res]
    return equiv, res


def color_style_names():
    """Returns an iterable of all ANSI color style names."""
    return STYLES.keys()


def color_style(style='default'):
    """Returns the current color map."""
    if style in STYLES:
        cmap = STYLES[style]
    else:
        msg = 'Could not find color style {0!r}, using default.'.format(style)
        warnings.warn(msg, RuntimeWarning)
        cmap = DEFAULT_STYLE
    return cmap


def _expand_style(cmap):
    """Expands a style in order to more quickly make color map changes."""
    for key, val in list(cmap.items()):
        if key == 'NO_COLOR':
            continue
        elif len(val) == 0:
            cmap['BOLD_'+key] = '1'
            cmap['UNDERLINE_'+key] = '4'
            cmap['BOLD_UNDERLINE_'+key] = '1;4'
            cmap['BACKGROUND_'+key] = val
        else:
            cmap['BOLD_'+key] = '1;' + val
            cmap['UNDERLINE_'+key] = '4;' + val
            cmap['BOLD_UNDERLINE_'+key] = '1;4;' + val
            cmap['BACKGROUND_'+key] = val.replace('38', '48', 1)


def _bw_style():
    style = {
        'BLACK': '',
        'BLUE': '',
        'CYAN': '',
        'GREEN': '',
        'INTENSE_BLACK': '',
        'INTENSE_BLUE': '',
        'INTENSE_CYAN': '',
        'INTENSE_GREEN': '',
        'INTENSE_PURPLE': '',
        'INTENSE_RED': '',
        'INTENSE_WHITE': '',
        'INTENSE_YELLOW': '',
        'NO_COLOR': '0',
        'PURPLE': '',
        'RED': '',
        'WHITE': '',
        'YELLOW': '',
        }
    _expand_style(style)
    return style


def _default_style():
    style = {
        # Reset
        'NO_COLOR': '0',  # Text Reset
        # Regular Colors
        'BLACK': '0;30',  # BLACK
        'RED': '0;31',  # RED
        'GREEN': '0;32',  # GREEN
        'YELLOW': '0;33',  # YELLOW
        'BLUE': '0;34',  # BLUE
        'PURPLE': '0;35',  # PURPLE
        'CYAN': '0;36',  # CYAN
        'WHITE': '0;37',  # WHITE
        # Bold
        'BOLD_BLACK': '1;30',  # BLACK
        'BOLD_RED': '1;31',  # RED
        'BOLD_GREEN': '1;32',  # GREEN
        'BOLD_YELLOW': '1;33',  # YELLOW
        'BOLD_BLUE': '1;34',  # BLUE
        'BOLD_PURPLE': '1;35',  # PURPLE
        'BOLD_CYAN': '1;36',  # CYAN
        'BOLD_WHITE': '1;37',  # WHITE
        # Underline
        'UNDERLINE_BLACK': '4;30',  # BLACK
        'UNDERLINE_RED': '4;31',  # RED
        'UNDERLINE_GREEN': '4;32',  # GREEN
        'UNDERLINE_YELLOW': '4;33',  # YELLOW
        'UNDERLINE_BLUE': '4;34',  # BLUE
        'UNDERLINE_PURPLE': '4;35',  # PURPLE
        'UNDERLINE_CYAN': '4;36',  # CYAN
        'UNDERLINE_WHITE': '4;37',  # WHITE
        # Bold, Underline
        'BOLD_UNDERLINE_BLACK': '1;4;30',  # BLACK
        'BOLD_UNDERLINE_RED': '1;4;31',  # RED
        'BOLD_UNDERLINE_GREEN': '1;4;32',  # GREEN
        'BOLD_UNDERLINE_YELLOW': '1;4;33',  # YELLOW
        'BOLD_UNDERLINE_BLUE': '1;4;34',  # BLUE
        'BOLD_UNDERLINE_PURPLE': '1;4;35',  # PURPLE
        'BOLD_UNDERLINE_CYAN': '1;4;36',  # CYAN
        'BOLD_UNDERLINE_WHITE': '1;4;37',  # WHITE
        # Background
        'BACKGROUND_BLACK': '40',  # BLACK
        'BACKGROUND_RED': '41',  # RED
        'BACKGROUND_GREEN': '42',  # GREEN
        'BACKGROUND_YELLOW': '43',  # YELLOW
        'BACKGROUND_BLUE': '44',  # BLUE
        'BACKGROUND_PURPLE': '45',  # PURPLE
        'BACKGROUND_CYAN': '46',  # CYAN
        'BACKGROUND_WHITE': '47',  # WHITE
        # High Intensity
        'INTENSE_BLACK': '0;90',  # BLACK
        'INTENSE_RED': '0;91',  # RED
        'INTENSE_GREEN': '0;92',  # GREEN
        'INTENSE_YELLOW': '0;93',  # YELLOW
        'INTENSE_BLUE': '0;94',  # BLUE
        'INTENSE_PURPLE': '0;95',  # PURPLE
        'INTENSE_CYAN': '0;96',  # CYAN
        'INTENSE_WHITE': '0;97',  # WHITE
        # Bold High Intensity
        'BOLD_INTENSE_BLACK': '1;90',  # BLACK
        'BOLD_INTENSE_RED': '1;91',  # RED
        'BOLD_INTENSE_GREEN': '1;92',  # GREEN
        'BOLD_INTENSE_YELLOW': '1;93',  # YELLOW
        'BOLD_INTENSE_BLUE': '1;94',  # BLUE
        'BOLD_INTENSE_PURPLE': '1;95',  # PURPLE
        'BOLD_INTENSE_CYAN': '1;96',  # CYAN
        'BOLD_INTENSE_WHITE': '1;97',  # WHITE
        # Underline High Intensity
        'UNDERLINE_INTENSE_BLACK': '4;90',  # BLACK
        'UNDERLINE_INTENSE_RED': '4;91',  # RED
        'UNDERLINE_INTENSE_GREEN': '4;92',  # GREEN
        'UNDERLINE_INTENSE_YELLOW': '4;93',  # YELLOW
        'UNDERLINE_INTENSE_BLUE': '4;94',  # BLUE
        'UNDERLINE_INTENSE_PURPLE': '4;95',  # PURPLE
        'UNDERLINE_INTENSE_CYAN': '4;96',  # CYAN
        'UNDERLINE_INTENSE_WHITE': '4;97',  # WHITE
        # Bold Underline High Intensity
        'BOLD_UNDERLINE_INTENSE_BLACK': '1;4;90',  # BLACK
        'BOLD_UNDERLINE_INTENSE_RED': '1;4;91',  # RED
        'BOLD_UNDERLINE_INTENSE_GREEN': '1;4;92',  # GREEN
        'BOLD_UNDERLINE_INTENSE_YELLOW': '1;4;93',  # YELLOW
        'BOLD_UNDERLINE_INTENSE_BLUE': '1;4;94',  # BLUE
        'BOLD_UNDERLINE_INTENSE_PURPLE': '1;4;95',  # PURPLE
        'BOLD_UNDERLINE_INTENSE_CYAN': '1;4;96',  # CYAN
        'BOLD_UNDERLINE_INTENSE_WHITE': '1;4;97',  # WHITE
        # High Intensity backgrounds
        'BACKGROUND_INTENSE_BLACK': '0;100',  # BLACK
        'BACKGROUND_INTENSE_RED': '0;101',  # RED
        'BACKGROUND_INTENSE_GREEN': '0;102',  # GREEN
        'BACKGROUND_INTENSE_YELLOW': '0;103',  # YELLOW
        'BACKGROUND_INTENSE_BLUE': '0;104',  # BLUE
        'BACKGROUND_INTENSE_PURPLE': '0;105',  # PURPLE
        'BACKGROUND_INTENSE_CYAN': '0;106',  # CYAN
        'BACKGROUND_INTENSE_WHITE': '0;107',  # WHITE
        }
    return style

def _monokai_style():
    style = {
        'NO_COLOR': '0',
        'BLACK': '38;5;16',
        'BLUE': '38;5;63',
        'CYAN': '38;5;81',
        'GREEN': '38;5;40',
        'PURPLE': '38;5;89',
        'RED': '38;5;124',
        'WHITE': '38;5;188',
        'YELLOW': '38;5;184',
        'INTENSE_BLACK': '38;5;59',
        'INTENSE_BLUE': '38;5;20',
        'INTENSE_CYAN': '38;5;44',
        'INTENSE_GREEN': '38;5;148',
        'INTENSE_PURPLE': '38;5;141',
        'INTENSE_RED': '38;5;197',
        'INTENSE_WHITE': '38;5;15',
        'INTENSE_YELLOW': '38;5;186',
        }
    _expand_style(style)
    return style


#############################################################
#############   Auto-generated below this line   ############
#############################################################

def _algol_style():
    style = {
        'BLACK': '38;5;59',
        'BLUE': '38;5;59',
        'CYAN': '38;5;59',
        'GREEN': '38;5;59',
        'INTENSE_BLACK': '38;5;59',
        'INTENSE_BLUE': '38;5;102',
        'INTENSE_CYAN': '38;5;102',
        'INTENSE_GREEN': '38;5;102',
        'INTENSE_PURPLE': '38;5;102',
        'INTENSE_RED': '38;5;09',
        'INTENSE_WHITE': '38;5;102',
        'INTENSE_YELLOW': '38;5;102',
        'NO_COLOR': '0',
        'PURPLE': '38;5;59',
        'RED': '38;5;09',
        'WHITE': '38;5;102',
        'YELLOW': '38;5;09',
        }
    _expand_style(style)
    return style


def _algol_nu_style():
    style = {
        'BLACK': '38;5;59',
        'BLUE': '38;5;59',
        'CYAN': '38;5;59',
        'GREEN': '38;5;59',
        'INTENSE_BLACK': '38;5;59',
        'INTENSE_BLUE': '38;5;102',
        'INTENSE_CYAN': '38;5;102',
        'INTENSE_GREEN': '38;5;102',
        'INTENSE_PURPLE': '38;5;102',
        'INTENSE_RED': '38;5;09',
        'INTENSE_WHITE': '38;5;102',
        'INTENSE_YELLOW': '38;5;102',
        'NO_COLOR': '0',
        'PURPLE': '38;5;59',
        'RED': '38;5;09',
        'WHITE': '38;5;102',
        'YELLOW': '38;5;09',
        }
    _expand_style(style)
    return style

def _autumn_style():
    style = {
        'BLACK': '38;5;18',
        'BLUE': '38;5;19',
        'CYAN': '38;5;37',
        'GREEN': '38;5;34',
        'INTENSE_BLACK': '38;5;59',
        'INTENSE_BLUE': '38;5;33',
        'INTENSE_CYAN': '38;5;33',
        'INTENSE_GREEN': '38;5;64',
        'INTENSE_PURPLE': '38;5;217',
        'INTENSE_RED': '38;5;130',
        'INTENSE_WHITE': '38;5;145',
        'INTENSE_YELLOW': '38;5;217',
        'NO_COLOR': '0',
        'PURPLE': '38;5;90',
        'RED': '38;5;124',
        'WHITE': '38;5;145',
        'YELLOW': '38;5;130',
    }
    _expand_style(style)
    return style

def _borland_style():
    style = {
        'BLACK': '38;5;16',
        'BLUE': '38;5;18',
        'CYAN': '38;5;30',
        'GREEN': '38;5;28',
        'INTENSE_BLACK': '38;5;59',
        'INTENSE_BLUE': '38;5;21',
        'INTENSE_CYAN': '38;5;194',
        'INTENSE_GREEN': '38;5;102',
        'INTENSE_PURPLE': '38;5;188',
        'INTENSE_RED': '38;5;09',
        'INTENSE_WHITE': '38;5;224',
        'INTENSE_YELLOW': '38;5;188',
        'NO_COLOR': '0',
        'PURPLE': '38;5;90',
        'RED': '38;5;124',
        'WHITE': '38;5;145',
        'YELLOW': '38;5;124',
        }
    _expand_style(style)
    return style


def _colorful_style():
    style = {
        'BLACK': '38;5;16',
        'BLUE': '38;5;20',
        'CYAN': '38;5;31',
        'GREEN': '38;5;34',
        'INTENSE_BLACK': '38;5;59',
        'INTENSE_BLUE': '38;5;61',
        'INTENSE_CYAN': '38;5;145',
        'INTENSE_GREEN': '38;5;102',
        'INTENSE_PURPLE': '38;5;217',
        'INTENSE_RED': '38;5;166',
        'INTENSE_WHITE': '38;5;15',
        'INTENSE_YELLOW': '38;5;217',
        'NO_COLOR': '0',
        'PURPLE': '38;5;90',
        'RED': '38;5;124',
        'WHITE': '38;5;145',
        'YELLOW': '38;5;130',
    }
    _expand_style(style)
    return style


def _emacs_style():
    style = {
        'BLACK': '38;5;28',
        'BLUE': '38;5;18',
        'CYAN': '38;5;26',
        'GREEN': '38;5;34',
        'INTENSE_BLACK': '38;5;59',
        'INTENSE_BLUE': '38;5;26',
        'INTENSE_CYAN': '38;5;145',
        'INTENSE_GREEN': '38;5;34',
        'INTENSE_PURPLE': '38;5;129',
        'INTENSE_RED': '38;5;167',
        'INTENSE_WHITE': '38;5;145',
        'INTENSE_YELLOW': '38;5;145',
        'NO_COLOR': '0',
        'PURPLE': '38;5;90',
        'RED': '38;5;124',
        'WHITE': '38;5;145',
        'YELLOW': '38;5;130',
    }
    _expand_style(style)
    return style


def _friendly_style():
    style = {
        'BLACK': '38;5;22',
        'BLUE': '38;5;18',
        'CYAN': '38;5;31',
        'GREEN': '38;5;34',
        'INTENSE_BLACK': '38;5;59',
        'INTENSE_BLUE': '38;5;74',
        'INTENSE_CYAN': '38;5;74',
        'INTENSE_GREEN': '38;5;71',
        'INTENSE_PURPLE': '38;5;134',
        'INTENSE_RED': '38;5;167',
        'INTENSE_WHITE': '38;5;15',
        'INTENSE_YELLOW': '38;5;145',
        'NO_COLOR': '0',
        'PURPLE': '38;5;90',
        'RED': '38;5;124',
        'WHITE': '38;5;145',
        'YELLOW': '38;5;166',
    }
    _expand_style(style)
    return style


def _fruity_style():
    style = {
        'BLACK': '38;5;16',
        'BLUE': '38;5;32',
        'CYAN': '38;5;32',
        'GREEN': '38;5;28',
        'INTENSE_BLACK': '38;5;59',
        'INTENSE_BLUE': '38;5;33',
        'INTENSE_CYAN': '38;5;33',
        'INTENSE_GREEN': '38;5;102',
        'INTENSE_PURPLE': '38;5;198',
        'INTENSE_RED': '38;5;202',
        'INTENSE_WHITE': '38;5;15',
        'INTENSE_YELLOW': '38;5;187',
        'NO_COLOR': '0',
        'PURPLE': '38;5;198',
        'RED': '38;5;09',
        'WHITE': '38;5;187',
        'YELLOW': '38;5;202',
        }
    _expand_style(style)
    return style


def _igor_style():
    style = {
        'BLACK': '38;5;34',
        'BLUE': '38;5;21',
        'CYAN': '38;5;30',
        'GREEN': '38;5;34',
        'INTENSE_BLACK': '38;5;30',
        'INTENSE_BLUE': '38;5;21',
        'INTENSE_CYAN': '38;5;30',
        'INTENSE_GREEN': '38;5;34',
        'INTENSE_PURPLE': '38;5;163',
        'INTENSE_RED': '38;5;166',
        'INTENSE_WHITE': '38;5;163',
        'INTENSE_YELLOW': '38;5;166',
        'NO_COLOR': '0',
        'PURPLE': '38;5;163',
        'RED': '38;5;166',
        'WHITE': '38;5;163',
        'YELLOW': '38;5;166',
        }
    _expand_style(style)
    return style

def _lovelace_style():
    style = {
        'BLACK': '38;5;59',
        'BLUE': '38;5;25',
        'CYAN': '38;5;29',
        'GREEN': '38;5;65',
        'INTENSE_BLACK': '38;5;59',
        'INTENSE_BLUE': '38;5;25',
        'INTENSE_CYAN': '38;5;102',
        'INTENSE_GREEN': '38;5;29',
        'INTENSE_PURPLE': '38;5;133',
        'INTENSE_RED': '38;5;131',
        'INTENSE_WHITE': '38;5;102',
        'INTENSE_YELLOW': '38;5;136',
        'NO_COLOR': '0',
        'PURPLE': '38;5;133',
        'RED': '38;5;124',
        'WHITE': '38;5;102',
        'YELLOW': '38;5;130',
        }
    _expand_style(style)
    return style


def _manni_style():
    style = {
        'BLACK': '38;5;16',
        'BLUE': '38;5;18',
        'CYAN': '38;5;30',
        'GREEN': '38;5;40',
        'INTENSE_BLACK': '38;5;59',
        'INTENSE_BLUE': '38;5;105',
        'INTENSE_CYAN': '38;5;45',
        'INTENSE_GREEN': '38;5;113',
        'INTENSE_PURPLE': '38;5;165',
        'INTENSE_RED': '38;5;202',
        'INTENSE_WHITE': '38;5;224',
        'INTENSE_YELLOW': '38;5;221',
        'NO_COLOR': '0',
        'PURPLE': '38;5;165',
        'RED': '38;5;124',
        'WHITE': '38;5;145',
        'YELLOW': '38;5;166',
        }
    _expand_style(style)
    return style


def _murphy_style():
    style = {
        'BLACK': '38;5;16',
        'BLUE': '38;5;18',
        'CYAN': '38;5;31',
        'GREEN': '38;5;34',
        'INTENSE_BLACK': '38;5;59',
        'INTENSE_BLUE': '38;5;63',
        'INTENSE_CYAN': '38;5;86',
        'INTENSE_GREEN': '38;5;86',
        'INTENSE_PURPLE': '38;5;213',
        'INTENSE_RED': '38;5;209',
        'INTENSE_WHITE': '38;5;15',
        'INTENSE_YELLOW': '38;5;222',
        'NO_COLOR': '0',
        'PURPLE': '38;5;90',
        'RED': '38;5;124',
        'WHITE': '38;5;145',
        'YELLOW': '38;5;166',
        }
    _expand_style(style)
    return style


def _native_style():
    style = {
        'BLACK': '38;5;52',
        'BLUE': '38;5;67',
        'CYAN': '38;5;31',
        'GREEN': '38;5;64',
        'INTENSE_BLACK': '38;5;59',
        'INTENSE_BLUE': '38;5;68',
        'INTENSE_CYAN': '38;5;87',
        'INTENSE_GREEN': '38;5;70',
        'INTENSE_PURPLE': '38;5;188',
        'INTENSE_RED': '38;5;160',
        'INTENSE_WHITE': '38;5;15',
        'INTENSE_YELLOW': '38;5;214',
        'NO_COLOR': '0',
        'PURPLE': '38;5;59',
        'RED': '38;5;124',
        'WHITE': '38;5;145',
        'YELLOW': '38;5;124',
        }
    _expand_style(style)
    return style

def _paraiso_dark_style():
    style = {
        'BLACK': '38;5;95',
        'BLUE': '38;5;97',
        'CYAN': '38;5;39',
        'GREEN': '38;5;72',
        'INTENSE_BLACK': '38;5;95',
        'INTENSE_BLUE': '38;5;97',
        'INTENSE_CYAN': '38;5;79',
        'INTENSE_GREEN': '38;5;72',
        'INTENSE_PURPLE': '38;5;188',
        'INTENSE_RED': '38;5;203',
        'INTENSE_WHITE': '38;5;188',
        'INTENSE_YELLOW': '38;5;220',
        'NO_COLOR': '0',
        'PURPLE': '38;5;97',
        'RED': '38;5;203',
        'WHITE': '38;5;79',
        'YELLOW': '38;5;214',
        }
    _expand_style(style)
    return style


def _paraiso_light_style():
    style = {
        'BLACK': '38;5;16',
        'BLUE': '38;5;16',
        'CYAN': '38;5;39',
        'GREEN': '38;5;72',
        'INTENSE_BLACK': '38;5;16',
        'INTENSE_BLUE': '38;5;97',
        'INTENSE_CYAN': '38;5;79',
        'INTENSE_GREEN': '38;5;72',
        'INTENSE_PURPLE': '38;5;97',
        'INTENSE_RED': '38;5;203',
        'INTENSE_WHITE': '38;5;79',
        'INTENSE_YELLOW': '38;5;220',
        'NO_COLOR': '0',
        'PURPLE': '38;5;97',
        'RED': '38;5;16',
        'WHITE': '38;5;102',
        'YELLOW': '38;5;214',
        }
    _expand_style(style)
    return style

def _pastie_style():
    style = {
        'BLACK': '38;5;16',
        'BLUE': '38;5;20',
        'CYAN': '38;5;25',
        'GREEN': '38;5;28',
        'INTENSE_BLACK': '38;5;59',
        'INTENSE_BLUE': '38;5;61',
        'INTENSE_CYAN': '38;5;194',
        'INTENSE_GREEN': '38;5;34',
        'INTENSE_PURPLE': '38;5;188',
        'INTENSE_RED': '38;5;172',
        'INTENSE_WHITE': '38;5;15',
        'INTENSE_YELLOW': '38;5;188',
        'NO_COLOR': '0',
        'PURPLE': '38;5;125',
        'RED': '38;5;124',
        'WHITE': '38;5;145',
        'YELLOW': '38;5;130',
        }
    _expand_style(style)
    return style


def _perldoc_style():
    style = {
        'BLACK': '38;5;18',
        'BLUE': '38;5;18',
        'CYAN': '38;5;31',
        'GREEN': '38;5;34',
        'INTENSE_BLACK': '38;5;59',
        'INTENSE_BLUE': '38;5;134',
        'INTENSE_CYAN': '38;5;145',
        'INTENSE_GREEN': '38;5;28',
        'INTENSE_PURPLE': '38;5;134',
        'INTENSE_RED': '38;5;167',
        'INTENSE_WHITE': '38;5;188',
        'INTENSE_YELLOW': '38;5;188',
        'NO_COLOR': '0',
        'PURPLE': '38;5;90',
        'RED': '38;5;124',
        'WHITE': '38;5;145',
        'YELLOW': '38;5;166',
        }
    _expand_style(style)
    return style

def _rrt_style():
    style = {
        'BLACK': '38;5;09',
        'BLUE': '38;5;117',
        'CYAN': '38;5;117',
        'GREEN': '38;5;46',
        'INTENSE_BLACK': '38;5;117',
        'INTENSE_BLUE': '38;5;117',
        'INTENSE_CYAN': '38;5;122',
        'INTENSE_GREEN': '38;5;46',
        'INTENSE_PURPLE': '38;5;213',
        'INTENSE_RED': '38;5;09',
        'INTENSE_WHITE': '38;5;188',
        'INTENSE_YELLOW': '38;5;222',
        'NO_COLOR': '0',
        'PURPLE': '38;5;213',
        'RED': '38;5;09',
        'WHITE': '38;5;117',
        'YELLOW': '38;5;09',
        }
    _expand_style(style)
    return style


def _tango_style():
    style = {
        'BLACK': '38;5;16',
        'BLUE': '38;5;20',
        'CYAN': '38;5;61',
        'GREEN': '38;5;34',
        'INTENSE_BLACK': '38;5;24',
        'INTENSE_BLUE': '38;5;62',
        'INTENSE_CYAN': '38;5;15',
        'INTENSE_GREEN': '38;5;64',
        'INTENSE_PURPLE': '38;5;15',
        'INTENSE_RED': '38;5;09',
        'INTENSE_WHITE': '38;5;15',
        'INTENSE_YELLOW': '38;5;178',
        'NO_COLOR': '0',
        'PURPLE': '38;5;90',
        'RED': '38;5;124',
        'WHITE': '38;5;15',
        'YELLOW': '38;5;94',
        }
    _expand_style(style)
    return style


def _trac_style():
    style = {
        'BLACK': '38;5;16',
        'BLUE': '38;5;18',
        'CYAN': '38;5;30',
        'GREEN': '38;5;100',
        'INTENSE_BLACK': '38;5;59',
        'INTENSE_BLUE': '38;5;60',
        'INTENSE_CYAN': '38;5;194',
        'INTENSE_GREEN': '38;5;102',
        'INTENSE_PURPLE': '38;5;188',
        'INTENSE_RED': '38;5;137',
        'INTENSE_WHITE': '38;5;224',
        'INTENSE_YELLOW': '38;5;188',
        'NO_COLOR': '0',
        'PURPLE': '38;5;90',
        'RED': '38;5;124',
        'WHITE': '38;5;145',
        'YELLOW': '38;5;100',
        }
    _expand_style(style)
    return style


def _vim_style():
    style = {
        'BLACK': '38;5;18',
        'BLUE': '38;5;18',
        'CYAN': '38;5;44',
        'GREEN': '38;5;40',
        'INTENSE_BLACK': '38;5;60',
        'INTENSE_BLUE': '38;5;68',
        'INTENSE_CYAN': '38;5;44',
        'INTENSE_GREEN': '38;5;40',
        'INTENSE_PURPLE': '38;5;164',
        'INTENSE_RED': '38;5;09',
        'INTENSE_WHITE': '38;5;188',
        'INTENSE_YELLOW': '38;5;184',
        'NO_COLOR': '0',
        'PURPLE': '38;5;164',
        'RED': '38;5;160',
        'WHITE': '38;5;188',
        'YELLOW': '38;5;160',
        }
    _expand_style(style)
    return style


def _vs_style():
    style = {
        'BLACK': '38;5;28',
        'BLUE': '38;5;21',
        'CYAN': '38;5;31',
        'GREEN': '38;5;28',
        'INTENSE_BLACK': '38;5;31',
        'INTENSE_BLUE': '38;5;31',
        'INTENSE_CYAN': '38;5;31',
        'INTENSE_GREEN': '38;5;31',
        'INTENSE_PURPLE': '38;5;31',
        'INTENSE_RED': '38;5;09',
        'INTENSE_WHITE': '38;5;31',
        'INTENSE_YELLOW': '38;5;31',
        'NO_COLOR': '0',
        'PURPLE': '38;5;124',
        'RED': '38;5;124',
        'WHITE': '38;5;31',
        'YELLOW': '38;5;124',
        }
    _expand_style(style)
    return style


def _xcode_style():
    style = {
        'BLACK': '38;5;16',
        'BLUE': '38;5;20',
        'CYAN': '38;5;60',
        'GREEN': '38;5;28',
        'INTENSE_BLACK': '38;5;60',
        'INTENSE_BLUE': '38;5;20',
        'INTENSE_CYAN': '38;5;60',
        'INTENSE_GREEN': '38;5;60',
        'INTENSE_PURPLE': '38;5;126',
        'INTENSE_RED': '38;5;160',
        'INTENSE_WHITE': '38;5;60',
        'INTENSE_YELLOW': '38;5;94',
        'NO_COLOR': '0',
        'PURPLE': '38;5;126',
        'RED': '38;5;160',
        'WHITE': '38;5;60',
        'YELLOW': '38;5;94',
        }
    _expand_style(style)
    return style


STYLES = LazyDict({
    'algol': _algol_style,
    'algol_nu': _algol_nu_style,
    'autumn': _autumn_style,
    'borland': _borland_style,
    'bw': _bw_style,
    'colorful': _colorful_style,
    'default': _default_style,
    'emacs': _emacs_style,
    'friendly': _friendly_style,
    'fruity': _fruity_style,
    'igor': _igor_style,
    'lovelace': _lovelace_style,
    'manni': _manni_style,
    'monokai': _monokai_style,
    'murphy': _murphy_style,
    'native': _native_style,
    'paraiso-dark': _paraiso_dark_style,
    'paraiso-light': _paraiso_light_style,
    'pastie': _pastie_style,
    'perldoc': _perldoc_style,
    'rrt': _rrt_style,
    'tango': _tango_style,
    'trac': _trac_style,
    'vim': _vim_style,
    'vs': _vs_style,
    'xcode': _xcode_style,
    }, globals(), 'STYLES')

del (_algol_style, _algol_nu_style, _autumn_style, _borland_style, _bw_style,
     _colorful_style, _default_style, _emacs_style, _friendly_style,
     _fruity_style, _igor_style, _lovelace_style, _manni_style,
     _monokai_style, _murphy_style, _native_style, _paraiso_dark_style,
     _paraiso_light_style, _pastie_style, _perldoc_style,  _rrt_style,
     _tango_style, _trac_style, _vim_style, _vs_style, _xcode_style)

#
# codecache
#
# amalgamated os
# amalgamated sys
hashlib = _LazyModule.load('hashlib', 'hashlib')
marshal = _LazyModule.load('marshal', 'marshal')
# amalgamated builtins
# amalgamated xonsh.lazyasd
def _splitpath(path, sofar=[]):
    folder, path = os.path.split(path)
    if path == "":
        return sofar[::-1]
    elif folder == "":
        return (sofar + [path])[::-1]
    else:
        return _splitpath(folder, sofar + [path])


def _character_map():
    cmap = {chr(o): '_%s' % chr(o+32) for o in range(65, 91)}
    cmap.update({'.': '_.', '_': '__'})
    return cmap


_CHARACTER_MAP = LazyObject(_character_map, globals(), '_CHARACTER_MAP')
del _character_map


def _cache_renamer(path, code=False):
    if not code:
        path = os.path.abspath(path)
    o = [''.join(_CHARACTER_MAP.get(i, i) for i in w) for w in _splitpath(path)]
    o[-1] = "{}.{}".format(o[-1], sys.implementation.cache_tag)
    return o


def _make_if_not_exists(dirname):
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

def should_use_cache(execer, mode):
    """
    Return ``True`` if caching has been enabled for this mode (through command
    line flags or environment variables)
    """
    if mode == 'exec':
        return ((execer.scriptcache or
                    execer.cacheall) and
                (builtins.__xonsh_env__['XONSH_CACHE_SCRIPTS'] or
                    builtins.__xonsh_env__['XONSH_CACHE_EVERYTHING']))
    else:
        return (execer.cacheall or
                builtins.__xonsh_env__['XONSH_CACHE_EVERYTHING'])


def run_compiled_code(code, glb, loc, mode):
    """
    Helper to run code in a given mode and context
    """
    if code is None:
        return
    if mode in {'exec', 'single'}:
        func = exec
    else:
        func = eval
    func(code, glb, loc)


def get_cache_filename(fname, code=True):
    """
    Return the filename of the cache for the given filename.

    Cache filenames are similar to those used by the Mercurial DVCS for its
    internal store.

    The ``code`` switch should be true if we should use the code store rather
    than the script store.
    """
    datadir = builtins.__xonsh_env__['XONSH_DATA_DIR']
    cachedir = os.path.join(datadir, 'xonsh_code_cache' if code else 'xonsh_script_cache')
    cachefname = os.path.join(cachedir, *_cache_renamer(fname, code=code))
    return cachefname


def update_cache(ccode, cache_file_name):
    """
    Update the cache at ``cache_file_name`` to contain the compiled code
    represented by ``ccode``.
    """
    if cache_file_name is not None:
        _make_if_not_exists(os.path.dirname(cache_file_name))
        with open(cache_file_name, 'wb') as cfile:
            marshal.dump(ccode, cfile)


def compile_code(filename, code, execer, glb, loc, mode):
    """
    Wrapper for ``execer.compile`` to compile the given code
    """
    try:
        if not code.endswith('\n'):
            code += '\n'
        old_filename = execer.filename
        execer.filename = filename
        ccode = execer.compile(code, glbs=glb, locs=loc, mode=mode)
    except:
        raise
    finally:
        execer.filename = old_filename
    return ccode


def script_cache_check(filename, cachefname):
    """
    Check whether the script cache for a particular file is valid.

    Returns a tuple containing: a boolean representing whether the cached code
    should be used, and the cached code (or ``None`` if the cache should not be
    used).
    """
    ccode = None
    run_cached = False
    if os.path.isfile(cachefname):
        if os.stat(cachefname).st_mtime >= os.stat(filename).st_mtime:
            with open(cachefname, 'rb') as cfile:
                ccode = marshal.load(cfile)
                run_cached = True
    return run_cached, ccode


def run_script_with_cache(filename, execer, glb=None, loc=None, mode='exec'):
    """
    Run a script, using a cached version if it exists (and the source has not
    changed), and updating the cache as necessary.
    """
    run_cached = False
    use_cache = should_use_cache(execer, mode)
    if use_cache:
        cachefname = get_cache_filename(filename, code=False)
        run_cached, ccode = script_cache_check(filename, cachefname)
    if not run_cached:
        with open(filename, 'r') as f:
            code = f.read()
        ccode = compile_code(filename, code, execer, glb, loc, mode)
        update_cache(ccode, cachefname)
    run_compiled_code(ccode, glb, loc, mode)


def code_cache_name(code):
    """
    Return an appropriate spoofed filename for the given code.
    """
    if isinstance(code, str):
        _code = code.encode()
    else:
        _code = code
    return hashlib.md5(_code).hexdigest()


def code_cache_check(cachefname):
    """
    Check whether the code cache for a particular piece of code is valid.

    Returns a tuple containing: a boolean representing whether the cached code
    should be used, and the cached code (or ``None`` if the cache should not be
    used).
    """
    ccode = None
    run_cached = False
    if os.path.isfile(cachefname):
        with open(cachefname, 'rb') as cfile:
            ccode = marshal.load(cfile)
            run_cached = True
    return run_cached, ccode


def run_code_with_cache(code, execer, glb=None, loc=None, mode='exec'):
    """
    Run a piece of code, using a cached version if it exists, and updating the
    cache as necessary.
    """
    use_cache = should_use_cache(execer, mode)
    filename = code_cache_name(code)
    cachefname = get_cache_filename(filename, code=True)
    run_cached = False
    if use_cache:
        run_cached, ccode = code_cache_check(cachefname)
    if not run_cached:
        ccode = compile_code(filename, code, execer, glb, loc, mode)
        update_cache(ccode, cachefname)
    run_compiled_code(ccode, glb, loc, mode)

#
# openpy
#
# -*- coding: utf-8 -*-
"""Tools to open ``*.py`` files as Unicode.

Uses the encoding specified within the file, as per PEP 263.

Much of the code is taken from the tokenize module in Python 3.2.

This file was forked from the IPython project:

* Copyright (c) 2008-2014, IPython Development Team
* Copyright (C) 2001-2007 Fernando Perez <fperez@colorado.edu>
* Copyright (c) 2001, Janko Hauser <jhauser@zscout.de>
* Copyright (c) 2001, Nathaniel Gray <n8gray@caltech.edu>
"""
# amalgamated io
# amalgamated os
# amalgamated re
tokenize = _LazyModule.load('tokenize', 'tokenize')
# amalgamated xonsh.lazyasd
cookie_comment_re = LazyObject(
    lambda: re.compile(r"^\s*#.*coding[:=]\s*([-\w.]+)", re.UNICODE),
    globals(), 'cookie_comment_re')

def source_to_unicode(txt, errors='replace', skip_encoding_cookie=True):
    """Converts a bytes string with python source code to unicode.

    Unicode strings are passed through unchanged. Byte strings are checked
    for the python source file encoding cookie to determine encoding.
    txt can be either a bytes buffer or a string containing the source
    code.
    """
    if isinstance(txt, str):
        return txt
    if isinstance(txt, bytes):
        buf = io.BytesIO(txt)
    else:
        buf = txt
    try:
        encoding, _ = tokenize.detect_encoding(buf.readline)
    except SyntaxError:
        encoding = "ascii"
    buf.seek(0)
    text = io.TextIOWrapper(buf, encoding, errors=errors, line_buffering=True)
    text.mode = 'r'
    if skip_encoding_cookie:
        return u"".join(strip_encoding_cookie(text))
    else:
        return text.read()


def strip_encoding_cookie(filelike):
    """Generator to pull lines from a text-mode file, skipping the encoding
    cookie if it is found in the first two lines.
    """
    it = iter(filelike)
    try:
        first = next(it)
        if not cookie_comment_re.match(first):
            yield first
        second = next(it)
        if not cookie_comment_re.match(second):
            yield second
    except StopIteration:
        return

    for line in it:
        yield line


def read_py_file(filename, skip_encoding_cookie=True):
    """Read a Python file, using the encoding declared inside the file.

    Parameters
    ----------
    filename : str
      The path to the file to read.
    skip_encoding_cookie : bool
      If True (the default), and the encoding declaration is found in the first
      two lines, that line will be excluded from the output - compiling a
      unicode string with an encoding declaration is a SyntaxError in Python 2.

    Returns
    -------
    A unicode string containing the contents of the file.
    """
    with tokenize.tokopen(filename) as f:  # the open function defined in this module.
        if skip_encoding_cookie:
            return "".join(strip_encoding_cookie(f))
        else:
            return f.read()


def read_py_url(url, errors='replace', skip_encoding_cookie=True):
    """Read a Python file from a URL, using the encoding declared inside the file.

    Parameters
    ----------
    url : str
      The URL from which to fetch the file.
    errors : str
      How to handle decoding errors in the file. Options are the same as for
      bytes.decode(), but here 'replace' is the default.
    skip_encoding_cookie : bool
      If True (the default), and the encoding declaration is found in the first
      two lines, that line will be excluded from the output - compiling a
      unicode string with an encoding declaration is a SyntaxError in Python 2.

    Returns
    -------
    A unicode string containing the contents of the file.
    """
    # Deferred import for faster start
    try:
        from urllib.request import urlopen  # Py 3
    except ImportError:
        from urllib import urlopen
    response = urlopen(url)
    buf = io.BytesIO(response.read())
    return source_to_unicode(buf, errors, skip_encoding_cookie)


def _list_readline(x):
    """Given a list, returns a readline() function that returns the next element
    with each call.
    """
    x = iter(x)

    def readline():
        return next(x)

    return readline

#
# platform
#
"""Module for platform-specific constants and implementations, as well as
compatibility layers to make use of the 'best' implementation available
on a platform.
"""
# amalgamated os
# amalgamated sys
pathlib = _LazyModule.load('pathlib', 'pathlib')
platform = _LazyModule.load('platform', 'platform')
functools = _LazyModule.load('functools', 'functools')
subprocess = _LazyModule.load('subprocess', 'subprocess')
# amalgamated importlib.util
# amalgamated xonsh.lazyasd
def _distro():
    try:
        import distro as d
    except ImportError:
        d = None
    except:
        raise
    return d


distro = LazyObject(_distro, globals(), 'distro')
del _distro

# do not import any xonsh-modules here to avoid circular dependencies


#
# OS
#
ON_DARWIN = LazyBool(lambda: platform.system() == 'Darwin',
                     globals(), 'ON_DARWIN')
""" ``True`` if executed on a Darwin platform, else ``False``. """
ON_LINUX = LazyBool(lambda: platform.system() == 'Linux',
                    globals(), 'ON_LINUX')
""" ``True`` if executed on a Linux platform, else ``False``. """
ON_WINDOWS = LazyBool(lambda: platform.system() == 'Windows',
                      globals(), 'ON_WINDOWS')
""" ``True`` if executed on a native Windows platform, else ``False``. """
ON_CYGWIN = LazyBool(lambda: sys.platform == 'cygwin', globals(), 'ON_CYGWIN')
""" ``True`` if executed on a Cygwin Windows platform, else ``False``. """
ON_POSIX = LazyBool(lambda: (os.name == 'posix'), globals(), 'ON_POSIX')
""" ``True`` if executed on a POSIX-compliant platform, else ``False``. """


#
# Python & packages
#

PYTHON_VERSION_INFO = sys.version_info[:3]
""" Version of Python interpreter as three-value tuple. """
ON_ANACONDA = LazyBool(
    lambda: any(s in sys.version for s in {'Anaconda', 'Continuum'}),
    globals(), 'ON_ANACONDA')
""" ``True`` if executed in an Anaconda instance, else ``False``. """

def _has_pygments():
    spec = importlib.util.find_spec('pygments')
    return (spec is not None)


HAS_PYGMENTS = LazyBool(_has_pygments, globals(), 'HAS_PYGMENTS')
""" ``True`` if `pygments` is available, else ``False``. """
del _has_pygments


@functools.lru_cache(1)
def pygments_version():
    """pygments.__version__ version if available, else None."""
    if HAS_PYGMENTS:
        import pygments
        v = pygments.__version__
    else:
        v = None
    return v


@functools.lru_cache(1)
def has_prompt_toolkit():
    """ Tests if the `prompt_toolkit` is available. """
    spec = importlib.util.find_spec('prompt_toolkit')
    return (spec is not None)


@functools.lru_cache(1)
def ptk_version():
    """ Returns `prompt_toolkit.__version__` if available, else ``None``. """
    if has_prompt_toolkit():
        import prompt_toolkit
        return getattr(prompt_toolkit, '__version__', '<0.57')
    else:
        return None


@functools.lru_cache(1)
def ptk_version_info():
    """ Returns `prompt_toolkit`'s version as tuple of integers. """
    if has_prompt_toolkit():
        return tuple(int(x) for x in ptk_version().strip('<>+-=.').split('.'))
    else:
        return None


@functools.lru_cache(1)
def ptk_version_is_supported():
    minimum_required_ptk_version = (1, 0)
    return ptk_version_info()[:2] >= minimum_required_ptk_version


@functools.lru_cache(1)
def best_shell_type():
    if ON_WINDOWS or has_prompt_toolkit():
        return 'prompt_toolkit'
    else:
        return 'readline'


@functools.lru_cache(1)
def is_readline_available():
    """Checks if readline is available to import."""
    spec = importlib.util.find_spec('readline')
    return (spec is not None)


#
# Dev release info
#

@functools.lru_cache(1)
def githash():
    install_base = os.path.dirname(__file__)
    try:
        with open('{}/dev.githash'.format(install_base), 'r') as f:
            sha = f.read().strip()
        if not sha:
            sha = None
    except FileNotFoundError:
        sha = None
    return sha


#
# Encoding
#

DEFAULT_ENCODING = sys.getdefaultencoding()
""" Default string encoding. """


if PYTHON_VERSION_INFO < (3, 5, 0):
    class DirEntry:
        def __init__(self, directory, name):
            self.__path__ = pathlib.Path(directory) / name
            self.name = name
            self.path = str(self.__path__)
            self.is_symlink = self.__path__.is_symlink

        def inode(self):
            return os.stat(self.path, follow_symlinks=False).st_ino

        def is_dir(self, *, follow_symlinks=True):
            if follow_symlinks:
                return self.__path__.is_dir()
            else:
                return not self.__path__.is_symlink() \
                       and self.__path__.is_dir()

        def is_file(self, *, follow_symlinks=True):
            if follow_symlinks:
                return self.__path__.is_file()
            else:
                return not self.__path__.is_symlink() \
                       and self.__path__.is_file()

        def stat(self, *, follow_symlinks=True):
            return os.stat(self.path, follow_symlinks=follow_symlinks)

    def scandir(path):
        """ Compatibility layer for  `os.scandir` from Python 3.5+. """
        return (DirEntry(path, x) for x in os.listdir(path))
else:
    scandir = os.scandir


#
# Linux distro
#

@functools.lru_cache(1)
def linux_distro():
    """The id of the Linux distribution running on, possibly 'unknown'.
    None on non-Linux platforms.
    """
    if ON_LINUX:
        if distro:
            ld = distro.id()
        elif PYTHON_VERSION_INFO < (3, 7, 0):
            ld = platform.linux_distribution()[0] or 'unknown'
        elif '-ARCH-' in platform.platform():
            ld = 'arch'  # that's the only one we need to know for now
        else:
            ld = 'unknown'
    else:
        ld = None
    return ld


#
# Windows
#

@functools.lru_cache(1)
def git_for_windows_path():
    """Returns the path to git for windows, if available and None otherwise."""
    import winreg
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             'SOFTWARE\\GitForWindows')
        gfwp, _ = winreg.QueryValueEx(key, "InstallPath")
    except FileNotFoundError:
        gfwp = None
    return gfwp


@functools.lru_cache(1)
def windows_bash_command():
    """Determines teh command for Bash on windows."""
    import winreg
    # Check that bash is on path otherwise try the default directory
    # used by Git for windows
    wbc = 'bash'
    try:
        subprocess.check_call([wbc, '--version'],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    except (FileNotFoundError, subprocess.CalledProcessError):
        gfwp = git_for_windows_path()
        if gfwp:
            bashcmd = os.path.join(gfwp, 'bin\\bash.exe')
            if os.path.isfile(bashcmd):
                wbc = bashcmd
    return wbc

#
# Environment variables defaults
#

def _bcd():
    """A possibly empty tuple with default paths to Bash completions known for
    the current platform.
    """
    if ON_LINUX or ON_CYGWIN:
        if linux_distro() == 'arch':
            bcd = (
                '/usr/share/bash-completion/bash_completion',
                '/usr/share/bash-completion/completions')
        else:
            bcd = ('/usr/share/bash-completion',
                   '/usr/share/bash-completion/completions')
    elif ON_DARWIN:
        bcd = ('/usr/local/etc/bash_completion',
               '/opt/local/etc/profile.d/bash_completion.sh')
    elif ON_WINDOWS and git_for_windows_path():
        bcd = (os.path.join(git_for_windows_path(),
                    'usr\\share\\bash-completion'),
               os.path.join(git_for_windows_path(),
                    'usr\\share\\bash-completion\\completions'),
               os.path.join(git_for_windows_path(),
                     'mingw64\\share\\git\\completion\\git-completion.bash'))
    else:
        bcd = ()
    return bcd


BASH_COMPLETIONS_DEFAULT = LazyObject(_bcd, globals(),
                                      'BASH_COMPLETIONS_DEFAULT')
del _bcd


def _pd():
    if ON_LINUX or ON_CYGWIN:
        if linux_distro() == 'arch':
            pd = ('/usr/local/sbin',
                  '/usr/local/bin', '/usr/bin', '/usr/bin/site_perl',
                  '/usr/bin/vendor_perl', '/usr/bin/core_perl')
        else:
            pd = (os.path.expanduser('~/bin'), '/usr/local/sbin',
                  '/usr/local/bin', '/usr/sbin', '/usr/bin', '/sbin', '/bin',
                  '/usr/games', '/usr/local/games')
    elif ON_DARWIN:
        pd = ('/usr/local/bin', '/usr/bin', '/bin', '/usr/sbin', '/sbin')
    elif ON_WINDOWS:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment')
        pd = tuple(winreg.QueryValueEx(key, 'Path')[0].split(os.pathsep))
    else:
        pd = ()
    return pd

PATH_DEFAULT = LazyObject(_pd, globals(), 'PATH_DEFAULT')
del _pd

#
# teepty
#
# -*- coding: utf-8 -*-
"""This implements a psuedo-TTY that tees its output into a Python buffer.

This file was forked from a version distibuted under an MIT license and
Copyright (c) 2011 Joshua D. Bartlett.
See http://sqizit.bartletts.id.au/2011/02/14/pseudo-terminals-in-python/ for
more information.
"""
# amalgamated io
# amalgamated re
# amalgamated os
# amalgamated sys
tty = _LazyModule.load('tty', 'tty')
pty = _LazyModule.load('pty', 'pty')
# amalgamated time
array = _LazyModule.load('array', 'array')
fcntl = _LazyModule.load('fcntl', 'fcntl')
select = _LazyModule.load('select', 'select')
signal = _LazyModule.load('signal', 'signal')
termios = _LazyModule.load('termios', 'termios')
tempfile = _LazyModule.load('tempfile', 'tempfile')
# amalgamated threading
# amalgamated xonsh.lazyasd
MODE_NUMS = ('1049', '47', '1047')
START_ALTERNATE_MODE = frozenset('\x1b[?{0}h'.format(i).encode() for i in MODE_NUMS)
END_ALTERNATE_MODE = frozenset('\x1b[?{0}l'.format(i).encode() for i in MODE_NUMS)
ALTERNATE_MODE_FLAGS = tuple(START_ALTERNATE_MODE) + tuple(END_ALTERNATE_MODE)

RE_HIDDEN = LazyObject(lambda: re.compile(b'(\001.*?\002)'),
                       globals(), 'RE_HIDDEN')
RE_COLOR = LazyObject(lambda: re.compile(b'\033\[\d+;?\d*m'),
                      globals(), 'RE_COLOR')

def _findfirst(s, substrs):
    """Finds whichever of the given substrings occurs first in the given string
    and returns that substring, or returns None if no such strings occur.
    """
    i = len(s)
    result = None
    for substr in substrs:
        pos = s.find(substr)
        if -1 < pos < i:
            i = pos
            result = substr
    return i, result


def _on_main_thread():
    """Checks if we are on the main thread or not. Duplicated from xonsh.tools
    here so that this module only relies on the Python standrd library.
    """
    return threading.current_thread() is threading.main_thread()


def _find_error_code(e):
    """Gets the approriate error code for an exception e, see
    http://tldp.org/LDP/abs/html/exitcodes.html for exit codes.
    """
    if isinstance(e, PermissionError):
        code = 126
    elif isinstance(e, FileNotFoundError):
        code = 127
    else:
        code = 1
    return code


class TeePTY(object):
    """This class is a pseudo terminal that tees the stdout and stderr into a buffer."""

    def __init__(self, bufsize=1024, remove_color=True, encoding='utf-8',
                 errors='strict'):
        """
        Parameters
        ----------
        bufsize : int, optional
            The buffer size to read from the root terminal to/from the tee'd terminal.
        remove_color : bool, optional
            Removes color codes from the tee'd buffer, though not the TTY.
        encoding : str, optional
            The encoding to use when decoding into a str.
        errors : str, optional
            The encoding error flag to use when decoding into a str.
        """
        self.bufsize = bufsize
        self.pid = self.master_fd = None
        self._in_alt_mode = False
        self.remove_color = remove_color
        self.encoding = encoding
        self.errors = errors
        self.buffer = io.BytesIO()
        self.wcode = None  # os.wait encoded retval
        self._temp_stdin = None

    def __str__(self):
        return self.buffer.getvalue().decode(encoding=self.encoding,
                                             errors=self.errors)

    def __del__(self):
        if self._temp_stdin is not None:
            self._temp_stdin.close()
            self._temp_stdin = None

    def spawn(self, argv=None, env=None, stdin=None, delay=None):
        """Create a spawned process. Based on the code for pty.spawn().
        This cannot be used except from the main thread.

        Parameters
        ----------
        argv : list of str, optional
            Arguments to pass in as subprocess. In None, will execute $SHELL.
        env : Mapping, optional
            Environment to pass execute in.
        delay : float, optional
            Delay timing before executing process if piping in data. The value
            is passed into time.sleep() so it is in [seconds]. If delay is None,
            its value will attempted to be looked up from the environment
            variable $TEEPTY_PIPE_DELAY, from the passed in env or os.environ.
            If not present or not positive valued, no delay is used.

        Returns
        -------
        wcode : int
            Return code for the spawned process encoded as os.wait format.
        """
        assert self.master_fd is None
        self._in_alt_mode = False
        if not argv:
            argv = [os.environ.get('SHELL', 'sh')]
        argv = self._put_stdin_in_argv(argv, stdin)

        pid, master_fd = pty.fork()
        self.pid = pid
        self.master_fd = master_fd
        if pid == pty.CHILD:
            # determine if a piping delay is needed.
            if self._temp_stdin is not None:
                self._delay_for_pipe(env=env, delay=delay)
            # ok, go
            try:
                if env is None:
                    os.execvp(argv[0], argv)
                else:
                    os.execvpe(argv[0], argv, env)
            except OSError as e:
                os._exit(_find_error_code(e))
        else:
            self._pipe_stdin(stdin)

        on_main_thread = _on_main_thread()
        if on_main_thread:
            old_handler = signal.signal(signal.SIGWINCH, self._signal_winch)
        try:
            mode = tty.tcgetattr(pty.STDIN_FILENO)
            tty.setraw(pty.STDIN_FILENO)
            restore = True
        except tty.error:    # This is the same as termios.error
            restore = False
        self._init_fd()
        try:
            self._copy()
        except (IOError, OSError):
            if restore:
                tty.tcsetattr(pty.STDIN_FILENO, tty.TCSAFLUSH, mode)

        _, self.wcode = os.waitpid(pid, 0)
        os.close(master_fd)
        self.master_fd = None
        self._in_alt_mode = False
        if on_main_thread:
            signal.signal(signal.SIGWINCH, old_handler)
        return self.wcode

    def _init_fd(self):
        """Called once when the pty is first set up."""
        self._set_pty_size()

    def _signal_winch(self, signum, frame):
        """Signal handler for SIGWINCH - window size has changed."""
        self._set_pty_size()

    def _set_pty_size(self):
        """Sets the window size of the child pty based on the window size of
        our own controlling terminal.
        """
        assert self.master_fd is not None
        # Get the terminal size of the real terminal, set it on the
        #       pseudoterminal.
        buf = array.array('h', [0, 0, 0, 0])
        fcntl.ioctl(pty.STDOUT_FILENO, termios.TIOCGWINSZ, buf, True)
        fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, buf)

    def _copy(self):
        """Main select loop. Passes all data to self.master_read() or self.stdin_read().
        """
        assert self.master_fd is not None
        master_fd = self.master_fd
        bufsize = self.bufsize
        while True:
            try:
                rfds, wfds, xfds = select.select([master_fd, pty.STDIN_FILENO], [], [])
            except OSError as e:
                if e.errno == 4:  # Interrupted system call.
                    continue      # This happens at terminal resize.
            if master_fd in rfds:
                data = os.read(master_fd, bufsize)
                self.write_stdout(data)
            if pty.STDIN_FILENO in rfds:
                data = os.read(pty.STDIN_FILENO, bufsize)
                self.write_stdin(data)

    def _sanatize_data(self, data):
        i, flag = _findfirst(data, ALTERNATE_MODE_FLAGS)
        if flag is None and self._in_alt_mode:
            return  b''
        elif flag is not None:
            if flag in START_ALTERNATE_MODE:
                # This code is executed when the child process switches the terminal into
                # alternate mode. The line below assumes that the user has opened vim,
                # less, or similar, and writes writes to stdin.
                d0 = data[:i]
                self._in_alt_mode = True
                d1 = self._sanatize_data(data[i+len(flag):])
                data = d0 + d1
            elif flag in END_ALTERNATE_MODE:
                # This code is executed when the child process switches the terminal back
                # out of alternate mode. The line below assumes that the user has
                # returned to the command prompt.
                self._in_alt_mode = False
                data = self._sanatize_data(data[i+len(flag):])
        data = RE_HIDDEN.sub(b'', data)
        if self.remove_color:
            data = RE_COLOR.sub(b'', data)
        return data

    def write_stdout(self, data):
        """Writes to stdout as if the child process had written the data (bytes)."""
        os.write(pty.STDOUT_FILENO, data)  # write to real terminal
        # tee to buffer
        data = self._sanatize_data(data)
        if len(data) > 0:
            self.buffer.write(data)

    def write_stdin(self, data):
        """Writes to the child process from its controlling terminal."""
        master_fd = self.master_fd
        assert master_fd is not None
        while len(data) > 0:
            n = os.write(master_fd, data)
            data = data[n:]

    def _stdin_filename(self, stdin):
        if stdin is None:
            rtn = None
        elif isinstance(stdin, io.FileIO) and os.path.isfile(stdin.name):
            rtn = stdin.name
        elif isinstance(stdin, (io.BufferedIOBase, str, bytes)):
            self._temp_stdin = tsi = tempfile.NamedTemporaryFile()
            rtn = tsi.name
        else:
            raise ValueError('stdin not understood {0!r}'.format(stdin))
        return rtn

    def _put_stdin_in_argv(self, argv, stdin):
        stdin_filename = self._stdin_filename(stdin)
        if stdin_filename is None:
            return argv
        argv = list(argv)
        # a lone dash '-' argument means stdin
        if argv.count('-') == 0:
            argv.append(stdin_filename)
        else:
            argv[argv.index('-')] = stdin_filename
        return argv

    def _pipe_stdin(self, stdin):
        if stdin is None or isinstance(stdin, io.FileIO):
            return None
        tsi = self._temp_stdin
        bufsize = self.bufsize
        if isinstance(stdin, io.BufferedIOBase):
            buf = stdin.read(bufsize)
            while len(buf) != 0:
                tsi.write(buf)
                tsi.flush()
                buf = stdin.read(bufsize)
        elif isinstance(stdin, (str, bytes)):
            raw = stdin.encode() if isinstance(stdin, str) else stdin
            for i in range((len(raw)//bufsize) + 1):
                tsi.write(raw[i*bufsize:(i + 1)*bufsize])
                tsi.flush()
        else:
            raise ValueError('stdin not understood {0!r}'.format(stdin))

    def _delay_for_pipe(self, env=None, delay=None):
        # This delay is sometimes needed because the temporary stdin file that
        # is being written (the pipe) may not have even hits its first flush()
        # call by the time the spawned process starts up and determines there
        # is nothing in the file. The spawn can thus exit, without doing any
        # real work.  Consider the case of piping something into grep:
        #
        #   $ ps aux | grep root
        #
        # grep will exit on EOF and so there is a race between the buffersize
        # and flushing the temporary file and grep.  However, this race is not
        # always meaningful. Pagers, for example, update when the file is written
        # to. So what is important is that we start the spawned process ASAP:
        #
        #   $ ps aux | less
        #
        # So there is a push-and-pull between the the competing objectives of
        # not blocking and letting the spawned process have enough to work with
        # such that it doesn't exit prematurely.  Unfortunately, there is no
        # way to know a priori how big the file is, how long the spawned process
        # will run for, etc. Thus as user-definable delay let's the user
        # find something that works for them.
        if delay is None:
            delay = (env or os.environ).get('TEEPTY_PIPE_DELAY', -1.0)
        delay = float(delay)
        if 0.0 < delay:
            time.sleep(delay)

def _teepty_main():
    tpty = TeePTY()
    tpty.spawn(sys.argv[1:])
    print('-=-'*10)
    print(tpty.buffer.getvalue())
    print('-=-'*10)
    print(tpty)
    print('-=-'*10)
    print('Returned with status {0}'.format(tpty.wcode))

if __name__ == '__main__':
    _teepty_main()

#
# jobs
#
# -*- coding: utf-8 -*-
"""Job control for the xonsh shell."""
# amalgamated os
# amalgamated sys
# amalgamated time
ctypes = _LazyModule.load('ctypes', 'ctypes')
# amalgamated signal
# amalgamated builtins
# amalgamated functools
# amalgamated subprocess
collections = _LazyModule.load('collections', 'collections')
# amalgamated xonsh.lazyasd
# amalgamated xonsh.platform
tasks = LazyObject(collections.deque, globals(), 'tasks')
# Track time stamp of last exit command, so that two consecutive attempts to
# exit can kill all jobs and exit.
_last_exit_time = None


if ON_DARWIN:
    def _send_signal(job, signal):
        # On OS X, os.killpg() may cause PermissionError when there are
        # any zombie processes in the process group.
        # See github issue #1012 for details
        for pid in job['pids']:
            if pid is None:  # the pid of an aliased proc is None
                continue
            os.kill(pid, signal)
elif ON_WINDOWS:
    pass
elif ON_CYGWIN:
    # Similar to what happened on OSX, more issues on Cygwin
    # (see Github issue #514).
    def _send_signal(job, signal):
        try:
            os.killpg(job['pgrp'], signal)
        except Exception:
            for pid in job['pids']:
                try:
                    os.kill(pid, signal)
                except:
                    pass
else:
    def _send_signal(job, signal):
        pgrp = job['pgrp']
        if pgrp is None:
            for pid in job['pids']:
                try:
                    os.kill(pid, signal)
                except:
                    pass
        else:
            os.killpg(job['pgrp'], signal)


if ON_WINDOWS:
    def _continue(job):
        job['status'] = "running"

    def _kill(job):
        subprocess.check_output(['taskkill', '/F', '/T', '/PID',
                                 str(job['obj'].pid)])

    def ignore_sigtstp():
        pass

    def _set_pgrp(info):
        pass

    def wait_for_active_job(signal_to_send=None):
        """
        Wait for the active job to finish, to be killed by SIGINT, or to be
        suspended by ctrl-z.
        """
        _clear_dead_jobs()
        active_task = get_next_task()
        # Return when there are no foreground active task
        if active_task is None:
            return
        obj = active_task['obj']
        _continue(active_task)
        while obj.returncode is None:
            try:
                obj.wait(0.01)
            except subprocess.TimeoutExpired:
                pass
            except KeyboardInterrupt:
                _kill(active_task)
        return wait_for_active_job()

else:
    def _continue(job):
        _send_signal(job, signal.SIGCONT)

    def _kill(job):
        _send_signal(job, signal.SIGKILL)

    def ignore_sigtstp():
        signal.signal(signal.SIGTSTP, signal.SIG_IGN)

    def _set_pgrp(info):
        pid = info['pids'][0]
        if pid is None:
            # occurs if first process is an alias
            info['pgrp'] = None
            return
        try:
            info['pgrp'] = os.getpgid(pid)
        except ProcessLookupError:
            info['pgrp'] = None

    _shell_pgrp = os.getpgrp()

    _block_when_giving = LazyObject(lambda: (signal.SIGTTOU, signal.SIGTTIN,
                                             signal.SIGTSTP, signal.SIGCHLD),
                                    globals(), '_block_when_giving')

    # check for shell tty
    @functools.lru_cache(1)
    def _shell_tty():
        try:
            _st = sys.stderr.fileno()
            if os.tcgetpgrp(_st) != os.getpgid(os.getpid()):
                # we don't own it
                _st = None
        except OSError:
            _st = None
        return _st


    # _give_terminal_to is a simplified version of:
    #    give_terminal_to from bash 4.3 source, jobs.c, line 4030
    # this will give the terminal to the process group pgid
    if ON_CYGWIN:
        _libc = LazyObject(lambda: ctypes.CDLL('cygwin1.dll'),
                           globals(), '_libc')

        # on cygwin, signal.pthread_sigmask does not exist in Python, even
        # though pthread_sigmask is defined in the kernel.  thus, we use
        # ctypes to mimic the calls in the "normal" version below.
        def _give_terminal_to(pgid):
            st = _shell_tty()
            if st is not None and os.isatty(st):
                omask = ctypes.c_ulong()
                mask = ctypes.c_ulong()
                _libc.sigemptyset(ctypes.byref(mask))
                for i in _block_when_giving:
                    _libc.sigaddset(ctypes.byref(mask), ctypes.c_int(i))
                _libc.sigemptyset(ctypes.byref(omask))
                _libc.sigprocmask(ctypes.c_int(signal.SIG_BLOCK),
                                  ctypes.byref(mask),
                                  ctypes.byref(omask))
                _libc.tcsetpgrp(ctypes.c_int(st), ctypes.c_int(pgid))
                _libc.sigprocmask(ctypes.c_int(signal.SIG_SETMASK),
                                  ctypes.byref(omask), None)
    else:
        def _give_terminal_to(pgid):
            st = _shell_tty()
            if st is not None and os.isatty(st):
                oldmask = signal.pthread_sigmask(signal.SIG_BLOCK,
                                                 _block_when_giving)
                os.tcsetpgrp(st, pgid)
                signal.pthread_sigmask(signal.SIG_SETMASK, oldmask)


    def wait_for_active_job():
        """
        Wait for the active job to finish, to be killed by SIGINT, or to be
        suspended by ctrl-z.
        """
        _clear_dead_jobs()
        active_task = get_next_task()
        # Return when there are no foreground active task
        if active_task is None:
            _give_terminal_to(_shell_pgrp)  # give terminal back to the shell
            return
        pgrp = active_task.get('pgrp', None)
        obj = active_task['obj']
        # give the terminal over to the fg process
        if pgrp is not None:
            _give_terminal_to(pgrp)
        _continue(active_task)
        _, wcode = os.waitpid(obj.pid, os.WUNTRACED)
        if os.WIFSTOPPED(wcode):
            print()  # get a newline because ^Z will have been printed
            active_task['status'] = "stopped"
        elif os.WIFSIGNALED(wcode):
            print()  # get a newline because ^C will have been printed
            obj.signal = (os.WTERMSIG(wcode), os.WCOREDUMP(wcode))
            obj.returncode = None
        else:
            obj.returncode = os.WEXITSTATUS(wcode)
            obj.signal = None
        return wait_for_active_job()


def get_next_task():
    """ Get the next active task and put it on top of the queue"""
    selected_task = None
    for tid in tasks:
        task = get_task(tid)
        if not task['bg'] and task['status'] == "running":
            selected_task = tid
            break
    if selected_task is None:
        return
    tasks.remove(selected_task)
    tasks.appendleft(selected_task)
    return get_task(selected_task)


def get_task(tid):
    return builtins.__xonsh_all_jobs__[tid]


def _clear_dead_jobs():
    to_remove = set()
    for tid in tasks:
        obj = get_task(tid)['obj']
        if obj.poll() is not None:
            to_remove.add(tid)
    for job in to_remove:
        tasks.remove(job)
        del builtins.__xonsh_all_jobs__[job]


def print_one_job(num, outfile=sys.stdout):
    """Print a line describing job number ``num``."""
    try:
        job = builtins.__xonsh_all_jobs__[num]
    except KeyError:
        return
    pos = '+' if tasks[0] == num else '-' if tasks[1] == num else ' '
    status = job['status']
    cmd = [' '.join(i) if isinstance(i, list) else i for i in job['cmds']]
    cmd = ' '.join(cmd)
    pid = job['pids'][-1]
    bg = ' &' if job['bg'] else ''
    print('[{}]{} {}: {}{} ({})'.format(num, pos, status, cmd, bg, pid),
          file=outfile)


def get_next_job_number():
    """Get the lowest available unique job number (for the next job created).
    """
    _clear_dead_jobs()
    i = 1
    while i in builtins.__xonsh_all_jobs__:
        i += 1
    return i


def add_job(info):
    """
    Add a new job to the jobs dictionary.
    """
    num = get_next_job_number()
    info['started'] = time.time()
    info['status'] = "running"
    _set_pgrp(info)
    tasks.appendleft(num)
    builtins.__xonsh_all_jobs__[num] = info
    if info['bg']:
        print_one_job(num)


def clean_jobs():
    """Clean up jobs for exiting shell

    In non-interactive mode, kill all jobs.

    In interactive mode, check for suspended or background jobs, print a
    warning if any exist, and return False. Otherwise, return True.
    """
    jobs_clean = True
    if builtins.__xonsh_env__['XONSH_INTERACTIVE']:
        _clear_dead_jobs()

        if builtins.__xonsh_all_jobs__:
            global _last_exit_time
            if builtins.__xonsh_history__.buffer:
                last_cmd_start = builtins.__xonsh_history__.buffer[-1]['ts'][0]
            else:
                last_cmd_start = None

            if (_last_exit_time and last_cmd_start and
                    _last_exit_time > last_cmd_start):
                # Exit occurred after last command started, so it was called as
                # part of the last command and is now being called again
                # immediately. Kill jobs and exit without reminder about
                # unfinished jobs in this case.
                kill_all_jobs()
            else:
                if len(builtins.__xonsh_all_jobs__) > 1:
                    msg = 'there are unfinished jobs'
                else:
                    msg = 'there is an unfinished job'

                if builtins.__xonsh_env__['SHELL_TYPE'] != 'prompt_toolkit':
                    # The Ctrl+D binding for prompt_toolkit already inserts a
                    # newline
                    print()
                print('xonsh: {}'.format(msg), file=sys.stderr)
                print('-'*5, file=sys.stderr)
                jobs([], stdout=sys.stderr)
                print('-'*5, file=sys.stderr)
                print('Type "exit" or press "ctrl-d" again to force quit.',
                      file=sys.stderr)
                jobs_clean = False
                _last_exit_time = time.time()
    else:
        kill_all_jobs()

    return jobs_clean


def kill_all_jobs():
    """
    Send SIGKILL to all child processes (called when exiting xonsh).
    """
    _clear_dead_jobs()
    for job in builtins.__xonsh_all_jobs__.values():
        _kill(job)


def jobs(args, stdin=None, stdout=sys.stdout, stderr=None):
    """
    xonsh command: jobs

    Display a list of all current jobs.
    """
    _clear_dead_jobs()
    for j in tasks:
        print_one_job(j, outfile=stdout)
    return None, None


def fg(args, stdin=None):
    """
    xonsh command: fg

    Bring the currently active job to the foreground, or, if a single number is
    given as an argument, bring that job to the foreground. Additionally,
    specify "+" for the most recent job and "-" for the second most recent job.
    """

    _clear_dead_jobs()
    if len(tasks) == 0:
        return '', 'Cannot bring nonexistent job to foreground.\n'

    if len(args) == 0:
        act = tasks[0]  # take the last manipulated task by default
    elif len(args) == 1:
        try:
            if args[0] == '+':  # take the last manipulated task
                act = tasks[0]
            elif args[0] == '-':  # take the second to last manipulated task
                act = tasks[1]
            else:
                act = int(args[0])
        except (ValueError, IndexError):
            return '', 'Invalid job: {}\n'.format(args[0])

        if act not in builtins.__xonsh_all_jobs__:
            return '', 'Invalid job: {}\n'.format(args[0])
    else:
        return '', 'fg expects 0 or 1 arguments, not {}\n'.format(len(args))

    # Put this one on top of the queue
    tasks.remove(act)
    tasks.appendleft(act)

    job = get_task(act)
    job['bg'] = False
    job['status'] = "running"
    print_one_job(act)


def bg(args, stdin=None):
    """
    xonsh command: bg

    Resume execution of the currently active job in the background, or, if a
    single number is given as an argument, resume that job in the background.
    """
    res = fg(args, stdin)
    if res is None:
        curTask = get_task(tasks[0])
        curTask['bg'] = True
        _continue(curTask)
    else:
        return res

#
# parser
#
# -*- coding: utf-8 -*-
"""Implements the xonsh parser."""
# amalgamated xonsh.platform
if PYTHON_VERSION_INFO < (3, 5, 0):
    from xonsh.parsers.v34 import Parser
else:
    from xonsh.parsers.v35 import Parser

#
# tokenize
#
"""Tokenization help for xonsh programs.

This file is a modified version of tokenize.py form the Python 3.4 and 3.5
standard libraries (licensed under the Python Software Foundation License,
version 2), which provides tokenization help for Python programs.

It is modified to properly tokenize xonsh code, including backtick regex
path and several xonsh-specific operators.

A few pieces of this file are specific to the version of Python being used.
To find these pieces, search the PY35.

Original file credits:
   __author__ = 'Ka-Ping Yee <ping@lfw.org>'
   __credits__ = ('GvR, ESR, Tim Peters, Thomas Wouters, Fred Drake, '
                  'Skip Montanaro, Raymond Hettinger, Trent Nelson, '
                  'Michael Foord')
"""

from builtins import open as _builtin_open
from codecs import lookup, BOM_UTF8
# amalgamated collections
from io import TextIOWrapper
from itertools import chain
# amalgamated re
# amalgamated sys
from token import (AMPER, AMPEREQUAL, AT, CIRCUMFLEX,
        CIRCUMFLEXEQUAL, COLON, COMMA, DEDENT, DOT, DOUBLESLASH,
        DOUBLESLASHEQUAL, DOUBLESTAR, DOUBLESTAREQUAL, ENDMARKER, EQEQUAL,
        EQUAL, ERRORTOKEN, GREATER, GREATEREQUAL, INDENT, LBRACE, LEFTSHIFT,
        LEFTSHIFTEQUAL, LESS, LESSEQUAL, LPAR, LSQB, MINEQUAL, MINUS, NAME,
        NEWLINE, NOTEQUAL, NUMBER, N_TOKENS, OP, PERCENT, PERCENTEQUAL, PLUS,
        PLUSEQUAL, RBRACE, RIGHTSHIFT, RIGHTSHIFTEQUAL, RPAR, RSQB, SEMI,
        SLASH, SLASHEQUAL, STAR, STAREQUAL, STRING, TILDE, VBAR, VBAREQUAL,
        tok_name)

# amalgamated xonsh.lazyasd
# amalgamated xonsh.platform
cookie_re = LazyObject(
    lambda: re.compile(r'^[ \t\f]*#.*coding[:=][ \t]*([-\w.]+)', re.ASCII),
    globals(), 'cookie_re')
blank_re = LazyObject(lambda: re.compile(br'^[ \t\f]*(?:[#\r\n]|$)', re.ASCII),
                      globals(), 'blank_re')

token = _LazyModule.load('token', 'token')
__all__ = token.__all__ + ["COMMENT", "tokenize", "detect_encoding",
                           "NL", "untokenize", "ENCODING", "TokenInfo",
                           "TokenError", 'SEARCHPATH', 'ATDOLLAR', 'ATEQUAL',
                           'DOLLARNAME', 'IOREDIRECT']
del token

PY35 = PYTHON_VERSION_INFO >= (3, 5, 0)
if PY35:
    from token import ASYNC, AWAIT
    AUGASSIGN_OPS = r"[+\-*/%&@|^=<>]=?"
    ADDSPACE_TOKS = (NAME, NUMBER, ASYNC, AWAIT)
else:
    AUGASSIGN_OPS = r"[+\-*/%&|^=<>]=?"
    ADDSPACE_TOKS = (NAME, NUMBER)


COMMENT = N_TOKENS
tok_name[COMMENT] = 'COMMENT'
NL = N_TOKENS + 1
tok_name[NL] = 'NL'
ENCODING = N_TOKENS + 2
tok_name[ENCODING] = 'ENCODING'
N_TOKENS += 3
SEARCHPATH = N_TOKENS
tok_name[N_TOKENS] = 'SEARCHPATH'
N_TOKENS += 1
IOREDIRECT = N_TOKENS
tok_name[N_TOKENS] = 'IOREDIRECT'
N_TOKENS += 1
DOLLARNAME = N_TOKENS
tok_name[N_TOKENS] = 'DOLLARNAME'
N_TOKENS += 1
ATDOLLAR = N_TOKENS
tok_name[N_TOKENS] = 'ATDOLLAR'
N_TOKENS += 1
ATEQUAL = N_TOKENS
tok_name[N_TOKENS] = 'ATEQUAL'
N_TOKENS += 1
_xonsh_tokens = {
    '?':   'QUESTION',
    '@=':  'ATEQUAL',
    '@$':  'ATDOLLAR',
    '||':  'DOUBLEPIPE',
    '&&':  'DOUBLEAMPER',
    '@(':  'ATLPAREN',
    '!(':  'BANGLPAREN',
    '![':  'BANGLBRACKET',
    '$(':  'DOLLARLPAREN',
    '$[':  'DOLLARLBRACKET',
    '${':  'DOLLARLBRACE',
    '??':  'DOUBLEQUESTION',
    '@$(': 'ATDOLLARLPAREN',
}

additional_parenlevs = frozenset({'@(', '!(', '![', '$(', '$[', '${', '@$('})

for k, v in _xonsh_tokens.items():
    exec('%s = N_TOKENS' % v)
    tok_name[N_TOKENS] = v
    N_TOKENS += 1
    __all__.append(v)


EXACT_TOKEN_TYPES = {
    '(':   LPAR,
    ')':   RPAR,
    '[':   LSQB,
    ']':   RSQB,
    ':':   COLON,
    ',':   COMMA,
    ';':   SEMI,
    '+':   PLUS,
    '-':   MINUS,
    '*':   STAR,
    '/':   SLASH,
    '|':   VBAR,
    '&':   AMPER,
    '<':   LESS,
    '>':   GREATER,
    '=':   EQUAL,
    '.':   DOT,
    '%':   PERCENT,
    '{':   LBRACE,
    '}':   RBRACE,
    '==':  EQEQUAL,
    '!=':  NOTEQUAL,
    '<=':  LESSEQUAL,
    '>=':  GREATEREQUAL,
    '~':   TILDE,
    '^':   CIRCUMFLEX,
    '<<':  LEFTSHIFT,
    '>>':  RIGHTSHIFT,
    '**':  DOUBLESTAR,
    '+=':  PLUSEQUAL,
    '-=':  MINEQUAL,
    '*=':  STAREQUAL,
    '/=':  SLASHEQUAL,
    '%=':  PERCENTEQUAL,
    '&=':  AMPEREQUAL,
    '|=':  VBAREQUAL,
    '^=': CIRCUMFLEXEQUAL,
    '<<=': LEFTSHIFTEQUAL,
    '>>=': RIGHTSHIFTEQUAL,
    '**=': DOUBLESTAREQUAL,
    '//':  DOUBLESLASH,
    '//=': DOUBLESLASHEQUAL,
    '@':   AT,
}

EXACT_TOKEN_TYPES.update(_xonsh_tokens)


class TokenInfo(collections.namedtuple('TokenInfo', 'type string start end line')):
    def __repr__(self):
        annotated_type = '%d (%s)' % (self.type, tok_name[self.type])
        return ('TokenInfo(type=%s, string=%r, start=%r, end=%r, line=%r)' %
                self._replace(type=annotated_type))

    @property
    def exact_type(self):
        if self.type == OP and self.string in EXACT_TOKEN_TYPES:
            return EXACT_TOKEN_TYPES[self.string]
        else:
            return self.type

def group(*choices): return '(' + '|'.join(choices) + ')'
def tokany(*choices): return group(*choices) + '*'
def maybe(*choices): return group(*choices) + '?'

# Note: we use unicode matching for names ("\w") but ascii matching for
# number literals.
Whitespace = r'[ \f\t]*'
Comment = r'#[^\r\n]*'
Ignore = Whitespace + tokany(r'\\\r?\n' + Whitespace) + maybe(Comment)
Name_RE = r'\$?\w+'

Hexnumber = r'0[xX][0-9a-fA-F]+'
Binnumber = r'0[bB][01]+'
Octnumber = r'0[oO][0-7]+'
Decnumber = r'(?:0+|[1-9][0-9]*)'
Intnumber = group(Hexnumber, Binnumber, Octnumber, Decnumber)
Exponent = r'[eE][-+]?[0-9]+'
Pointfloat = group(r'[0-9]+\.[0-9]*', r'\.[0-9]+') + maybe(Exponent)
Expfloat = r'[0-9]+' + Exponent
Floatnumber = group(Pointfloat, Expfloat)
Imagnumber = group(r'[0-9]+[jJ]', Floatnumber + r'[jJ]')
Number = group(Imagnumber, Floatnumber, Intnumber)

StringPrefix = r'(?:[bB][rR]?|[rR][bB]?|[uU])?'

# Tail end of ' string.
Single = r"[^'\\]*(?:\\.[^'\\]*)*'"
# Tail end of " string.
Double = r'[^"\\]*(?:\\.[^"\\]*)*"'
# Tail end of ''' string.
Single3 = r"[^'\\]*(?:(?:\\.|'(?!''))[^'\\]*)*'''"
# Tail end of """ string.
Double3 = r'[^"\\]*(?:(?:\\.|"(?!""))[^"\\]*)*"""'
Triple = group(StringPrefix + "'''", StringPrefix + '"""')
# Single-line ' or " string.
String = group(StringPrefix + r"'[^\n'\\]*(?:\\.[^\n'\\]*)*'",
               StringPrefix + r'"[^\n"\\]*(?:\\.[^\n"\\]*)*"')

# Xonsh-specific Syntax
SearchPath = r"((?:[rg]|@\w*)?)`([^\n`\\]*(?:\\.[^\n`\\]*)*)`"

# Because of leftmost-then-longest match semantics, be sure to put the
# longest operators first (e.g., if = came before ==, == would get
# recognized as two instances of =).
_redir_names = ('out', 'all', 'err', 'e', '2', 'a', '&', '1', 'o')
_e2o_map = ('err>out', 'err>&1', '2>out', 'err>o', 'err>1', 'e>out', 'e>&1',
            '2>&1', 'e>o', '2>o', 'e>1', '2>1')
IORedirect = group(group(*_e2o_map), '{}>>?'.format(group(*_redir_names)))
_redir_check = set(_e2o_map)
_redir_check = {'{}>'.format(i) for i in _redir_names}.union(_redir_check)
_redir_check = {'{}>>'.format(i) for i in _redir_names}.union(_redir_check)
_redir_check = frozenset(_redir_check)
Operator = group(r"\*\*=?", r">>=?", r"<<=?", r"!=", r"//=?", r"->",
                 r"@\$\(?", r'\|\|', '&&', r'@\(', r'!\(', r'!\[', r'\$\(',
                 r'\$\[', '\${', r'\?\?', r'\?', AUGASSIGN_OPS, r"~")

Bracket = '[][(){}]'
Special = group(r'\r?\n', r'\.\.\.', r'[:;.,@]')
Funny = group(Operator, Bracket, Special)

PlainToken = group(IORedirect, Number, Funny, String, Name_RE, SearchPath)
Token = Ignore + PlainToken

# First (or only) line of ' or " string.
ContStr = group(StringPrefix + r"'[^\n'\\]*(?:\\.[^\n'\\]*)*" +
                group("'", r'\\\r?\n'),
                StringPrefix + r'"[^\n"\\]*(?:\\.[^\n"\\]*)*' +
                group('"', r'\\\r?\n'))
PseudoExtras = group(r'\\\r?\n|\Z', Comment, Triple, SearchPath)
PseudoToken = Whitespace + group(PseudoExtras, IORedirect, Number, Funny,
                                 ContStr, Name_RE)

def _compile(expr):
    return re.compile(expr, re.UNICODE)

endpats = {"'": Single, '"': Double,
           "'''": Single3, '"""': Double3,
           "r'''": Single3, 'r"""': Double3,
           "b'''": Single3, 'b"""': Double3,
           "R'''": Single3, 'R"""': Double3,
           "B'''": Single3, 'B"""': Double3,
           "br'''": Single3, 'br"""': Double3,
           "bR'''": Single3, 'bR"""': Double3,
           "Br'''": Single3, 'Br"""': Double3,
           "BR'''": Single3, 'BR"""': Double3,
           "rb'''": Single3, 'rb"""': Double3,
           "Rb'''": Single3, 'Rb"""': Double3,
           "rB'''": Single3, 'rB"""': Double3,
           "RB'''": Single3, 'RB"""': Double3,
           "u'''": Single3, 'u"""': Double3,
           "U'''": Single3, 'U"""': Double3,
           'r': None, 'R': None, 'b': None, 'B': None,
           'u': None, 'U': None}

triple_quoted = {}
for t in ("'''", '"""',
          "r'''", 'r"""', "R'''", 'R"""',
          "b'''", 'b"""', "B'''", 'B"""',
          "br'''", 'br"""', "Br'''", 'Br"""',
          "bR'''", 'bR"""', "BR'''", 'BR"""',
          "rb'''", 'rb"""', "rB'''", 'rB"""',
          "Rb'''", 'Rb"""', "RB'''", 'RB"""',
          "u'''", 'u"""', "U'''", 'U"""',
          ):
    triple_quoted[t] = t
single_quoted = {}
for t in ("'", '"',
          "r'", 'r"', "R'", 'R"',
          "b'", 'b"', "B'", 'B"',
          "br'", 'br"', "Br'", 'Br"',
          "bR'", 'bR"', "BR'", 'BR"' ,
          "rb'", 'rb"', "rB'", 'rB"',
          "Rb'", 'Rb"', "RB'", 'RB"' ,
          "u'", 'u"', "U'", 'U"',
          ):
    single_quoted[t] = t

tabsize = 8

class TokenError(Exception): pass

class StopTokenizing(Exception): pass


class Untokenizer:

    def __init__(self):
        self.tokens = []
        self.prev_row = 1
        self.prev_col = 0
        self.encoding = None

    def add_whitespace(self, start):
        row, col = start
        if row < self.prev_row or row == self.prev_row and col < self.prev_col:
            raise ValueError("start ({},{}) precedes previous end ({},{})"
                             .format(row, col, self.prev_row, self.prev_col))
        row_offset = row - self.prev_row
        if row_offset:
            self.tokens.append("\\\n" * row_offset)
            self.prev_col = 0
        col_offset = col - self.prev_col
        if col_offset:
            self.tokens.append(" " * col_offset)

    def untokenize(self, iterable):
        it = iter(iterable)
        indents = []
        startline = False
        for t in it:
            if len(t) == 2:
                self.compat(t, it)
                break
            tok_type, token, start, end, line = t
            if tok_type == ENCODING:
                self.encoding = token
                continue
            if tok_type == ENDMARKER:
                break
            if tok_type == INDENT:
                indents.append(token)
                continue
            elif tok_type == DEDENT:
                indents.pop()
                self.prev_row, self.prev_col = end
                continue
            elif tok_type in (NEWLINE, NL):
                startline = True
            elif startline and indents:
                indent = indents[-1]
                if start[1] >= len(indent):
                    self.tokens.append(indent)
                    self.prev_col = len(indent)
                startline = False
            self.add_whitespace(start)
            self.tokens.append(token)
            self.prev_row, self.prev_col = end
            if tok_type in (NEWLINE, NL):
                self.prev_row += 1
                self.prev_col = 0
        return "".join(self.tokens)

    def compat(self, token, iterable):
        indents = []
        toks_append = self.tokens.append
        startline = token[0] in (NEWLINE, NL)
        prevstring = False

        for tok in chain([token], iterable):
            toknum, tokval = tok[:2]
            if toknum == ENCODING:
                self.encoding = tokval
                continue

            if toknum in ADDSPACE_TOKS:
                tokval += ' '

            # Insert a space between two consecutive strings
            if toknum == STRING:
                if prevstring:
                    tokval = ' ' + tokval
                prevstring = True
            else:
                prevstring = False

            if toknum == INDENT:
                indents.append(tokval)
                continue
            elif toknum == DEDENT:
                indents.pop()
                continue
            elif toknum in (NEWLINE, NL):
                startline = True
            elif startline and indents:
                toks_append(indents[-1])
                startline = False
            toks_append(tokval)


def untokenize(iterable):
    """Transform tokens back into Python source code.
    It returns a bytes object, encoded using the ENCODING
    token, which is the first token sequence output by tokenize.

    Each element returned by the iterable must be a token sequence
    with at least two elements, a token number and token value.  If
    only two tokens are passed, the resulting output is poor.

    Round-trip invariant for full input:
        Untokenized source will match input source exactly

    Round-trip invariant for limited intput:
        # Output bytes will tokenize the back to the input
        t1 = [tok[:2] for tok in tokenize(f.readline)]
        newcode = untokenize(t1)
        readline = BytesIO(newcode).readline
        t2 = [tok[:2] for tok in tokenize(readline)]
        assert t1 == t2
    """
    ut = Untokenizer()
    out = ut.untokenize(iterable)
    if ut.encoding is not None:
        out = out.encode(ut.encoding)
    return out


def _get_normal_name(orig_enc):
    """Imitates get_normal_name in tokenizer.c."""
    # Only care about the first 12 characters.
    enc = orig_enc[:12].lower().replace("_", "-")
    if enc == "utf-8" or enc.startswith("utf-8-"):
        return "utf-8"
    if enc in ("latin-1", "iso-8859-1", "iso-latin-1") or \
       enc.startswith(("latin-1-", "iso-8859-1-", "iso-latin-1-")):
        return "iso-8859-1"
    return orig_enc

def detect_encoding(readline):
    """
    The detect_encoding() function is used to detect the encoding that should
    be used to decode a Python source file.  It requires one argument, readline,
    in the same way as the tokenize() generator.

    It will call readline a maximum of twice, and return the encoding used
    (as a string) and a list of any lines (left as bytes) it has read in.

    It detects the encoding from the presence of a utf-8 bom or an encoding
    cookie as specified in pep-0263.  If both a bom and a cookie are present,
    but disagree, a SyntaxError will be raised.  If the encoding cookie is an
    invalid charset, raise a SyntaxError.  Note that if a utf-8 bom is found,
    'utf-8-sig' is returned.

    If no encoding is specified, then the default of 'utf-8' will be returned.
    """
    try:
        filename = readline.__self__.name
    except AttributeError:
        filename = None
    bom_found = False
    encoding = None
    default = 'utf-8'
    def read_or_stop():
        try:
            return readline()
        except StopIteration:
            return b''

    def find_cookie(line):
        try:
            # Decode as UTF-8. Either the line is an encoding declaration,
            # in which case it should be pure ASCII, or it must be UTF-8
            # per default encoding.
            line_string = line.decode('utf-8')
        except UnicodeDecodeError:
            msg = "invalid or missing encoding declaration"
            if filename is not None:
                msg = '{} for {!r}'.format(msg, filename)
            raise SyntaxError(msg)

        match = cookie_re.match(line_string)
        if not match:
            return None
        encoding = _get_normal_name(match.group(1))
        try:
            codec = lookup(encoding)
        except LookupError:
            # This behaviour mimics the Python interpreter
            if filename is None:
                msg = "unknown encoding: " + encoding
            else:
                msg = "unknown encoding for {!r}: {}".format(filename,
                        encoding)
            raise SyntaxError(msg)

        if bom_found:
            if encoding != 'utf-8':
                # This behaviour mimics the Python interpreter
                if filename is None:
                    msg = 'encoding problem: utf-8'
                else:
                    msg = 'encoding problem for {!r}: utf-8'.format(filename)
                raise SyntaxError(msg)
            encoding += '-sig'
        return encoding

    first = read_or_stop()
    if first.startswith(BOM_UTF8):
        bom_found = True
        first = first[3:]
        default = 'utf-8-sig'
    if not first:
        return default, []

    encoding = find_cookie(first)
    if encoding:
        return encoding, [first]
    if not blank_re.match(first):
        return default, [first]

    second = read_or_stop()
    if not second:
        return default, [first]

    encoding = find_cookie(second)
    if encoding:
        return encoding, [first, second]

    return default, [first, second]


def _tokopen(filename):
    """Open a file in read only mode using the encoding detected by
    detect_encoding().
    """
    buffer = _builtin_open(filename, 'rb')
    try:
        encoding, lines = detect_encoding(buffer.readline)
        buffer.seek(0)
        text = TextIOWrapper(buffer, encoding, line_buffering=True)
        text.mode = 'r'
        return text
    except:
        buffer.close()
        raise


def _tokenize(readline, encoding):
    lnum = parenlev = continued = 0
    numchars = '0123456789'
    contstr, needcont = '', 0
    contline = None
    indents = [0]

    # 'stashed' and 'async_*' are used for async/await parsing
    stashed = None
    async_def = False
    async_def_indent = 0
    async_def_nl = False

    if encoding is not None:
        if encoding == "utf-8-sig":
            # BOM will already have been stripped.
            encoding = "utf-8"
        yield TokenInfo(ENCODING, encoding, (0, 0), (0, 0), '')
    while True:             # loop over lines in stream
        try:
            line = readline()
        except StopIteration:
            line = b''

        if encoding is not None:
            line = line.decode(encoding)
        lnum += 1
        pos, max = 0, len(line)

        if contstr:                            # continued string
            if not line:
                raise TokenError("EOF in multi-line string", strstart)
            endmatch = endprog.match(line)
            if endmatch:
                pos = end = endmatch.end(0)
                yield TokenInfo(STRING, contstr + line[:end],
                       strstart, (lnum, end), contline + line)
                contstr, needcont = '', 0
                contline = None
            elif needcont and line[-2:] != '\\\n' and line[-3:] != '\\\r\n':
                yield TokenInfo(ERRORTOKEN, contstr + line,
                           strstart, (lnum, len(line)), contline)
                contstr = ''
                contline = None
                continue
            else:
                contstr = contstr + line
                contline = contline + line
                continue

        elif parenlev == 0 and not continued:  # new statement
            if not line: break
            column = 0
            while pos < max:                   # measure leading whitespace
                if line[pos] == ' ':
                    column += 1
                elif line[pos] == '\t':
                    column = (column//tabsize + 1)*tabsize
                elif line[pos] == '\f':
                    column = 0
                else:
                    break
                pos += 1
            if pos == max:
                break

            if line[pos] in '#\r\n':           # skip comments or blank lines
                if line[pos] == '#':
                    comment_token = line[pos:].rstrip('\r\n')
                    nl_pos = pos + len(comment_token)
                    yield TokenInfo(COMMENT, comment_token,
                           (lnum, pos), (lnum, pos + len(comment_token)), line)
                    yield TokenInfo(NL, line[nl_pos:],
                           (lnum, nl_pos), (lnum, len(line)), line)
                else:
                    yield TokenInfo((NL, COMMENT)[line[pos] == '#'], line[pos:],
                           (lnum, pos), (lnum, len(line)), line)
                continue

            if column > indents[-1]:           # count indents or dedents
                indents.append(column)
                yield TokenInfo(INDENT, line[:pos], (lnum, 0), (lnum, pos), line)
            while column < indents[-1]:
                if column not in indents:
                    raise IndentationError(
                        "unindent does not match any outer indentation level",
                        ("<tokenize>", lnum, pos, line))
                indents = indents[:-1]

                if async_def and async_def_indent >= indents[-1]:
                    async_def = False
                    async_def_nl = False
                    async_def_indent = 0

                yield TokenInfo(DEDENT, '', (lnum, pos), (lnum, pos), line)

            if async_def and async_def_nl and async_def_indent >= indents[-1]:
                async_def = False
                async_def_nl = False
                async_def_indent = 0

        else:                                  # continued statement
            if not line:
                raise TokenError("EOF in multi-line statement", (lnum, 0))
            continued = 0

        while pos < max:
            pseudomatch = _compile(PseudoToken).match(line, pos)
            if pseudomatch:                                # scan for tokens
                start, end = pseudomatch.span(1)
                spos, epos, pos = (lnum, start), (lnum, end), end
                if start == end:
                    continue
                token, initial = line[start:end], line[start]

                if token in _redir_check:
                    yield TokenInfo(IOREDIRECT, token, spos, epos, line)
                elif (initial in numchars or                  # ordinary number
                    (initial == '.' and token != '.' and token != '...')):
                    yield TokenInfo(NUMBER, token, spos, epos, line)
                elif initial in '\r\n':
                    if stashed:
                        yield stashed
                        stashed = None
                    if parenlev > 0:
                        yield TokenInfo(NL, token, spos, epos, line)
                    else:
                        yield TokenInfo(NEWLINE, token, spos, epos, line)
                        if async_def:
                            async_def_nl = True

                elif initial == '#':
                    assert not token.endswith("\n")
                    if stashed:
                        yield stashed
                        stashed = None
                    yield TokenInfo(COMMENT, token, spos, epos, line)
                # Xonsh-specific Regex Globbing
                elif re.match(SearchPath, token):
                    yield TokenInfo(SEARCHPATH, token, spos, epos, line)
                elif token in triple_quoted:
                    endprog = _compile(endpats[token])
                    endmatch = endprog.match(line, pos)
                    if endmatch:                           # all on one line
                        pos = endmatch.end(0)
                        token = line[start:pos]
                        yield TokenInfo(STRING, token, spos, (lnum, pos), line)
                    else:
                        strstart = (lnum, start)           # multiple lines
                        contstr = line[start:]
                        contline = line
                        break
                elif initial in single_quoted or \
                    token[:2] in single_quoted or \
                    token[:3] in single_quoted:
                    if token[-1] == '\n':                  # continued string
                        strstart = (lnum, start)
                        endprog = _compile(endpats[initial] or
                                           endpats[token[1]] or
                                           endpats[token[2]])
                        contstr, needcont = line[start:], 1
                        contline = line
                        break
                    else:                                  # ordinary string
                        yield TokenInfo(STRING, token, spos, epos, line)
                elif token.startswith('$') and token[1:].isidentifier():
                    yield TokenInfo(DOLLARNAME, token, spos, epos, line)
                elif initial.isidentifier():               # ordinary name
                    if token in ('async', 'await'):
                        if async_def:
                            yield TokenInfo(
                                ASYNC if token == 'async' else AWAIT,
                                token, spos, epos, line)
                            continue

                    tok = TokenInfo(NAME, token, spos, epos, line)
                    if token == 'async' and not stashed:
                        stashed = tok
                        continue

                    if token == 'def':
                        if (stashed
                                and stashed.type == NAME
                                and stashed.string == 'async'):

                            async_def = True
                            async_def_indent = indents[-1]

                            yield TokenInfo(ASYNC, stashed.string,
                                            stashed.start, stashed.end,
                                            stashed.line)
                            stashed = None

                    if stashed:
                        yield stashed
                        stashed = None

                    yield tok
                elif initial == '\\':                      # continued stmt
                    continued = 1
                else:
                    if initial in '([{':
                        parenlev += 1
                    elif initial in ')]}':
                        parenlev -= 1
                    elif token in additional_parenlevs:
                        parenlev += 1
                    if stashed:
                        yield stashed
                        stashed = None
                    yield TokenInfo(OP, token, spos, epos, line)
            else:
                yield TokenInfo(ERRORTOKEN, line[pos],
                           (lnum, pos), (lnum, pos+1), line)
                pos += 1

    if stashed:
        yield stashed
        stashed = None

    for indent in indents[1:]:                 # pop remaining indent levels
        yield TokenInfo(DEDENT, '', (lnum, 0), (lnum, 0), '')
    yield TokenInfo(ENDMARKER, '', (lnum, 0), (lnum, 0), '')


def tokenize(readline):
    """
    The tokenize() generator requires one argment, readline, which
    must be a callable object which provides the same interface as the
    readline() method of built-in file objects.  Each call to the function
    should return one line of input as bytes.  Alternately, readline
    can be a callable function terminating with StopIteration:
        readline = open(myfile, 'rb').__next__  # Example of alternate readline

    The generator produces 5-tuples with these members: the token type; the
    token string; a 2-tuple (srow, scol) of ints specifying the row and
    column where the token begins in the source; a 2-tuple (erow, ecol) of
    ints specifying the row and column where the token ends in the source;
    and the line on which the token was found.  The line passed is the
    logical line; continuation lines are included.

    The first token sequence will always be an ENCODING token
    which tells you which encoding was used to decode the bytes stream.
    """
    # This import is here to avoid problems when the itertools module is not
    # built yet and tokenize is imported.
    from itertools import chain, repeat
    encoding, consumed = detect_encoding(readline)
    rl_gen = iter(readline, b"")
    empty = repeat(b"")
    return _tokenize(chain(consumed, rl_gen, empty).__next__, encoding)


# An undocumented, backwards compatible, API for all the places in the standard
# library that expect to be able to use tokenize with strings
def generate_tokens(readline):
    return _tokenize(readline, None)

def tokenize_main():
    import argparse

    # Helper error handling routines
    def perror(message):
        print(message, file=sys.stderr)

    def error(message, filename=None, location=None):
        if location:
            args = (filename,) + location + (message,)
            perror("%s:%d:%d: error: %s" % args)
        elif filename:
            perror("%s: error: %s" % (filename, message))
        else:
            perror("error: %s" % message)
        sys.exit(1)

    # Parse the arguments and options
    parser = argparse.ArgumentParser(prog='python -m tokenize')
    parser.add_argument(dest='filename', nargs='?',
                        metavar='filename.py',
                        help='the file to tokenize; defaults to stdin')
    parser.add_argument('-e', '--exact', dest='exact', action='store_true',
                        help='display token names using the exact type')
    args = parser.parse_args()

    try:
        # Tokenize the input
        if args.filename:
            filename = args.filename
            with _builtin_open(filename, 'rb') as f:
                tokens = list(tokenize(f.readline))
        else:
            filename = "<stdin>"
            tokens = _tokenize(sys.stdin.readline, None)

        # Output the tokenization
        for token in tokens:
            token_type = token.type
            if args.exact:
                token_type = token.exact_type
            token_range = "%d,%d-%d,%d:" % (token.start + token.end)
            print("%-20s%-15s%-15r" %
                  (token_range, tok_name[token_type], token.string))
    except IndentationError as err:
        line, column = err.args[1][1:3]
        error(err.args[0], filename, (line, column))
    except TokenError as err:
        line, column = err.args[1]
        error(err.args[0], filename, (line, column))
    except SyntaxError as err:
        error(err, filename)
    except OSError as err:
        error(err)
    except KeyboardInterrupt:
        print("interrupted\n")
    except Exception as err:
        perror("unexpected error: %s" % err)
        raise

#
# tools
#
# -*- coding: utf-8 -*-
"""Misc. xonsh tools.

The following implementations were forked from the IPython project:

* Copyright (c) 2008-2014, IPython Development Team
* Copyright (C) 2001-2007 Fernando Perez <fperez@colorado.edu>
* Copyright (c) 2001, Janko Hauser <jhauser@zscout.de>
* Copyright (c) 2001, Nathaniel Gray <n8gray@caltech.edu>

Implementations:

* decode()
* encode()
* cast_unicode()
* safe_hasattr()
* indent()

"""
# amalgamated builtins
# amalgamated collections
# amalgamated collections.abc
# amalgamated ctypes
# amalgamated functools
glob = _LazyModule.load('glob', 'glob')
# amalgamated os
# amalgamated pathlib
# amalgamated re
# amalgamated string
# amalgamated subprocess
# amalgamated sys
# amalgamated threading
traceback = _LazyModule.load('traceback', 'traceback')
# amalgamated warnings
# amalgamated from contextlib import contextmanager
from subprocess import CalledProcessError

# adding further imports from xonsh modules is discouraged to avoid circular
# dependencies
# amalgamated xonsh.lazyasd
# amalgamated xonsh.platform
@functools.lru_cache(1)
def is_superuser():
    if ON_WINDOWS:
        rtn = (ctypes.windll.shell32.IsUserAnAdmin() != 0)
    else:
        rtn = (os.getuid() == 0)
    return rtn


class XonshError(Exception):
    pass


class XonshBlockError(XonshError):
    """Special xonsh exception for communicating the lines of block bodies."""

    def __init__(self, lines, glbs, locs, *args, **kwargs):
        """
        Parameters
        ----------
        lines : list f str
            Block lines, as if split by str.splitlines().
        glbs : Mapping or None
            Global execution context for lines, ie globals() of calling frame.
        locs : Mapping or None
            Local execution context for lines, ie locals() of calling frame.
        """
        super().__init__(*args, **kwargs)
        self.lines = lines
        self.glbs = glbs
        self.locs = locs


class XonshCalledProcessError(XonshError, CalledProcessError):
    """Raised when there's an error with a called process

    Inherits from XonshError and subprocess.CalledProcessError, catching
    either will also catch this error.

    Raised *after* iterating over stdout of a captured command, if the
    returncode of the command is nonzero.

    Example:
        try:
            for line in !(ls):
                print(line)
        except CalledProcessError as error:
            print("Error in process: {}.format(error.completed_command.pid))

    This also handles differences between Python3.4 and 3.5 where
    CalledProcessError is concerned.
    """
    def __init__(self, returncode, command, output=None, stderr=None,
                 completed_command=None):
        super().__init__(returncode, command, output)
        self.stderr = stderr
        self.completed_command = completed_command


def expandpath(path):
    """Performs environment variable / user expansion on a given path
    if the relevant flag has been set.
    """
    env = getattr(builtins, '__xonsh_env__', os.environ)
    if env.get('EXPAND_ENV_VARS', False):
        path = os.path.expanduser(expandvars(path))
    return path


def decode_bytes(path):
    """Tries to decode a path in bytes using XONSH_ENCODING if available,
    otherwise using sys.getdefaultencoding().
    """
    env = getattr(builtins, '__xonsh_env__', os.environ)
    enc = env.get('XONSH_ENCODING', DEFAULT_ENCODING)
    return path.decode(encoding=enc,
                       errors=env.get('XONSH_ENCODING_ERRORS') or 'strict')


class EnvPath(collections.MutableSequence):
    """A class that implements an environment path, which is a list of
    strings. Provides a custom method that expands all paths if the
    relevant env variable has been set.
    """
    def __init__(self, args=None):
        if not args:
            self._l = []
        else:
            if isinstance(args, str):
                self._l = args.split(os.pathsep)
            elif isinstance(args, pathlib.Path):
                self._l = [args]
            elif isinstance(args, bytes):
                # decode bytes to a string and then split based on
                # the default path separator
                self._l = decode_bytes(args).split(os.pathsep)
            elif isinstance(args, collections.Iterable):
                # put everything in a list -before- performing the type check
                # in order to be able to retrieve it later, for cases such as
                # when a generator expression was passed as an argument
                args = list(args)
                if not all(isinstance(i, (str, bytes, pathlib.Path))
                           for i in args):
                    # make TypeError's message as informative as possible
                    # when given an invalid initialization sequence
                    raise TypeError(
                            "EnvPath's initialization sequence should only "
                            "contain str, bytes and pathlib.Path entries")
                self._l = args
            else:
                raise TypeError('EnvPath cannot be initialized with items '
                                'of type %s' % type(args))

    def __getitem__(self, item):
        # handle slices separately
        if isinstance(item, slice):
            return [expandpath(i) for i in self._l[item]]
        else:
            return expandpath(self._l[item])

    def __setitem__(self, index, item):
        self._l.__setitem__(index, item)

    def __len__(self):
        return len(self._l)

    def __delitem__(self, key):
        self._l.__delitem__(key)

    def insert(self, index, value):
        self._l.insert(index, value)

    @property
    def paths(self):
        """
        Returns the list of directories that this EnvPath contains.
        """
        return list(self)

    def __repr__(self):
        return repr(self._l)


class DefaultNotGivenType(object):
    """Singleton for representing when no default value is given."""

    __inst = None

    def __new__(cls):
        if DefaultNotGivenType.__inst is None:
            DefaultNotGivenType.__inst = object.__new__(cls)
        return DefaultNotGivenType.__inst


DefaultNotGiven = DefaultNotGivenType()

BEG_TOK_SKIPS = LazyObject(
                    lambda: frozenset(['WS', 'INDENT', 'NOT', 'LPAREN']),
                    globals(), 'BEG_TOK_SKIPS')
END_TOK_TYPES = LazyObject(lambda: frozenset(['SEMI', 'AND', 'OR', 'RPAREN']),
                           globals(), 'END_TOK_TYPES')
RE_END_TOKS = LazyObject(lambda: re.compile('(;|and|\&\&|or|\|\||\))'),
                         globals(), 'RE_END_TOKS')
LPARENS = LazyObject(lambda: frozenset(['LPAREN', 'AT_LPAREN', 'BANG_LPAREN',
                                        'DOLLAR_LPAREN', 'ATDOLLAR_LPAREN']),
                     globals(), 'LPARENS')


def _is_not_lparen_and_rparen(lparens, rtok):
    """Tests if an RPAREN token is matched with something other than a plain old
    LPAREN type.
    """
    # note that any([]) is False, so this covers len(lparens) == 0
    return rtok.type == 'RPAREN' and any(x != 'LPAREN' for x in lparens)


def find_next_break(line, mincol=0, lexer=None):
    """Returns the column number of the next logical break in subproc mode.
    This function may be useful in finding the maxcol argument of
    subproc_toks().
    """
    if mincol >= 1:
        line = line[mincol:]
    if lexer is None:
        lexer = builtins.__xonsh_execer__.parser.lexer
    if RE_END_TOKS.search(line) is None:
        return None
    maxcol = None
    lparens = []
    lexer.input(line)
    for tok in lexer:
        if tok.type in LPARENS:
            lparens.append(tok.type)
        elif tok.type in END_TOK_TYPES:
            if _is_not_lparen_and_rparen(lparens, tok):
                lparens.pop()
            else:
                maxcol = tok.lexpos + mincol + 1
                break
        elif tok.type == 'ERRORTOKEN' and ')' in tok.value:
            maxcol = tok.lexpos + mincol + 1
            break
    return maxcol


def subproc_toks(line, mincol=-1, maxcol=None, lexer=None, returnline=False):
    """Excapsulates tokens in a source code line in a uncaptured
    subprocess ![] starting at a minimum column. If there are no tokens
    (ie in a comment line) this returns None.
    """
    if lexer is None:
        lexer = builtins.__xonsh_execer__.parser.lexer
    if maxcol is None:
        maxcol = len(line) + 1
    lexer.reset()
    lexer.input(line)
    toks = []
    lparens = []
    end_offset = 0
    for tok in lexer:
        pos = tok.lexpos
        if tok.type not in END_TOK_TYPES and pos >= maxcol:
            break
        if tok.type in LPARENS:
            lparens.append(tok.type)
        if len(toks) == 0 and tok.type in BEG_TOK_SKIPS:
            continue  # handle indentation
        elif len(toks) > 0 and toks[-1].type in END_TOK_TYPES:
            if _is_not_lparen_and_rparen(lparens, toks[-1]):
                lparens.pop()  # don't continue or break
            elif pos < maxcol and tok.type not in ('NEWLINE', 'DEDENT', 'WS'):
                toks.clear()
                if tok.type in BEG_TOK_SKIPS:
                    continue
            else:
                break
        if pos < mincol:
            continue
        toks.append(tok)
        if tok.type == 'NEWLINE':
            break
        elif tok.type == 'DEDENT':
            # fake a newline when dedenting without a newline
            tok.type = 'NEWLINE'
            tok.value = '\n'
            tok.lineno -= 1
            if len(toks) >= 2:
                prev_tok_end = toks[-2].lexpos + len(toks[-2].value)
            else:
                prev_tok_end = len(line)
            if '#' in line[prev_tok_end:]:
                tok.lexpos = prev_tok_end  # prevents wrapping comments
            else:
                tok.lexpos = len(line)
            break
    else:
        if len(toks) > 0 and toks[-1].type in END_TOK_TYPES:
            if _is_not_lparen_and_rparen(lparens, toks[-1]):
                pass
            else:
                toks.pop()
        if len(toks) == 0:
            return  # handle comment lines
        tok = toks[-1]
        pos = tok.lexpos
        if isinstance(tok.value, str):
            end_offset = len(tok.value.rstrip())
        else:
            el = line[pos:].split('#')[0].rstrip()
            end_offset = len(el)
    if len(toks) == 0:
        return  # handle comment lines
    beg, end = toks[0].lexpos, (toks[-1].lexpos + end_offset)
    end = len(line[:end].rstrip())
    rtn = '![' + line[beg:end] + ']'
    if returnline:
        rtn = line[:beg] + rtn + line[end:]
    return rtn


def subexpr_from_unbalanced(expr, ltok, rtok):
    """Attempts to pull out a valid subexpression for unbalanced grouping,
    based on opening tokens, eg. '(', and closing tokens, eg. ')'.  This
    does not do full tokenization, but should be good enough for tab
    completion.
    """
    lcnt = expr.count(ltok)
    if lcnt == 0:
        return expr
    rcnt = expr.count(rtok)
    if lcnt == rcnt:
        return expr
    subexpr = expr.rsplit(ltok, 1)[-1]
    subexpr = subexpr.rsplit(',', 1)[-1]
    subexpr = subexpr.rsplit(':', 1)[-1]
    return subexpr


def decode(s, encoding=None):
    encoding = encoding or DEFAULT_ENCODING
    return s.decode(encoding, "replace")


def encode(u, encoding=None):
    encoding = encoding or DEFAULT_ENCODING
    return u.encode(encoding, "replace")


def cast_unicode(s, encoding=None):
    if isinstance(s, bytes):
        return decode(s, encoding)
    return s


def safe_hasattr(obj, attr):
    """In recent versions of Python, hasattr() only catches AttributeError.
    This catches all errors.
    """
    try:
        getattr(obj, attr)
        return True
    except Exception:  # pylint:disable=bare-except
        return False


def indent(instr, nspaces=4, ntabs=0, flatten=False):
    """Indent a string a given number of spaces or tabstops.

    indent(str,nspaces=4,ntabs=0) -> indent str by ntabs+nspaces.

    Parameters
    ----------
    instr : basestring
        The string to be indented.
    nspaces : int (default: 4)
        The number of spaces to be indented.
    ntabs : int (default: 0)
        The number of tabs to be indented.
    flatten : bool (default: False)
        Whether to scrub existing indentation.  If True, all lines will be
        aligned to the same indentation.  If False, existing indentation will
        be strictly increased.

    Returns
    -------
    outstr : string indented by ntabs and nspaces.

    """
    if instr is None:
        return
    ind = '\t' * ntabs + ' ' * nspaces
    if flatten:
        pat = re.compile(r'^\s*', re.MULTILINE)
    else:
        pat = re.compile(r'^', re.MULTILINE)
    outstr = re.sub(pat, ind, instr)
    if outstr.endswith(os.linesep + ind):
        return outstr[:-len(ind)]
    else:
        return outstr


def get_sep():
    """ Returns the appropriate filepath separator char depending on OS and
    xonsh options set
    """
    if ON_WINDOWS and builtins.__xonsh_env__.get('FORCE_POSIX_PATHS'):
        return os.altsep
    else:
        return os.sep


def fallback(cond, backup):
    """Decorator for returning the object if cond is true and a backup if cond
    is false.
    """
    def dec(obj):
        return obj if cond else backup
    return dec


# The following redirect classes were taken directly from Python 3.5's source
# code (from the contextlib module). This can be removed when 3.5 is released,
# although redirect_stdout exists in 3.4, redirect_stderr does not.
# See the Python software license: https://docs.python.org/3/license.html
# Copyright (c) Python Software Foundation. All rights reserved.
class _RedirectStream:

    _stream = None

    def __init__(self, new_target):
        self._new_target = new_target
        # We use a list of old targets to make this CM re-entrant
        self._old_targets = []

    def __enter__(self):
        self._old_targets.append(getattr(sys, self._stream))
        setattr(sys, self._stream, self._new_target)
        return self._new_target

    def __exit__(self, exctype, excinst, exctb):
        setattr(sys, self._stream, self._old_targets.pop())


class redirect_stdout(_RedirectStream):
    """Context manager for temporarily redirecting stdout to another file::

        # How to send help() to stderr
        with redirect_stdout(sys.stderr):
            help(dir)

        # How to write help() to a file
        with open('help.txt', 'w') as f:
            with redirect_stdout(f):
                help(pow)

    Mostly for backwards compatibility.
    """
    _stream = "stdout"


class redirect_stderr(_RedirectStream):
    """Context manager for temporarily redirecting stderr to another file."""
    _stream = "stderr"


def _yield_accessible_unix_file_names(path):
    """yield file names of executable files in path."""
    if not os.path.exists(path):
        return
    for file_ in scandir(path):
        try:
            if file_.is_file() and os.access(file_.path, os.X_OK):
                yield file_.name
        except (FileNotFoundError, NotADirectoryError):
            # broken Symlink are neither dir not files
            pass


def _executables_in_posix(path):
    if not os.path.exists(path):
        return
    elif PYTHON_VERSION_INFO < (3, 5, 0):
        for fname in os.listdir(path):
            fpath = os.path.join(path, fname)
            if (os.path.exists(fpath) and
                    os.access(fpath, os.X_OK) and
                    (not os.path.isdir(fpath))):
                yield fname
    else:
        yield from _yield_accessible_unix_file_names(path)


def _executables_in_windows(path):
    if not os.path.isdir(path):
        return
    extensions = builtins.__xonsh_env__['PATHEXT']
    if PYTHON_VERSION_INFO < (3, 5, 0):
        for fname in os.listdir(path):
            fpath = os.path.join(path, fname)
            if (os.path.exists(fpath) and not os.path.isdir(fpath)):
                base_name, ext = os.path.splitext(fname)
                if ext.upper() in extensions:
                    yield fname
    else:
        for x in scandir(path):
            if x.is_file():
                fname = x.name
            else:
                continue
            base_name, ext = os.path.splitext(fname)
            if ext.upper() in extensions:
                yield fname


def executables_in(path):
    """Returns a generator of files in path that the user could execute. """
    if ON_WINDOWS:
        func = _executables_in_windows
    else:
        func = _executables_in_posix
    try:
        yield from func(path)
    except PermissionError:
        return


def command_not_found(cmd):
    """Uses the debian/ubuntu command-not-found utility to suggest packages for a
    command that cannot currently be found.
    """
    if not ON_LINUX:
        return ''
    elif not os.path.isfile('/usr/lib/command-not-found'):
        # utility is not on PATH
        return ''
    c = '/usr/lib/command-not-found {0}; exit 0'
    s = subprocess.check_output(c.format(cmd), universal_newlines=True,
                                stderr=subprocess.STDOUT, shell=True)
    s = '\n'.join(s.splitlines()[:-1]).strip()
    return s


def suggest_commands(cmd, env, aliases):
    """Suggests alternative commands given an environment and aliases."""
    if not env.get('SUGGEST_COMMANDS'):
        return
    thresh = env.get('SUGGEST_THRESHOLD')
    max_sugg = env.get('SUGGEST_MAX_NUM')
    if max_sugg < 0:
        max_sugg = float('inf')
    cmd = cmd.lower()
    suggested = {}

    for alias in builtins.aliases:
        if alias not in suggested:
            if levenshtein(alias.lower(), cmd, thresh) < thresh:
                suggested[alias] = 'Alias'

    for path in filter(os.path.isdir, env.get('PATH')):
        for _file in executables_in(path):
            if (_file not in suggested and
                    levenshtein(_file.lower(), cmd, thresh) < thresh):
                suggested[_file] = \
                    'Command ({0})'.format(os.path.join(path, _file))

    suggested = collections.OrderedDict(
        sorted(suggested.items(),
               key=lambda x: suggestion_sort_helper(x[0].lower(), cmd)))
    num = min(len(suggested), max_sugg)

    if num == 0:
        rtn = command_not_found(cmd)
    else:
        oneof = '' if num == 1 else 'one of '
        tips = 'Did you mean {}the following?'.format(oneof)
        items = list(suggested.popitem(False) for _ in range(num))
        length = max(len(key) for key, _ in items) + 2
        alternatives = '\n'.join('    {: <{}} {}'.format(key + ":", length, val)
                                 for key, val in items)
        rtn = '{}\n{}'.format(tips, alternatives)
        c = command_not_found(cmd)
        rtn += ('\n\n' + c) if len(c) > 0 else ''
    return rtn


def print_exception(msg=None):
    """Print exceptions with/without traceback."""
    env = getattr(builtins, '__xonsh_env__', None)
    # flags indicating whether the traceback options have been manually set
    if env is None:
        env = os.environ
        manually_set_trace = 'XONSH_SHOW_TRACEBACK' in env
        manually_set_logfile ='XONSH_TRACEBACK_LOGFILE' in env
    else:
        manually_set_trace = env.is_manually_set('XONSH_SHOW_TRACEBACK')
        manually_set_logfile = env.is_manually_set('XONSH_TRACEBACK_LOGFILE')
    if (not manually_set_trace) and (not manually_set_logfile):
        # Notify about the traceback output possibility if neither of
        # the two options have been manually set
        sys.stderr.write('xonsh: For full traceback set: '
                         '$XONSH_SHOW_TRACEBACK = True\n')
    # get env option for traceback and convert it if necessary
    show_trace = env.get('XONSH_SHOW_TRACEBACK', False)
    if not is_bool(show_trace):
        show_trace = to_bool(show_trace)
    # if the trace option has been set, print all traceback info to stderr
    if show_trace:
        # notify user about XONSH_TRACEBACK_LOGFILE if it has
        # not been set manually
        if not manually_set_logfile:
            sys.stderr.write('xonsh: To log full traceback to a file set: '
                             '$XONSH_TRACEBACK_LOGFILE = <filename>\n')
        traceback.print_exc()
    # additionally, check if a file for traceback logging has been
    # specified and convert to a proper option if needed
    log_file = env.get('XONSH_TRACEBACK_LOGFILE', None)
    log_file = to_logfile_opt(log_file)
    if log_file:
        # if log_file <> '' or log_file <> None, append
        # traceback log there as well
        with open(os.path.abspath(log_file), 'a') as f:
            traceback.print_exc(file=f)

    if not show_trace:
        # if traceback output is disabled, print the exception's
        # error message on stderr.
        display_error_message()
    if msg:
        msg = msg if msg.endswith('\n') else msg + '\n'
        sys.stderr.write(msg)


def display_error_message():
    """
    Prints the error message of the current exception on stderr.
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    exception_only = traceback.format_exception_only(exc_type, exc_value)
    sys.stderr.write(''.join(exception_only))


def is_writable_file(filepath):
    """
    Checks if a filepath is valid for writing.
    """
    # convert to absolute path if needed
    if not os.path.isabs(filepath):
        filepath = os.path.abspath(filepath)
    # cannot write to directories
    if os.path.isdir(filepath):
        return False
    # if the file exists and is writable, we're fine
    if os.path.exists(filepath):
        return True if os.access(filepath, os.W_OK) else False
    # if the path doesn't exist, isolate its directory component
    # and ensure that directory is writable instead
    return os.access(os.path.dirname(filepath), os.W_OK)


# Modified from Public Domain code, by Magnus Lie Hetland
# from http://hetland.org/coding/python/levenshtein.py
def levenshtein(a, b, max_dist=float('inf')):
    """Calculates the Levenshtein distance between a and b."""
    n, m = len(a), len(b)
    if abs(n - m) > max_dist:
        return float('inf')
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a, b = b, a
        n, m = m, n
    current = range(n + 1)
    for i in range(1, m + 1):
        previous, current = current, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete = previous[j] + 1, current[j - 1] + 1
            change = previous[j - 1]
            if a[j - 1] != b[i - 1]:
                change = change + 1
            current[j] = min(add, delete, change)
    return current[n]


def suggestion_sort_helper(x, y):
    """Returns a score (lower is better) for x based on how similar
    it is to y.  Used to rank suggestions."""
    x = x.lower()
    y = y.lower()
    lendiff = len(x) + len(y)
    inx = len([i for i in x if i not in y])
    iny = len([i for i in y if i not in x])
    return lendiff + inx + iny


def escape_windows_cmd_string(s):
    """Returns a string that is usable by the Windows cmd.exe.
    The escaping is based on details here and emperical testing:
    http://www.robvanderwoude.com/escapechars.php
    """
    for c in '()%!^<>&|"':
        s = s.replace(c, '^' + c)
    s = s.replace('/?', '/.')
    return s


def argvquote(arg, force=False):
    """ Returns an argument quoted in such a way that that CommandLineToArgvW
    on Windows will return the argument string unchanged.
    This is the same thing Popen does when supplied with an list of arguments.
    Arguments in a command line should be separated by spaces; this
    function does not add these spaces. This implementation follows the
    suggestions outlined here:
    https://blogs.msdn.microsoft.com/twistylittlepassagesallalike/2011/04/23/everyone-quotes-command-line-arguments-the-wrong-way/
    """
    if not force and len(arg) != 0 and not any([c in arg for c in ' \t\n\v"']):
        return arg
    else:
        n_backslashes = 0
        cmdline = '"'
        for c in arg:
            if c == '"':
                cmdline += (n_backslashes * 2 + 1) * '\\'
            else:
                cmdline += n_backslashes * '\\'
            if c != '\\':
                cmdline += c
                n_backslashes = 0
            else:
                n_backslashes += 1
        return cmdline + n_backslashes * 2 * '\\' + '"'


def on_main_thread():
    """Checks if we are on the main thread or not."""
    return threading.current_thread() is threading.main_thread()


@contextmanager
def swap(namespace, name, value, default=NotImplemented):
    """Swaps a current variable name in a namespace for another value, and then
    replaces it when the context is exited.
    """
    old = getattr(namespace, name, default)
    setattr(namespace, name, value)
    yield value
    if old is default:
        delattr(namespace, name)
    else:
        setattr(namespace, name, old)

#
# Validators and converters
#


def is_int(x):
    """Tests if something is an integer"""
    return isinstance(x, int)


def is_int_as_str(x):
    """
    Tests if something is an integer
    If not a string to begin with is automatically false
    """
    if isinstance(x, str):
        try:
            int(x)
        except ValueError:
            return False
        return True
    return False


def is_float(x):
    """Tests if something is a float"""
    return isinstance(x, float)


def is_string(x):
    """Tests if something is a string"""
    return isinstance(x, str)


def is_slice(x):
    """Tests if something is a slice"""
    return isinstance(x, slice)


def is_slice_as_str(x):
    """
    Tests if a str is a slice
    If not a string to begin with is automatically false
    """
    if isinstance(x, str):
        if ':' in x:
            x = x.strip('[]()')
            try:
                slice(*(int(x) if len(x) > 0 else None
                        for x in x.split(':')))
            except ValueError:
                return False
        else:
            return False
        return True
    return False


def is_callable(x):
    """Tests if something is callable"""
    return callable(x)


def is_string_or_callable(x):
    """Tests if something is a string or callable"""
    return is_string(x) or is_callable(x)


def always_true(x):
    """Returns True"""
    return True


def always_false(x):
    """Returns False"""
    return False


def ensure_string(x):
    """Returns a string if x is not a string, and x if it already is."""
    return str(x)


def is_env_path(x):
    """This tests if something is an environment path, ie a list of strings."""
    return isinstance(x, EnvPath)


def str_to_env_path(x):
    """Converts a string to an environment path, ie a list of strings,
    splitting on the OS separator.
    """
    # splitting will be done implicitly in EnvPath's __init__
    return EnvPath(x)


def env_path_to_str(x):
    """Converts an environment path to a string by joining on the OS
    separator.
    """
    return os.pathsep.join(x)


def is_bool(x):
    """Tests if something is a boolean."""
    return isinstance(x, bool)


def is_logfile_opt(x):
    """
    Checks if x is a valid $XONSH_TRACEBACK_LOGFILE option. Returns False
    if x is not a writable/creatable file or an empty string or None.
    """
    if x is None:
        return True
    if not isinstance(x, str):
        return False
    else:
        return (is_writable_file(x) or x == '')


def to_logfile_opt(x):
    """
    Converts a $XONSH_TRACEBACK_LOGFILE option to either a str containing
    the filepath if it is a writable file or None if the filepath is not
    valid, informing the user on stderr about the invalid choice.
    """
    if is_logfile_opt(x):
        return x
    else:
        # if option is not valid, return a proper
        # option and inform the user on stderr
        sys.stderr.write('xonsh: $XONSH_TRACEBACK_LOGFILE must be a '
                         'filepath pointing to a file that either exists '
                         'and is writable or that can be created.\n')
        return None


def logfile_opt_to_str(x):
    """
    Detypes a $XONSH_TRACEBACK_LOGFILE option.
    """
    if x is None:
        # None should not be detyped to 'None', as 'None' constitutes
        # a perfectly valid filename and retyping it would introduce
        # ambiguity. Detype to the empty string instead.
        return ''
    return str(x)


_FALSES = LazyObject(lambda: frozenset(['', '0', 'n', 'f', 'no', 'none',
                                        'false']), globals(), '_FALSES')


def to_bool(x):
    """"Converts to a boolean in a semantically meaningful way."""
    if isinstance(x, bool):
        return x
    elif isinstance(x, str):
        return False if x.lower() in _FALSES else True
    else:
        return bool(x)


def bool_to_str(x):
    """Converts a bool to an empty string if False and the string '1' if
    True.
    """
    return '1' if x else ''


_BREAKS = frozenset(['b', 'break', 's', 'skip', 'q', 'quit'])


def to_bool_or_break(x):
    if isinstance(x, str) and x.lower() in _BREAKS:
        return 'break'
    else:
        return to_bool(x)


def is_bool_or_int(x):
    """Returns whether a value is a boolean or integer."""
    return is_bool(x) or is_int(x)


def to_bool_or_int(x):
    """Converts a value to a boolean or an integer."""
    if isinstance(x, str):
        return int(x) if x.isdigit() else to_bool(x)
    elif is_int(x):  # bools are ints too!
        return x
    else:
        return bool(x)


def bool_or_int_to_str(x):
    """Converts a boolean or integer to a string."""
    return bool_to_str(x) if is_bool(x) else str(x)


def ensure_int_or_slice(x):
    """Makes sure that x is list-indexable."""
    if x is None:
        return slice(None)
    elif is_int(x) or is_slice(x):
        return x
    # must have a string from here on
    if is_slice_as_str(x):
        x = x.strip('[]()')
        return slice(*(int(x) if len(x) > 0 else None for x in x.split(':')))
    elif is_int_as_str(x):
        return int(x)
    return False


def is_string_set(x):
    """Tests if something is a set of strings"""
    return (isinstance(x, abc.Set) and
            all(isinstance(a, str) for a in x))


def csv_to_set(x):
    """Convert a comma-separated list of strings to a set of strings."""
    if not x:
        return set()
    else:
        return set(x.split(','))


def set_to_csv(x):
    """Convert a set of strings to a comma-separated list of strings."""
    return ','.join(x)


def pathsep_to_set(x):
    """Converts a os.pathsep separated string to a set of strings."""
    if not x:
        return set()
    else:
        return set(x.split(os.pathsep))


def set_to_pathsep(x, sort=False):
    """Converts a set to an os.pathsep separated string. The sort kwarg
    specifies whether to sort the set prior to str conversion.
    """
    if sort:
        x = sorted(x)
    return os.pathsep.join(x)


def is_string_seq(x):
    """Tests if something is a sequence of strings"""
    return (isinstance(x, abc.Sequence) and
            all(isinstance(a, str) for a in x))


def is_nonstring_seq_of_strings(x):
    """Tests if something is a sequence of strings, where the top-level
    sequence is not a string itself.
    """
    return (isinstance(x, abc.Sequence) and not isinstance(x, str) and
            all(isinstance(a, str) for a in x))


def pathsep_to_seq(x):
    """Converts a os.pathsep separated string to a sequence of strings."""
    if not x:
        return []
    else:
        return x.split(os.pathsep)


def seq_to_pathsep(x):
    """Converts a sequence to an os.pathsep separated string."""
    return os.pathsep.join(x)


def pathsep_to_upper_seq(x):
    """Converts a os.pathsep separated string to a sequence of
    uppercase strings.
    """
    if not x:
        return []
    else:
        return x.upper().split(os.pathsep)


def seq_to_upper_pathsep(x):
    """Converts a sequence to an uppercase os.pathsep separated string."""
    return os.pathsep.join(x).upper()


def is_bool_seq(x):
    """Tests if an object is a sequence of bools."""
    return isinstance(x, abc.Sequence) and all(isinstance(y, bool) for y in x)


def csv_to_bool_seq(x):
    """Takes a comma-separated string and converts it into a list of bools."""
    return [to_bool(y) for y in csv_to_set(x)]


def bool_seq_to_csv(x):
    """Converts a sequence of bools to a comma-separated string."""
    return ','.join(map(str, x))


def is_completions_display_value(x):
    return x in {'none', 'single', 'multi'}


def to_completions_display_value(x):
    x = str(x).lower()
    if x in {'none', 'false'}:
        x = 'none'
    elif x in {'multi', 'true'}:
        x = 'multi'
    elif x == 'single':
        pass
    else:
        msg = '"{}" is not a valid value for $COMPLETIONS_DISPLAY. '.format(x)
        msg += 'Using "multi".'
        warnings.warn(msg, RuntimeWarning)
        x = 'multi'
    return x


def setup_win_unicode_console(enable):
    """"Enables or disables unicode display on windows."""
    try:
        import win_unicode_console
    except ImportError:
        win_unicode_console = False
    enable = to_bool(enable)
    if ON_WINDOWS and win_unicode_console:
        if enable:
            win_unicode_console.enable()
        else:
            win_unicode_console.disable()
    return enable

# history validation

_min_to_sec = lambda x: 60.0 * float(x)
_hour_to_sec = lambda x: 60.0 * _min_to_sec(x)
_day_to_sec = lambda x: 24.0 * _hour_to_sec(x)
_month_to_sec = lambda x: 30.4375 * _day_to_sec(x)
_year_to_sec = lambda x: 365.25 * _day_to_sec(x)
_kb_to_b = lambda x: 1024 * int(x)
_mb_to_b = lambda x: 1024 * _kb_to_b(x)
_gb_to_b = lambda x: 1024 * _mb_to_b(x)
_tb_to_b = lambda x: 1024 * _tb_to_b(x)

CANON_HISTORY_UNITS = LazyObject(
    lambda: frozenset(['commands', 'files', 's', 'b']),
    globals(), 'CANON_HISTORY_UNITS')

HISTORY_UNITS = LazyObject(lambda: {
    '': ('commands', int),
    'c': ('commands', int),
    'cmd': ('commands', int),
    'cmds': ('commands', int),
    'command': ('commands', int),
    'commands': ('commands', int),
    'f': ('files', int),
    'files': ('files', int),
    's': ('s', float),
    'sec': ('s', float),
    'second': ('s', float),
    'seconds': ('s', float),
    'm': ('s', _min_to_sec),
    'min': ('s', _min_to_sec),
    'mins': ('s', _min_to_sec),
    'h': ('s', _hour_to_sec),
    'hr': ('s', _hour_to_sec),
    'hour': ('s', _hour_to_sec),
    'hours': ('s', _hour_to_sec),
    'd': ('s', _day_to_sec),
    'day': ('s', _day_to_sec),
    'days': ('s', _day_to_sec),
    'mon': ('s', _month_to_sec),
    'month': ('s', _month_to_sec),
    'months': ('s', _month_to_sec),
    'y': ('s', _year_to_sec),
    'yr': ('s', _year_to_sec),
    'yrs': ('s', _year_to_sec),
    'year': ('s', _year_to_sec),
    'years': ('s', _year_to_sec),
    'b': ('b', int),
    'byte': ('b', int),
    'bytes': ('b', int),
    'kb': ('b', _kb_to_b),
    'kilobyte': ('b', _kb_to_b),
    'kilobytes': ('b', _kb_to_b),
    'mb': ('b', _mb_to_b),
    'meg': ('b', _mb_to_b),
    'megs': ('b', _mb_to_b),
    'megabyte': ('b', _mb_to_b),
    'megabytes': ('b', _mb_to_b),
    'gb': ('b', _gb_to_b),
    'gig': ('b', _gb_to_b),
    'gigs': ('b', _gb_to_b),
    'gigabyte': ('b', _gb_to_b),
    'gigabytes': ('b', _gb_to_b),
    'tb': ('b', _tb_to_b),
    'terabyte': ('b', _tb_to_b),
    'terabytes': ('b', _tb_to_b),
    }, globals(), 'HISTORY_UNITS')
"""Maps lowercase unit names to canonical name and conversion utilities."""


def is_history_tuple(x):
    """Tests if something is a proper history value, units tuple."""
    if (isinstance(x, abc.Sequence) and
            len(x) == 2 and
            isinstance(x[0], (int, float)) and
            x[1].lower() in CANON_HISTORY_UNITS):
        return True
    return False


def is_dynamic_cwd_width(x):
    """ Determine if the input is a valid input for the DYNAMIC_CWD_WIDTH
    environement variable.
    """
    return (isinstance(x, tuple) and
            len(x) == 2 and
            isinstance(x[0], float) and
            x[1] in set('c%'))


def to_dynamic_cwd_tuple(x):
    """Convert to a canonical cwd_width tuple."""
    unit = 'c'
    if isinstance(x, str):
        if x[-1] == '%':
            x = x[:-1]
            unit = '%'
        else:
            unit = 'c'
        return (float(x), unit)
    else:
        return (float(x[0]), x[1])


def dynamic_cwd_tuple_to_str(x):
    """Convert a canonical cwd_width tuple to a string."""
    if x[1] == '%':
        return str(x[0]) + '%'
    else:
        return str(x[0])


RE_HISTORY_TUPLE = LazyObject(
    lambda: re.compile('([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)\s*([A-Za-z]*)'),
    globals(), 'RE_HISTORY_TUPLE')


def to_history_tuple(x):
    """Converts to a canonincal history tuple."""
    if not isinstance(x, (abc.Sequence, float, int)):
        raise ValueError('history size must be given as a sequence or number')
    if isinstance(x, str):
        m = RE_HISTORY_TUPLE.match(x.strip().lower())
        return to_history_tuple((m.group(1), m.group(3)))
    elif isinstance(x, (float, int)):
        return to_history_tuple((x, 'commands'))
    units, converter = HISTORY_UNITS[x[1]]
    value = converter(x[0])
    return (value, units)


def history_tuple_to_str(x):
    """Converts a valid history tuple to a canonical string."""
    return '{0} {1}'.format(*x)


def format_color(string, **kwargs):
    """Formats strings that may contain colors. This simply dispatches to the
    shell instances method of the same name. The results of this function should
    be directly usable by print_color().
    """
    return builtins.__xonsh_shell__.shell.format_color(string, **kwargs)


def print_color(string, **kwargs):
    """Prints a string that may contain colors. This dispatched to the shell
    method of the same name. Colors will be formatted if they have not already
    been.
    """
    builtins.__xonsh_shell__.shell.print_color(string, **kwargs)


def color_style_names():
    """Returns an iterable of all available style names."""
    return builtins.__xonsh_shell__.shell.color_style_names()


def color_style():
    """Returns the current color map."""
    return builtins.__xonsh_shell__.shell.color_style()


def _get_color_indexes(style_map):
    """ Generates the color and windows color index for a style """
    import prompt_toolkit
    table = prompt_toolkit.terminal.win32_output.ColorLookupTable()
    pt_style = prompt_toolkit.styles.style_from_dict(style_map)
    for token in style_map:
        attr = pt_style.token_to_attrs[token]
        if attr.color is not None:
            index = table.lookup_color(attr.color, attr.bgcolor)
            try:
                rgb = (int(attr.color[0:2], 16),
                       int(attr.color[2:4], 16),
                       int(attr.color[4:6], 16))
            except:
                rgb = None
            yield token, index, rgb


def intensify_colors_for_cmd_exe(style_map, replace_colors=None):
    """Returns a modified style to where colors that maps to dark
       colors are replaced with brighter versions. Also expands the
       range used by the gray colors
    """
    modified_style = {}
    stype = builtins.__xonsh_env__.get('SHELL_TYPE')
    if (not ON_WINDOWS or
            (stype not in ('prompt_toolkit', 'best')) or
            (stype == 'best' and not has_prompt_toolkit())):
        return modified_style
    if replace_colors is None:
        replace_colors = {1: '#44ffff',  # subst blue with bright cyan
                          2: '#44ff44',  # subst green with bright green
                          4: '#ff4444',  # subst red with bright red
                          5: '#ff44ff',  # subst magenta with bright magenta
                          6: '#ffff44',  # subst yellow with bright yellow
                          9: '#00aaaa',  # subst intense blue (hard to read)
                                         # with dark cyan (which is readable)
                          }
    for token, idx, _ in _get_color_indexes(style_map):
        if idx in replace_colors:
            modified_style[token] = replace_colors[idx]
    return modified_style


def expand_gray_colors_for_cmd_exe(style_map):
    """ Expand the style's gray scale color range.
        All gray scale colors has a tendency to map to the same default GRAY
        in cmd.exe.
    """
    modified_style = {}
    stype = builtins.__xonsh_env__.get('SHELL_TYPE')
    if (not ON_WINDOWS or
            (stype not in ('prompt_toolkit', 'best')) or
            (stype == 'best' and not has_prompt_toolkit())):
        return modified_style
    for token, idx, rgb in _get_color_indexes(style_map):
        if idx == 7 and rgb:
            if sum(rgb) <= 306:
                # Equal and below '#666666 is reset to dark gray
                modified_style[token] = '#444444'
            elif sum(rgb) >= 408:
                # Equal and above 0x888888 is reset to white
                modified_style[token] = '#ffffff'
    return modified_style


def intensify_colors_on_win_setter(enable):
    """Resets the style when setting the INTENSIFY_COLORS_ON_WIN
    environment variable.
    """
    enable = to_bool(enable)
    delattr(builtins.__xonsh_shell__.shell.styler, 'style_name')
    return enable


_RE_STRING_START = "[bBrRuU]*"
_RE_STRING_TRIPLE_DOUBLE = '"""'
_RE_STRING_TRIPLE_SINGLE = "'''"
_RE_STRING_DOUBLE = '"'
_RE_STRING_SINGLE = "'"
_STRINGS = (_RE_STRING_TRIPLE_DOUBLE,
            _RE_STRING_TRIPLE_SINGLE,
            _RE_STRING_DOUBLE,
            _RE_STRING_SINGLE)
RE_BEGIN_STRING = LazyObject(
    lambda: re.compile("(" + _RE_STRING_START +
                       '(' + "|".join(_STRINGS) + '))'),
    globals(), 'RE_BEGIN_STRING')
"""Regular expression matching the start of a string, including quotes and
leading characters (r, b, or u)"""

RE_STRING_START = LazyObject(lambda: re.compile(_RE_STRING_START),
                             globals(), 'RE_STRING_START')
"""Regular expression matching the characters before the quotes when starting a
string (r, b, or u, case insensitive)"""

RE_STRING_CONT = LazyDict({
    '"': lambda: re.compile(r'((\\(.|\n))|([^"\\]))*'),
    "'": lambda: re.compile(r"((\\(.|\n))|([^'\\]))*"),
    '"""': lambda: re.compile(r'((\\(.|\n))|([^"\\])|("(?!""))|\n)*'),
    "'''": lambda: re.compile(r"((\\(.|\n))|([^'\\])|('(?!''))|\n)*"),
    }, globals(), 'RE_STRING_CONT')
"""Dictionary mapping starting quote sequences to regular expressions that
match the contents of a string beginning with those quotes (not including the
terminating quotes)"""


def check_for_partial_string(x):
    """
    Returns the starting index (inclusive), ending index (exclusive), and
    starting quote string of the most recent Python string found in the input.

    check_for_partial_string(x) -> (startix, endix, quote)

    Parameters
    ----------
    x : str
        The string to be checked (representing a line of terminal input)

    Returns
    -------
    startix : int (or None)
        The index where the most recent Python string found started
        (inclusive), or None if no strings exist in the input

    endix : int (or None)
        The index where the most recent Python string found ended (exclusive),
        or None if no strings exist in the input OR if the input ended in the
        middle of a Python string

    quote : str (or None)
        A string containing the quote used to start the string (e.g., b", ",
        '''), or None if no string was found.
    """
    string_indices = []
    starting_quote = []
    current_index = 0
    match = re.search(RE_BEGIN_STRING, x)
    while match is not None:
        # add the start in
        start = match.start()
        quote = match.group(0)
        lenquote = len(quote)
        current_index += start
        # store the starting index of the string, as well as the
        # characters in the starting quotes (e.g., ", ', """, r", etc)
        string_indices.append(current_index)
        starting_quote.append(quote)
        # determine the string that should terminate this string
        ender = re.sub(RE_STRING_START, '', quote)
        x = x[start + lenquote:]
        current_index += lenquote
        # figure out what is inside the string
        continuer = RE_STRING_CONT[ender]
        contents = re.match(continuer, x)
        inside = contents.group(0)
        leninside = len(inside)
        current_index += contents.start() + leninside + len(ender)
        # if we are not at the end of the input string, add the ending index of
        # the string to string_indices
        if contents.end() < len(x):
            string_indices.append(current_index)
        x = x[leninside + len(ender):]
        # find the next match
        match = re.search(RE_BEGIN_STRING, x)
    numquotes = len(string_indices)
    if numquotes == 0:
        return (None, None, None)
    elif numquotes % 2:
        return (string_indices[-1], None, starting_quote[-1])
    else:
        return (string_indices[-2], string_indices[-1], starting_quote[-1])


# expandvars is a modified version of os.path.expandvars from the Python 3.5.1
# source code (root/Lib/ntpath.py, line 353)

def _is_in_env(name):
    env = builtins.__xonsh_env__
    return name in env._d or name in env._defaults


def _get_env_string(name):
    env = builtins.__xonsh_env__
    value = env.get(name)
    ensurer = env.get_ensurer(name)
    if ensurer.detype is bool_to_str:
        value = ensure_string(value)
    else:
        value = ensurer.detype(value)
    return value


def expandvars(path):
    """Expand shell variables of the forms $var, ${var} and %var%.
    Unknown variables are left unchanged.
    """
    env = builtins.__xonsh_env__
    if isinstance(path, bytes):
        path = path.decode(encoding=env.get('XONSH_ENCODING'),
                           errors=env.get('XONSH_ENCODING_ERRORS'))
    elif isinstance(path, pathlib.Path):
        # get the path's string representation
        path = str(path)
    if '$' not in path and (not ON_WINDOWS or '%' not in path):
        return path
    varchars = string.ascii_letters + string.digits + '_-'
    quote = '\''
    percent = '%'
    brace = '{'
    rbrace = '}'
    dollar = '$'
    res = path[:0]
    index = 0
    pathlen = len(path)
    while index < pathlen:
        c = path[index:index+1]
        if c == quote:   # no expansion within single quotes
            path = path[index + 1:]
            pathlen = len(path)
            try:
                index = path.index(c)
                res += c + path[:index + 1]
            except ValueError:
                res += c + path
                index = pathlen - 1
        elif c == percent and ON_WINDOWS:  # variable or '%'
            if path[index + 1:index + 2] == percent:
                res += c
                index += 1
            else:
                path = path[index+1:]
                pathlen = len(path)
                try:
                    index = path.index(percent)
                except ValueError:
                    res += percent + path
                    index = pathlen - 1
                else:
                    var = path[:index]
                    if _is_in_env(var):
                        value = _get_env_string(var)
                    else:
                        value = percent + var + percent
                    res += value
        elif c == dollar:  # variable or '$$'
            if path[index + 1:index + 2] == dollar:
                res += c
                index += 1
            elif path[index + 1:index + 2] == brace:
                path = path[index+2:]
                pathlen = len(path)
                try:
                    index = path.index(rbrace)
                except ValueError:
                    res += dollar + brace + path
                    index = pathlen - 1
                else:
                    var = path[:index]
                    try:
                        var = eval(var, builtins.__xonsh_ctx__)
                        if _is_in_env(var):
                            value = _get_env_string(var)
                        elif var is Ellipsis:
                            value = dollar + brace + '...' + rbrace
                        else:
                            value = dollar + brace + var + rbrace
                    except:
                        value = dollar + brace + var + rbrace
                    res += value
            else:
                var = path[:0]
                index += 1
                c = path[index:index + 1]
                while c and c in varchars:
                    var += c
                    index += 1
                    c = path[index:index + 1]
                if _is_in_env(var):
                    value = _get_env_string(var)
                else:
                    value = dollar + var
                res += value
                if c:
                    index -= 1
        else:
            res += c
        index += 1
    return res

#
# File handling tools
#


def backup_file(fname):
    """Moves an existing file to a new name that has the current time right
    before the extension.
    """
    # lazy imports
    import shutil
    from datetime import datetime
    base, ext = os.path.splitext(fname)
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')
    newfname = '%s.%s%s' % (base, timestamp, ext)
    shutil.move(fname, newfname)


def normabspath(p):
    """Retuns as normalized absolute path, namely, normcase(abspath(p))"""
    return os.path.normcase(os.path.abspath(p))


def expanduser_abs_path(inp):
    """ Provides user expanded absolute path """
    return os.path.abspath(os.path.expanduser(inp))


WINDOWS_DRIVE_MATCHER = LazyObject(lambda: re.compile(r'^\w:'),
                                   globals(), 'WINDOWS_DRIVE_MATCHER')


def expand_case_matching(s):
    """Expands a string to a case insensitive globable string."""
    t = []
    openers = {'[', '{'}
    closers = {']', '}'}
    nesting = 0

    drive_part = WINDOWS_DRIVE_MATCHER.match(s) if ON_WINDOWS else None

    if drive_part:
        drive_part = drive_part.group(0)
        t.append(drive_part)
        s = s[len(drive_part):]

    for c in s:
        if c in openers:
            nesting += 1
        elif c in closers:
            nesting -= 1
        elif nesting > 0:
            pass
        elif c.isalpha():
            folded = c.casefold()
            if len(folded) == 1:
                c = '[{0}{1}]'.format(c.upper(), c.lower())
            else:
                newc = ['[{0}{1}]?'.format(f.upper(), f.lower())
                        for f in folded[:-1]]
                newc = ''.join(newc)
                newc += '[{0}{1}{2}]'.format(folded[-1].upper(),
                                             folded[-1].lower(),
                                             c)
                c = newc
        t.append(c)
    return ''.join(t)


def globpath(s, ignore_case=False, return_empty=False, sort_result=None):
    """Simple wrapper around glob that also expands home and env vars."""
    o, s = _iglobpath(s, ignore_case=ignore_case, sort_result=sort_result)
    o = list(o)
    no_match = [] if return_empty else [s]
    return o if len(o) != 0 else no_match


def _iglobpath(s, ignore_case=False, sort_result=None):
    s = builtins.__xonsh_expand_path__(s)
    if sort_result is None:
        sort_result = builtins.__xonsh_env__.get('GLOB_SORTED')
    if ignore_case:
        s = expand_case_matching(s)
    if sys.version_info > (3, 5):
        if '**' in s and '**/*' not in s:
            s = s.replace('**', '**/*')
        # `recursive` is only a 3.5+ kwarg.
        if sort_result:
            paths = glob.glob(s, recursive=True)
            paths.sort()
            paths = iter(paths)
        else:
            paths = glob.iglob(s, recursive=True)
        return paths, s
    else:
        if sort_result:
            paths = glob.glob(s)
            paths.sort()
            paths = iter(paths)
        else:
            paths = glob.iglob(s)
        return paths, s


def iglobpath(s, ignore_case=False, sort_result=None):
    """Simple wrapper around iglob that also expands home and env vars."""
    return _iglobpath(s, ignore_case=ignore_case, sort_result=sort_result)[0]

#
# vox
#
# amalgamated os
venv = _LazyModule.load('venv', 'venv')
# amalgamated builtins
shutil = _LazyModule.load('shutil', 'shutil')
# amalgamated xonsh.platform
class Vox:
    """Vox is a virtual environment manager for xonsh."""

    def __init__(self):
        """Ensure that $VIRTUALENV_HOME is defined and declare the available vox commands"""

        if not builtins.__xonsh_env__.get('VIRTUALENV_HOME'):
            home_path = os.path.expanduser('~')
            venvdir = os.path.join(home_path, '.virtualenvs')
            builtins.__xonsh_env__['VIRTUALENV_HOME'] = venvdir

        self.commands = {
            ('new',): self.create_env,
            ('activate', 'workon', 'enter'): self.activate_env,
            ('deactivate', 'exit'): self.deactivate_env,
            ('list', 'ls'): self.list_envs,
            ('remove', 'rm', 'delete', 'del'): self.remove_env,
            ('help', '-h', '--help'): self.show_help
        }

    def __call__(self, args, stdin=None):
        """Call the right handler method for a given command."""

        if not args:
            self.show_help()
            return None

        command_name, params = args[0], args[1:]

        try:
            command = [
                self.commands[aliases] for aliases in self.commands
                if command_name in aliases
            ][0]

            command(*params)

        except IndexError:
            print('Command "%s" doesn\'t exist.\n' % command_name)
            self.print_commands()

    @staticmethod
    def create_env(name):
        """Create a virtual environment in $VIRTUALENV_HOME with python3's ``venv``.

        Parameters
        ----------
        name : str
            Virtual environment name
        """
        env_path = os.path.join(builtins.__xonsh_env__['VIRTUALENV_HOME'], name)
        print('Creating environment...')
        venv.create(env_path, with_pip=True)
        msg = 'Environment {0!r} created. Activate it with "vox activate {0}".\n'
        print(msg.format(name))

    def activate_env(self, name):
        """Activate a virtual environment.

        Parameters
        ----------
        name : str
            Virtual environment name
        """
        env = builtins.__xonsh_env__
        env_path = os.path.join(env['VIRTUALENV_HOME'], name)
        if not os.path.exists(env_path):
            print('This environment doesn\'t exist. Create it with "vox new %s".\n' % name)
            return None
        if ON_WINDOWS:
            bin_dir = 'Scripts'
        elif ON_POSIX:
            bin_dir = 'bin'
        else:
            print('This OS is not supported.')
            return None
        bin_path = os.path.join(env_path, bin_dir)
        if 'VIRTUAL_ENV' in env:
            self.deactivate_env()
        env['PATH'].insert(0, bin_path)
        env['VIRTUAL_ENV'] = env_path
        print('Activated "%s".\n' % name)

    @staticmethod
    def deactivate_env():
        """Deactive the active virtual environment."""

        if 'VIRTUAL_ENV' not in __xonsh_env__:
            print('No environment currently active. Activate one with "vox activate".\n')
            return None

        env_path = __xonsh_env__['VIRTUAL_ENV']

        env_name = os.path.basename(env_path)

        if ON_WINDOWS:
            bin_dir = 'Scripts'

        elif ON_POSIX:
            bin_dir = 'bin'

        else:
            print('This OS is not supported.')
            return None

        bin_path = os.path.join(env_path, bin_dir)

        while bin_path in __xonsh_env__['PATH']:
            __xonsh_env__['PATH'].remove(bin_path)

        __xonsh_env__.pop('VIRTUAL_ENV')

        print('Deactivated "%s".\n' % env_name)

    @staticmethod
    def list_envs():
        """List available virtual environments."""

        venv_home = builtins.__xonsh_env__['VIRTUALENV_HOME']
        try:
            env_dirs = list(x.name for x in scandir(venv_home) if x.is_dir())
        except PermissionError:
            print('No permissions on {}'.format(venv_home))
            return None

        if not env_dirs:
            print('No environments available. Create one with "vox new".\n')
            return None

        print('Available environments:')
        print('\n'.join(env_dirs))


    @staticmethod
    def remove_env(name):
        """Remove virtual environment.

        Parameters
        ----------
        name : str
            virtual environment name
        """
        if 'VIRTUAL_ENV' in __xonsh_env__:
            print('This environment is currently active. If you really want to remove it, deactivate it first with "vox deactivate %s".\n' % name)
            return None
        env_path = os.path.join(builtins.__xonsh_env__['VIRTUALENV_HOME'], name)
        shutil.rmtree(env_path)
        print('Environment "%s" removed.\n' % name)

    def show_help(self):
        """Show help."""

        print(self.__doc__, '\n')
        self.print_commands()

    @staticmethod
    def print_commands():
        """Print available vox commands."""

        print("""Available commands:
    vox new <env>
        Create new virtual environment in $VIRTUALENV_HOME

    vox activate (workon, enter) <env>
        Activate virtual environment

    vox deactivate (exit)
        Deactivate current virtual environment

    vox list (ls)
        List all available environments

    vox remove (rm, delete, del) <env>
        Remove virtual environment

    vox help (-h, --help)
        Show help
""")

#
# ast
#
# -*- coding: utf-8 -*-
"""The xonsh abstract syntax tree node."""
# These are imported into our module namespace for the benefit of parser.py.
# pylint: disable=unused-import
from ast import Module, Num, Expr, Str, Bytes, UnaryOp, UAdd, USub, Invert, \
    BinOp, Add, Sub, Mult, Div, FloorDiv, Mod, Pow, Compare, Lt, Gt, \
    LtE, GtE, Eq, NotEq, In, NotIn, Is, IsNot, Not, BoolOp, Or, And, \
    Subscript, Load, Slice, ExtSlice, List, Tuple, Set, Dict, AST, NameConstant, \
    Name, GeneratorExp, Store, comprehension, ListComp, SetComp, DictComp, \
    Assign, AugAssign, BitXor, BitAnd, BitOr, LShift, RShift, Assert, Delete, \
    Del, Pass, Raise, Import, alias, ImportFrom, Continue, Break, Yield, \
    YieldFrom, Return, IfExp, Lambda, arguments, arg, Call, keyword, \
    Attribute, Global, Nonlocal, If, While, For, withitem, With, Try, \
    ExceptHandler, FunctionDef, ClassDef, Starred, NodeTransformer, \
    Interactive, Expression, Index, literal_eval, dump, walk, increment_lineno
from ast import Ellipsis as EllipsisNode
# pylint: enable=unused-import
textwrap = _LazyModule.load('textwrap', 'textwrap')
# amalgamated itertools
# amalgamated xonsh.tools
# amalgamated xonsh.platform
if PYTHON_VERSION_INFO >= (3, 5, 0):
    # pylint: disable=unused-import
    # pylint: disable=no-name-in-module
    from ast import MatMult, AsyncFunctionDef, AsyncWith, AsyncFor, Await
else:
    MatMult = AsyncFunctionDef = AsyncWith = AsyncFor = Await = None

STATEMENTS = (FunctionDef, ClassDef, Return, Delete, Assign, AugAssign, For,
              While, If, With, Raise, Try, Assert, Import, ImportFrom, Global,
              Nonlocal, Expr, Pass, Break, Continue)


def leftmostname(node):
    """Attempts to find the first name in the tree."""
    if isinstance(node, Name):
        rtn = node.id
    elif isinstance(node, (BinOp, Compare)):
        rtn = leftmostname(node.left)
    elif isinstance(node, (Attribute, Subscript, Starred, Expr)):
        rtn = leftmostname(node.value)
    elif isinstance(node, Call):
        rtn = leftmostname(node.func)
    elif isinstance(node, UnaryOp):
        rtn = leftmostname(node.operand)
    elif isinstance(node, BoolOp):
        rtn = leftmostname(node.values[0])
    elif isinstance(node, Assign):
        rtn = leftmostname(node.targets[0])
    elif isinstance(node, (Str, Bytes)):
        # handles case of "./my executable"
        rtn = leftmostname(node.s)
    elif isinstance(node, Tuple) and len(node.elts) > 0:
        # handles case of echo ,1,2,3
        rtn = leftmostname(node.elts[0])
    else:
        rtn = None
    return rtn


def get_lineno(node, default=0):
    """Gets the lineno of a node or returns the default."""
    return getattr(node, 'lineno', default)


def min_line(node):
    """Computes the minimum lineno."""
    node_line = get_lineno(node)
    return min(map(get_lineno, walk(node), itertools.repeat(node_line)))


def max_line(node):
    """Computes the maximum lineno."""
    return max(map(get_lineno, walk(node)))


def get_col(node, default=-1):
    """Gets the col_offset of a node, or returns the default"""
    return getattr(node, 'col_offset', default)


def min_col(node):
    """Computes the minimum col_offset."""
    return min(map(get_col, walk(node), itertools.repeat(node.col_offset)))


def max_col(node):
    """Returns the maximum col_offset of the node and all sub-nodes."""
    col = getattr(node, 'max_col', None)
    if col is None:
        col = max(map(get_col, walk(node)))
    return col


def get_id(node, default=None):
    """Gets the id attribute of a node, or returns a default."""
    return getattr(node, 'id', default)


def gather_names(node):
    """Returns the set of all names present in the node's tree."""
    rtn = set(map(get_id, walk(node)))
    rtn.discard(None)
    return rtn


def has_elts(x):
    """Tests if x is an AST node with elements."""
    return isinstance(x, AST) and hasattr(x, 'elts')


def xonsh_call(name, args, lineno=None, col=None):
    """Creates the AST node for calling a function of a given name."""
    return Call(func=Name(id=name, ctx=Load(), lineno=lineno, col_offset=col),
                args=args, keywords=[], starargs=None, kwargs=None,
                lineno=lineno, col_offset=col)


def isdescendable(node):
    """Deteremines whether or not a node is worth visiting. Currently only
    UnaryOp and BoolOp nodes are visited.
    """
    return isinstance(node, (UnaryOp, BoolOp))


class CtxAwareTransformer(NodeTransformer):
    """Transforms a xonsh AST based to use subprocess calls when
    the first name in an expression statement is not known in the context.
    This assumes that the expression statement is instead parseable as
    a subprocess.
    """

    def __init__(self, parser):
        """Parameters
        ----------
        parser : xonsh.Parser
            A parse instance to try to parse suprocess statements with.
        """
        super(CtxAwareTransformer, self).__init__()
        self.parser = parser
        self.input = None
        self.contexts = []
        self.lines = None
        self.mode = None
        self._nwith = 0

    def ctxvisit(self, node, inp, ctx, mode='exec'):
        """Transforms the node in a context-dependent way.

        Parameters
        ----------
        node : ast.AST
            A syntax tree to transform.
        input : str
            The input code in string format.
        ctx : dict
            The root context to use.

        Returns
        -------
        node : ast.AST
            The transformed node.
        """
        self.lines = inp.splitlines()
        self.contexts = [ctx, set()]
        self.mode = mode
        self._nwith = 0
        node = self.visit(node)
        del self.lines, self.contexts, self.mode
        self._nwith = 0
        return node

    def ctxupdate(self, iterable):
        """Updated the most recent context."""
        self.contexts[-1].update(iterable)

    def ctxadd(self, value):
        """Adds a value the most recent context."""
        self.contexts[-1].add(value)

    def ctxremove(self, value):
        """Removes a value the most recent context."""
        for ctx in reversed(self.contexts):
            if value in ctx:
                ctx.remove(value)
                break

    def try_subproc_toks(self, node, strip_expr=False):
        """Tries to parse the line of the node as a subprocess."""
        line = self.lines[node.lineno - 1]
        if self.mode == 'eval':
            mincol = len(line) - len(line.lstrip())
            maxcol = None
        else:
            mincol = min_col(node)
            maxcol = max_col(node)
            if mincol == maxcol:
                maxcol = find_next_break(line, mincol=mincol,
                                         lexer=self.parser.lexer)
            else:
                maxcol += 1
        spline = subproc_toks(line,
                              mincol=mincol,
                              maxcol=maxcol,
                              returnline=False,
                              lexer=self.parser.lexer)
        if spline is None:
            return node
        try:
            newnode = self.parser.parse(spline, mode=self.mode)
            newnode = newnode.body
            if not isinstance(newnode, AST):
                # take the first (and only) Expr
                newnode = newnode[0]
            increment_lineno(newnode, n=node.lineno - 1)
            newnode.col_offset = node.col_offset
        except SyntaxError:
            newnode = node
        if strip_expr and isinstance(newnode, Expr):
            newnode = newnode.value
        return newnode

    def is_in_scope(self, node):
        """Determines whether or not the current node is in scope."""
        lname = leftmostname(node)
        if lname is None:
            return node
        inscope = False
        for ctx in reversed(self.contexts):
            if lname in ctx:
                inscope = True
                break
        return inscope

    #
    # With Transformers
    #
    def insert_with_block_check(self, node):
        """Modifies a with statement node in-place to add an initial check
        for whether or not the block should be executed. If the block is
        not executed it will raise a XonshBlockError containing the required
        information.
        """
        nwith = self._nwith  # the nesting level of the current with-statement
        lineno = get_lineno(node)
        col = get_col(node, 0)
        # Add or discover target names
        targets = set()
        i = 0  # index of unassigned items

        def make_next_target():
            nonlocal i
            targ = '__xonsh_with_target_{}_{}__'.format(nwith, i)
            n = Name(id=targ, ctx=Store(), lineno=lineno, col_offset=col)
            targets.add(targ)
            i += 1
            return n
        for item in node.items:
            if item.optional_vars is None:
                if has_elts(item.context_expr):
                    targs = [make_next_target() for _ in item.context_expr.elts]
                    optvars = Tuple(elts=targs, ctx=Store(), lineno=lineno,
                                    col_offset=col)
                else:
                    optvars = make_next_target()
                item.optional_vars = optvars
            else:
                targets.update(gather_names(item.optional_vars))
        # Ok, now that targets have been found / created, make the actual check
        # to see if we are in a non-executing block. This is equivalent to
        # writing the following condition:
        #
        #     if getattr(targ0, '__xonsh_block__', False) or \
        #        getattr(targ1, '__xonsh_block__', False) or ...:
        #         raise XonshBlockError(lines, globals(), locals())
        tests = [_getblockattr(t, lineno, col) for t in sorted(targets)]
        if len(tests) == 1:
            test = tests[0]
        else:
            test = BoolOp(op=Or(), values=tests, lineno=lineno, col_offset=col)
        ldx, udx = self._find_with_block_line_idx(node)
        lines = [Str(s=s, lineno=lineno, col_offset=col)
                 for s in self.lines[ldx:udx]]
        check = If(test=test, body=[
            Raise(exc=xonsh_call('XonshBlockError',
                                 args=[List(elts=lines, ctx=Load(),
                                            lineno=lineno, col_offset=col),
                                       xonsh_call('globals', args=[],
                                                  lineno=lineno, col=col),
                                       xonsh_call('locals', args=[],
                                                  lineno=lineno, col=col)],
                                 lineno=lineno, col=col),
                  cause=None, lineno=lineno, col_offset=col)],
                orelse=[], lineno=lineno, col_offset=col)
        node.body.insert(0, check)

    def _find_with_block_line_idx(self, node):
        ldx = min_line(node.body[0]) - 1
        udx = max_line(node.body[-1])
        # now check if parsable, or add lines until it is or we run out of lines
        nlines = len(self.lines)
        lines = 'with __xonsh_dummy__:\n' + '\n'.join(self.lines[ldx:udx])
        lines += '\n'
        parsable = False
        while not parsable and udx < nlines:
            try:
                self.parser.parse(lines, mode=self.mode)
                parsable = True
            except SyntaxError:
                lines += self.lines[udx] + '\n'
                udx += 1
        return ldx, udx

    #
    # Replacement visitors
    #

    def visit_Expression(self, node):
        """Handle visiting an expression body."""
        if isdescendable(node.body):
            node.body = self.visit(node.body)
        body = node.body
        inscope = self.is_in_scope(body)
        if not inscope:
            node.body = self.try_subproc_toks(body)
        return node

    def visit_Expr(self, node):
        """Handle visiting an expression."""
        if isdescendable(node.value):
            node.value = self.visit(node.value)  # this allows diving into BoolOps
        if self.is_in_scope(node):
            return node
        else:
            newnode = self.try_subproc_toks(node)
            if not isinstance(newnode, Expr):
                newnode = Expr(value=newnode,
                               lineno=node.lineno,
                               col_offset=node.col_offset)
                if hasattr(node, 'max_lineno'):
                    newnode.max_lineno = node.max_lineno
                    newnode.max_col = node.max_col
            return newnode

    def visit_UnaryOp(self, node):
        """Handle visiting an unary operands, like not."""
        if isdescendable(node.operand):
            node.operand = self.visit(node.operand)
        operand = node.operand
        inscope = self.is_in_scope(operand)
        if not inscope:
            node.operand = self.try_subproc_toks(operand, strip_expr=True)
        return node

    def visit_BoolOp(self, node):
        """Handle visiting an boolean operands, like and/or."""
        for i in range(len(node.values)):
            val = node.values[i]
            if isdescendable(val):
                val = node.values[i] = self.visit(val)
            inscope = self.is_in_scope(val)
            if not inscope:
                node.values[i] = self.try_subproc_toks(val, strip_expr=True)
        return node

    #
    # Context aggregator visitors
    #

    def visit_Assign(self, node):
        """Handle visiting an assignment statement."""
        ups = set()
        for targ in node.targets:
            if isinstance(targ, (Tuple, List)):
                ups.update(leftmostname(elt) for elt in targ.elts)
            elif isinstance(targ, BinOp):
                newnode = self.try_subproc_toks(node)
                if newnode is node:
                    ups.add(leftmostname(targ))
                else:
                    return newnode
            else:
                ups.add(leftmostname(targ))
        self.ctxupdate(ups)
        return node

    def visit_Import(self, node):
        """Handle visiting a import statement."""
        for name in node.names:
            if name.asname is None:
                self.ctxadd(name.name)
            else:
                self.ctxadd(name.asname)
        return node

    def visit_ImportFrom(self, node):
        """Handle visiting a "from ... import ..." statement."""
        for name in node.names:
            if name.asname is None:
                self.ctxadd(name.name)
            else:
                self.ctxadd(name.asname)
        return node

    def visit_With(self, node):
        """Handle visiting a with statement."""
        for item in node.items:
            if item.optional_vars is not None:
                self.ctxupdate(gather_names(item.optional_vars))
        self._nwith += 1
        self.generic_visit(node)
        self._nwith -= 1
        self.insert_with_block_check(node)
        return node

    def visit_For(self, node):
        """Handle visiting a for statement."""
        targ = node.target
        if isinstance(targ, (Tuple, List)):
            self.ctxupdate(leftmostname(elt) for elt in targ.elts)
        else:
            self.ctxadd(leftmostname(targ))
        self.generic_visit(node)
        return node

    def visit_FunctionDef(self, node):
        """Handle visiting a function definition."""
        self.ctxadd(node.name)
        self.contexts.append(set())
        self.generic_visit(node)
        self.contexts.pop()
        return node

    def visit_ClassDef(self, node):
        """Handle visiting a class definition."""
        self.ctxadd(node.name)
        self.contexts.append(set())
        self.generic_visit(node)
        self.contexts.pop()
        return node

    def visit_Delete(self, node):
        """Handle visiting a del statement."""
        for targ in node.targets:
            if isinstance(targ, Name):
                self.ctxremove(targ.id)
        self.generic_visit(node)
        return node

    def visit_Try(self, node):
        """Handle visiting a try statement."""
        for handler in node.handlers:
            if handler.name is not None:
                self.ctxadd(handler.name)
        self.generic_visit(node)
        return node

    def visit_Global(self, node):
        """Handle visiting a global statement."""
        self.contexts[1].update(node.names)  # contexts[1] is the global ctx
        self.generic_visit(node)
        return node



def pdump(s, **kwargs):
    """performs a pretty dump of an AST node."""
    if isinstance(s, AST):
        s = dump(s, **kwargs).replace(',', ',\n')
    openers = '([{'
    closers = ')]}'
    lens = len(s) + 1
    if lens == 1:
        return s
    i = min([s.find(o)%lens for o in openers])
    if i == lens - 1:
        return s
    closer = closers[openers.find(s[i])]
    j = s.rfind(closer)
    if j == -1 or j <= i:
        return s[:i+1] + '\n' + textwrap.indent(pdump(s[i+1:]), ' ')
    pre = s[:i+1] + '\n'
    mid = s[i+1:j]
    post = '\n' + s[j:]
    mid = textwrap.indent(pdump(mid), ' ')
    if '(' in post or '[' in post or '{' in post:
        post = pdump(post)
    return pre + mid + post


def pprint(s, *, sep=None, end=None, file=None, flush=False, **kwargs):
    """Performs a pretty print of the AST nodes."""
    print(pdump(s, **kwargs), sep=sep, end=end, file=file, flush=flush)


#
# Private helpers
#

def _getblockattr(name, lineno, col):
    """calls getattr(name, '__xonsh_block__', False)."""
    return xonsh_call('getattr', args=[
        Name(id=name, ctx=Load(), lineno=lineno, col_offset=col),
        Str(s='__xonsh_block__', lineno=lineno, col_offset=col),
        NameConstant(value=False, lineno=lineno, col_offset=col)],
        lineno=lineno, col=col)

#
# contexts
#
"""Context management tools for xonsh."""
# amalgamated sys
# amalgamated builtins
from collections.abc import Mapping

# amalgamated xonsh.tools
class Block(object):
    """This is a context manager for obtaining a block of lines without actually
    executing the block. The lines are accessible as the 'lines' attribute.
    """
    __xonsh_block__ = True

    def __init__(self):
        """
        Attributes
        ----------
        lines : list of str or None
            Block lines as if split by str.splitlines(), if available.
        glbs : Mapping or None
            Global execution context, ie globals().
        locs : Mapping or None
            Local execution context, ie locals().
        """
        self.lines = self.glbs = self.locs = None

    def __enter__(self):
        self.lines = self.glbs = self.locs = None  # make re-entrant
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not XonshBlockError:
            return  # some other kind of error happened
        self.lines = exc_value.lines
        self.glbs = exc_value.glbs
        if exc_value.locs is not self.glbs:
            # leave locals as None when it is the same as globals
            self.locs = exc_value.locs
        return True


class Functor(Block):
    """This is a context manager that turns the block into a callable
    object, bound to the execution context it was created in.
    """

    def __init__(self, args=(), kwargs=None, rtn=''):
        """
        Parameters
        ----------
        args : Sequence of str, optional
            A tuple of argument names for the functor.
        kwargs : Mapping of str to values or list of item tuples, optional
            Keyword argument names and values, if available.
        rtn : str, optional
            Name of object to return, if available.

        Attributes
        ----------
        func : function
            The underlying function object. This defaults to none and is set
            after the the block is exited.
        """
        super().__init__()
        self.func = None
        self.args = args
        if kwargs is None:
            self.kwargs = []
        elif isinstance(kwargs, Mapping):
            self.kwargs = sorted(kwargs.items())
        else:
            self.kwargs = kwargs
        self.rtn = rtn

    def __enter__(self):
        super().__enter__()
        self.func = None
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        res = super().__exit__(exc_type, exc_value, traceback)
        if not res:
            return res
        body = '\n'.join(self.lines)
        uid = hash(body) + sys.maxsize  # should always be a positive int
        name = '__xonsh_functor_{uid}__'.format(uid=uid)
        # construct signature string
        sig = rtn = ''
        sig = ', '.join(self.args)
        kwstr = ', '.join([k + '=None' for k, _ in self.kwargs])
        if len(kwstr) > 0:
            sig = kwstr if len(sig) == 0 else sig + ', ' + kwstr
        # construct return string
        rtn = str(self.rtn)
        if len(rtn) > 0:
            line0 = self.lines[0]
            ws = line0[:-len(line0.lstrip())]
            rtn = ws + 'return ' + rtn + '\n'
        # construct function string
        fstr = 'def {name}({sig}):\n{body}\n{rtn}'
        fstr = fstr.format(name=name, sig=sig, body=body, rtn=rtn)
        glbs = self.glbs
        locs = self.locs
        execer = builtins.__xonsh_execer__
        execer.exec(fstr, glbs=glbs, locs=locs)
        if locs is not None and name in locs:
            func = locs[name]
        elif name in glbs:
            func = glbs[name]
        else:
            raise exc_value
        if len(self.kwargs) > 0:
            func.__defaults__ = tuple(v for _, v in self.kwargs)
        self.func = func
        return res

    def __call__(self, *args, **kwargs):
        """Dispatches to func."""
        if self.func is None:
            msg = "{} block with 'None' func not callable"
            raise AttributeError(msg.formst(self.__class__.__name__))
        return self.func(*args, **kwargs)

#
# diff_history
#
# -*- coding: utf-8 -*-
"""Tools for diff'ing two xonsh history files in a meaningful fashion."""
difflib = _LazyModule.load('difflib', 'difflib')
# amalgamated datetime
# amalgamated itertools
# amalgamated xonsh.lazyjson
# amalgamated xonsh.tools
NO_COLOR = '{NO_COLOR}'
RED = '{RED}'
GREEN = '{GREEN}'
BOLD_RED = '{BOLD_RED}'
BOLD_GREEN = '{BOLD_GREEN}'

# intern some strings
REPLACE = 'replace'
DELETE = 'delete'
INSERT = 'insert'
EQUAL = 'equal'


def bold_str_diff(a, b, sm=None):
    if sm is None:
        sm = difflib.SequenceMatcher()
    aline = RED + '- '
    bline = GREEN + '+ '
    sm.set_seqs(a, b)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == REPLACE:
            aline += BOLD_RED + a[i1:i2] + RED
            bline += BOLD_GREEN + b[j1:j2] + GREEN
        elif tag == DELETE:
            aline += BOLD_RED + a[i1:i2] + RED
        elif tag == INSERT:
            bline += BOLD_GREEN + b[j1:j2] + GREEN
        elif tag == EQUAL:
            aline += a[i1:i2]
            bline += b[j1:j2]
        else:
            raise RuntimeError('tag not understood')
    return aline + NO_COLOR + '\n' + bline + NO_COLOR +'\n'


def redline(line):
   return '{red}- {line}{no_color}\n'.format(red=RED, line=line, no_color=NO_COLOR)


def greenline(line):
   return '{green}+ {line}{no_color}\n'.format(green=GREEN, line=line, no_color=NO_COLOR)


def highlighted_ndiff(a, b):
    """Returns a highlited string, with bold charaters where different."""
    s = ''
    sm = difflib.SequenceMatcher()
    sm.set_seqs(a, b)
    linesm = difflib.SequenceMatcher()
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == REPLACE:
            for aline, bline in itertools.zip_longest(a[i1:i2], b[j1:j2]):
                if bline is None:
                    s += redline(aline)
                elif aline is None:
                    s += greenline(bline)
                else:
                    s += bold_str_diff(aline, bline, sm=linesm)
        elif tag == DELETE:
            for aline in a[i1:i2]:
                s += redline(aline)
        elif tag == INSERT:
            for bline in b[j1:j2]:
                s += greenline(bline)
        elif tag == EQUAL:
            for aline in a[i1:i2]:
                s += '  ' + aline + '\n'
        else:
            raise RuntimeError('tag not understood')
    return s


class HistoryDiffer(object):
    """This class helps diff two xonsh history files."""

    def __init__(self, afile, bfile, reopen=False, verbose=False):
        """
        Parameters
        ----------
        afile : file handle or str
            The first file to diff
        bfile : file handle or str
            The second file to diff
        reopen : bool, optional
            Whether or not to reopen the file handles each time. The default here is
            opposite from the LazyJSON default because we know that we will be doing
            a lot of reading so it is best to keep the handles open.
        verbose : bool, optional
            Whether to print a verbose amount of information.
        """
        self.a = LazyJSON(afile, reopen=reopen)
        self.b = LazyJSON(bfile, reopen=reopen)
        self.verbose = verbose
        self.sm = difflib.SequenceMatcher(autojunk=False)

    def __del__(self):
        self.a.close()
        self.b.close()

    def __str__(self):
        return self.format()

    def _header_line(self, lj):
        s = lj._f.name if hasattr(lj._f, 'name') else ''
        s += ' (' + lj['sessionid'] + ')'
        s += ' [locked]' if lj['locked'] else ' [unlocked]'
        ts = lj['ts'].load()
        ts0 = datetime.datetime.fromtimestamp(ts[0])
        s += ' started: ' + ts0.isoformat(' ')
        if ts[1] is not None:
            ts1 = datetime.datetime.fromtimestamp(ts[1])
            s += ' stopped: ' + ts1.isoformat(' ') + ' runtime: ' + str(ts1 - ts0)
        return s

    def header(self):
        """Computes a header string difference."""
        s = ('{red}--- {aline}{no_color}\n'
             '{green}+++ {bline}{no_color}')
        s = s.format(aline=self._header_line(self.a), bline=self._header_line(self.b),
                     red=RED, green=GREEN, no_color=NO_COLOR)
        return s

    def _env_both_diff(self, in_both, aenv, benv):
        sm = self.sm
        s = ''
        for key in sorted(in_both):
            aval = aenv[key]
            bval = benv[key]
            if aval == bval:
                continue
            s += '{0!r} is in both, but differs\n'.format(key)
            s += bold_str_diff(aval, bval, sm=sm) + '\n'
        return s

    def _env_in_one_diff(self, x, y, color, xid, xenv):
        only_x = sorted(x - y)
        if len(only_x) == 0:
                return ''
        if self.verbose:
            xstr = ',\n'.join(['    {0!r}: {1!r}'.format(key, xenv[key]) \
                               for key in only_x])
            xstr = '\n' + xstr
        else:
            xstr = ', '.join(['{0!r}'.format(key) for key in only_x])
        in_x = 'These vars are only in {color}{xid}{no_color}: {{{xstr}}}\n\n'
        return in_x.format(xid=xid, color=color, no_color=NO_COLOR, xstr=xstr)

    def envdiff(self):
        """Computes the difference between the environments."""
        aenv = self.a['env'].load()
        benv = self.b['env'].load()
        akeys = frozenset(aenv)
        bkeys = frozenset(benv)
        in_both = akeys & bkeys
        if len(in_both) == len(akeys) == len(bkeys):
            keydiff = self._env_both_diff(in_both, aenv, benv)
            if len(keydiff) == 0:
                return ''
            in_a = in_b = ''
        else:
            keydiff = self._env_both_diff(in_both, aenv, benv)
            in_a = self._env_in_one_diff(akeys, bkeys, RED, self.a['sessionid'], aenv)
            in_b = self._env_in_one_diff(bkeys, akeys, GREEN, self.b['sessionid'], benv)
        s = 'Environment\n-----------\n' + in_a + keydiff + in_b
        return s

    def _cmd_in_one_diff(self, inp, i, xlj, xid, color):
        s = 'cmd #{i} only in {color}{xid}{no_color}:\n'
        s = s.format(i=i, color=color, xid=xid, no_color=NO_COLOR)
        lines = inp.splitlines()
        lt = '{color}{pre}{no_color} {line}\n'
        s += lt.format(color=color, no_color=NO_COLOR, line=lines[0], pre='>>>')
        for line in lines[1:]:
            s += lt.format(color=color, no_color=NO_COLOR, line=line, pre='...')
        if not self.verbose:
            return s + '\n'
        out = xlj['cmds'][0].get('out', 'Note: no output stored')
        s += out.rstrip() + '\n\n'
        return s

    def _cmd_out_and_rtn_diff(self, i, j):
        s = ''
        aout = self.a['cmds'][i].get('out', None)
        bout = self.b['cmds'][j].get('out', None)
        if aout is None and bout is None:
            #s += 'Note: neither output stored\n'
            pass
        elif bout is None:
            aid = self.a['sessionid']
            s += 'Note: only {red}{aid}{no_color} output stored\n'.format(red=RED,
                                                            aid=aid, no_color=NO_COLOR)
        elif aout is None:
            bid = self.b['sessionid']
            s += 'Note: only {green}{bid}{no_color} output stored\n'.format(green=GREEN,
                                                            bid=bid, no_color=NO_COLOR)
        elif aout != bout:
            s += 'Outputs differ\n'
            s += highlighted_ndiff(aout.splitlines(), bout.splitlines())
        else:
            pass
        artn = self.a['cmds'][i]['rtn']
        brtn = self.b['cmds'][j]['rtn']
        if artn != brtn:
            s += ('Return vals {red}{artn}{no_color} & {green}{brtn}{no_color} differ\n'
                  ).format(red=RED, green=GREEN, no_color=NO_COLOR, artn=artn, brtn=brtn)
        return s

    def _cmd_replace_diff(self, i, ainp, aid, j, binp, bid):
        s = ('cmd #{i} in {red}{aid}{no_color} is replaced by \n'
             'cmd #{j} in {green}{bid}{no_color}:\n')
        s = s.format(i=i, aid=aid, j=j, bid=bid, red=RED, green=GREEN, no_color=NO_COLOR)
        s += highlighted_ndiff(ainp.splitlines(), binp.splitlines())
        if not self.verbose:
            return s + '\n'
        s += self._cmd_out_and_rtn_diff(i, j)
        return s + '\n'

    def cmdsdiff(self):
        """Computes the difference of the commands themselves."""
        aid = self.a['sessionid']
        bid = self.b['sessionid']
        ainps = [c['inp'] for c in self.a['cmds']]
        binps = [c['inp'] for c in self.b['cmds']]
        sm = self.sm
        sm.set_seqs(ainps, binps)
        s = ''
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == REPLACE:
                zipper = itertools.zip_longest
                for i, ainp, j, binp in zipper(range(i1, i2), ainps[i1:i2],
                                               range(j1, j2), binps[j1:j2]):
                    if j is None:
                        s += self._cmd_in_one_diff(ainp, i, self.a, aid, RED)
                    elif i is None:
                        s += self._cmd_in_one_diff(binp, j, self.b, bid, GREEN)
                    else:
                        self._cmd_replace_diff(i, ainp, aid, j, binp, bid)
            elif tag == DELETE:
                for i, inp in enumerate(ainps[i1:i2], i1):
                    s += self._cmd_in_one_diff(inp, i, self.a, aid, RED)
            elif tag == INSERT:
                for j, inp in enumerate(binps[j1:j2], j1):
                    s += self._cmd_in_one_diff(inp, j, self.b, bid, GREEN)
            elif tag == EQUAL:
                for i, j, in zip(range(i1, i2), range(j1, j2)):
                    odiff = self._cmd_out_and_rtn_diff(i, j)
                    if len(odiff) > 0:
                        h = ('cmd #{i} in {red}{aid}{no_color} input is the same as \n'
                             'cmd #{j} in {green}{bid}{no_color}, but output differs:\n')
                        s += h.format(i=i, aid=aid, j=j, bid=bid, red=RED, green=GREEN,
                                      no_color=NO_COLOR)
                        s += odiff + '\n'
            else:
                raise RuntimeError('tag not understood')
        if len(s) == 0:
            return s
        return 'Commands\n--------\n' + s

    def format(self):
        """Formats the difference between the two history files."""
        s = self.header()
        ed = self.envdiff()
        if len(ed) > 0:
            s += '\n\n' + ed
        cd = self.cmdsdiff()
        if len(cd) > 0:
            s += '\n\n' + cd
        return s.rstrip()


_HD_PARSER = None

def _dh_create_parser(p=None):
    global _HD_PARSER
    p_was_none = (p is None)
    if _HD_PARSER is not None and p_was_none:
        return _HD_PARSER
    if p_was_none:
        from argparse import ArgumentParser
        p = ArgumentParser('diff-history', description='diffs two xonsh history files')
    p.add_argument('--reopen', dest='reopen', default=False, action='store_true',
                   help='make lazy file loading reopen files each time')
    p.add_argument('-v', '--verbose', dest='verbose', default=False, action='store_true',
                   help='whether to print even more information')
    p.add_argument('a', help='first file in diff')
    p.add_argument('b', help='second file in diff')
    if p_was_none:
        _HD_PARSER = p
    return p


def _dh_main_action(ns, hist=None):
    hd = HistoryDiffer(ns.a, ns.b, reopen=ns.reopen, verbose=ns.verbose)
    print_color(hd.format())


def diff_history_main(args=None, stdin=None):
    """Main entry point for history diff'ing"""
    parser = _create_parser()
    ns = parser.parse_args(args)
    _dh_main_action(ns)


if __name__ == '__main__':
    diff_history_main()

#
# dirstack
#
# -*- coding: utf-8 -*-
"""Directory stack and associated utilities for the xonsh shell."""
# amalgamated os
# amalgamated glob
argparse = _LazyModule.load('argparse', 'argparse')
# amalgamated builtins
# amalgamated xonsh.lazyasd
# amalgamated xonsh.tools
DIRSTACK = []
"""A list containing the currently remembered directories."""


def _get_cwd():
    try:
        return os.getcwd()
    except (OSError, FileNotFoundError):
        return None


def _change_working_directory(newdir):
    env = builtins.__xonsh_env__
    old = env['PWD']
    new = os.path.join(old, newdir)
    try:
        os.chdir(os.path.abspath(new))
    except (OSError, FileNotFoundError):
        if new.endswith(get_sep()):
            new = new[:-1]
        if os.path.basename(new) == '..':
            env['PWD'] = new
        return
    if old is not None:
        env['OLDPWD'] = old
    if new is not None:
        env['PWD'] = os.path.abspath(new)


def _try_cdpath(apath):
    # NOTE: this CDPATH implementation differs from the bash one.
    # In bash if a CDPATH is set, an unqualified local folder
    # is considered after all CDPATHs, example:
    # CDPATH=$HOME/src (with src/xonsh/ inside)
    # $ cd xonsh -> src/xonsh (whith xonsh/xonsh)
    # a second $ cd xonsh has no effects, to move in the nested xonsh
    # in bash a full $ cd ./xonsh is needed.
    # In xonsh a relative folder is allways preferred.
    env = builtins.__xonsh_env__
    cdpaths = env.get('CDPATH')
    for cdp in cdpaths:
        globber = builtins.__xonsh_expand_path__(os.path.join(cdp, apath))
        for cdpath_prefixed_path in glob.iglob(globber):
            return cdpath_prefixed_path
    return apath


def cd(args, stdin=None):
    """Changes the directory.

    If no directory is specified (i.e. if `args` is None) then this
    changes to the current user's home directory.
    """
    env = builtins.__xonsh_env__
    oldpwd = env.get('OLDPWD', None)
    cwd = env['PWD']

    if len(args) == 0:
        d = os.path.expanduser('~')
    elif len(args) == 1:
        d = os.path.expanduser(args[0])
        if not os.path.isdir(d):
            if d == '-':
                if oldpwd is not None:
                    d = oldpwd
                else:
                    return '', 'cd: no previous directory stored\n', 1
            elif d.startswith('-'):
                try:
                    num = int(d[1:])
                except ValueError:
                    return '', 'cd: Invalid destination: {0}\n'.format(d), 1
                if num == 0:
                    return None, None, 0
                elif num < 0:
                    return '', 'cd: Invalid destination: {0}\n'.format(d), 1
                elif num > len(DIRSTACK):
                    e = 'cd: Too few elements in dirstack ({0} elements)\n'
                    return '', e.format(len(DIRSTACK)), 1
                else:
                    d = DIRSTACK[num - 1]
            else:
                d = _try_cdpath(d)
    else:
        return '', 'cd takes 0 or 1 arguments, not {0}\n'.format(len(args)), 1
    if not os.path.exists(d):
        return '', 'cd: no such file or directory: {0}\n'.format(d), 1
    if not os.path.isdir(d):
        return '', 'cd: {0} is not a directory\n'.format(d), 1
    if not os.access(d, os.X_OK):
        return '', 'cd: permission denied: {0}\n'.format(d), 1
    # now, push the directory onto the dirstack if AUTO_PUSHD is set
    if cwd is not None and env.get('AUTO_PUSHD'):
        pushd(['-n', '-q', cwd])
    _change_working_directory(d)
    return None, None, 0


def _pushd_parser():
    parser = argparse.ArgumentParser(prog="pushd")
    parser.add_argument('dir', nargs='?')
    parser.add_argument('-n',
                        dest='cd',
                        help='Suppresses the normal change of directory when'
                        ' adding directories to the stack, so that only the'
                        ' stack is manipulated.',
                        action='store_false')
    parser.add_argument('-q',
                        dest='quiet',
                        help='Do not call dirs, regardless of $PUSHD_SILENT',
                        action='store_true')
    return parser


pushd_parser = LazyObject(_pushd_parser, globals(), 'pushd_parser')
del _pushd_parser

def pushd(args, stdin=None):
    """xonsh command: pushd

    Adds a directory to the top of the directory stack, or rotates the stack,
    making the new top of the stack the current working directory.
    """
    global DIRSTACK

    try:
        args = pushd_parser.parse_args(args)
    except SystemExit:
        return None, None, 1

    env = builtins.__xonsh_env__

    pwd = env['PWD']

    if env.get('PUSHD_MINUS', False):
        BACKWARD = '-'
        FORWARD = '+'
    else:
        BACKWARD = '+'
        FORWARD = '-'

    if args.dir is None:
        try:
            new_pwd = DIRSTACK.pop(0)
        except IndexError:
            e = 'pushd: Directory stack is empty\n'
            return None, e, 1
    elif os.path.isdir(args.dir):
        new_pwd = args.dir
    else:
        try:
            num = int(args.dir[1:])
        except ValueError:
            e = 'Invalid argument to pushd: {0}\n'
            return None, e.format(args.dir), 1

        if num < 0:
            e = 'Invalid argument to pushd: {0}\n'
            return None, e.format(args.dir), 1

        if num > len(DIRSTACK):
            e = 'Too few elements in dirstack ({0} elements)\n'
            return None, e.format(len(DIRSTACK)), 1
        elif args.dir.startswith(FORWARD):
            if num == len(DIRSTACK):
                new_pwd = None
            else:
                new_pwd = DIRSTACK.pop(len(DIRSTACK) - 1 - num)
        elif args.dir.startswith(BACKWARD):
            if num == 0:
                new_pwd = None
            else:
                new_pwd = DIRSTACK.pop(num - 1)
        else:
            e = 'Invalid argument to pushd: {0}\n'
            return None, e.format(args.dir), 1
    if new_pwd is not None:
        if args.cd:
            DIRSTACK.insert(0, os.path.expanduser(pwd))
            _change_working_directory(new_pwd)
        else:
            DIRSTACK.insert(0, os.path.expanduser(new_pwd))

    maxsize = env.get('DIRSTACK_SIZE')
    if len(DIRSTACK) > maxsize:
        DIRSTACK = DIRSTACK[:maxsize]

    if not args.quiet and not env.get('PUSHD_SILENT'):
        return dirs([], None)

    return None, None, 0



def _popd_parser():
    parser = argparse.ArgumentParser(prog="popd")
    parser.add_argument('dir', nargs='?')
    parser.add_argument('-n',
                        dest='cd',
                        help='Suppresses the normal change of directory when'
                        ' adding directories to the stack, so that only the'
                        ' stack is manipulated.',
                        action='store_false')
    parser.add_argument('-q',
                        dest='quiet',
                        help='Do not call dirs, regardless of $PUSHD_SILENT',
                        action='store_true')
    return parser


popd_parser = LazyObject(_popd_parser, globals(), 'popd_parser')
del _popd_parser

def popd(args, stdin=None):
    """
    xonsh command: popd

    Removes entries from the directory stack.
    """
    global DIRSTACK

    try:
        args = pushd_parser.parse_args(args)
    except SystemExit:
        return None, None, 1

    env = builtins.__xonsh_env__

    if env.get('PUSHD_MINUS'):
        BACKWARD = '-'
        FORWARD = '+'
    else:
        BACKWARD = '-'
        FORWARD = '+'

    if args.dir is None:
        try:
            new_pwd = DIRSTACK.pop(0)
        except IndexError:
            e = 'popd: Directory stack is empty\n'
            return None, e, 1
    else:
        try:
            num = int(args.dir[1:])
        except ValueError:
            e = 'Invalid argument to popd: {0}\n'
            return None, e.format(args.dir), 1

        if num < 0:
            e = 'Invalid argument to popd: {0}\n'
            return None, e.format(args.dir), 1

        if num > len(DIRSTACK):
            e = 'Too few elements in dirstack ({0} elements)\n'
            return None, e.format(len(DIRSTACK)), 1
        elif args.dir.startswith(FORWARD):
            if num == len(DIRSTACK):
                new_pwd = DIRSTACK.pop(0)
            else:
                new_pwd = None
                DIRSTACK.pop(len(DIRSTACK) - 1 - num)
        elif args.dir.startswith(BACKWARD):
            if num == 0:
                new_pwd = DIRSTACK.pop(0)
            else:
                new_pwd = None
                DIRSTACK.pop(num - 1)
        else:
            e = 'Invalid argument to popd: {0}\n'
            return None, e.format(args.dir), 1

    if new_pwd is not None:
        e = None
        if args.cd:
            _change_working_directory(new_pwd)

    if not args.quiet and not env.get('PUSHD_SILENT'):
        return dirs([], None)

    return None, None, 0


def _dirs_parser():
    parser = argparse.ArgumentParser(prog="dirs")
    parser.add_argument('N', nargs='?')
    parser.add_argument('-c',
                        dest='clear',
                        help='Clears the directory stack by deleting all of'
                        ' the entries.',
                        action='store_true')
    parser.add_argument('-p',
                        dest='print_long',
                        help='Print the directory stack with one entry per'
                        ' line.',
                        action='store_true')
    parser.add_argument('-v',
                        dest='verbose',
                        help='Print the directory stack with one entry per'
                        ' line, prefixing each entry with its index in the'
                        ' stack.',
                        action='store_true')
    parser.add_argument('-l',
                        dest='long',
                        help='Produces a longer listing; the default listing'
                        ' format uses a tilde to denote the home directory.',
                        action='store_true')
    return parser


dirs_parser = LazyObject(_dirs_parser, globals(), 'dirs_parser')
del _dirs_parser

def dirs(args, stdin=None):
    """xonsh command: dirs

    Displays the list of currently remembered directories.  Can also be used
    to clear the directory stack.
    """
    global DIRSTACK
    try:
        args = dirs_parser.parse_args(args)
    except SystemExit:
        return None, None

    env = builtins.__xonsh_env__
    dirstack = [os.path.expanduser(env['PWD'])] + DIRSTACK

    if env.get('PUSHD_MINUS'):
        BACKWARD = '-'
        FORWARD = '+'
    else:
        BACKWARD = '-'
        FORWARD = '+'

    if args.clear:
        DIRSTACK = []
        return None, None, 0

    if args.long:
        o = dirstack
    else:
        d = os.path.expanduser('~')
        o = [i.replace(d, '~') for i in dirstack]

    if args.verbose:
        out = ''
        pad = len(str(len(o) - 1))
        for (ix, e) in enumerate(o):
            blanks = ' ' * (pad - len(str(ix)))
            out += '\n{0}{1} {2}'.format(blanks, ix, e)
        out = out[1:]
    elif args.print_long:
        out = '\n'.join(o)
    else:
        out = ' '.join(o)

    N = args.N
    if N is not None:
        try:
            num = int(N[1:])
        except ValueError:
            e = 'Invalid argument to dirs: {0}\n'
            return None, e.format(N), 1

        if num < 0:
            e = 'Invalid argument to dirs: {0}\n'
            return None, e.format(len(o)), 1

        if num >= len(o):
            e = 'Too few elements in dirstack ({0} elements)\n'
            return None, e.format(len(o)), 1

        if N.startswith(BACKWARD):
            idx = num
        elif N.startswith(FORWARD):
            idx = len(o) - 1 - num
        else:
            e = 'Invalid argument to dirs: {0}\n'
            return None, e.format(N), 1

        out = o[idx]

    return out + '\n', None, 0

#
# foreign_shells
#
# -*- coding: utf-8 -*-
"""Tools to help interface with foreign shells, such as Bash."""
# amalgamated os
# amalgamated sys
# amalgamated re
# amalgamated json
shlex = _LazyModule.load('shlex', 'shlex')
# amalgamated tempfile
# amalgamated builtins
# amalgamated subprocess
from warnings import warn
from functools import lru_cache
from collections import MutableMapping, Mapping, Sequence

# amalgamated xonsh.lazyasd
# amalgamated xonsh.tools
# amalgamated xonsh.platform
COMMAND = """
{seterrprevcmd}
{prevcmd}
echo __XONSH_ENV_BEG__
{envcmd}
echo __XONSH_ENV_END__
echo __XONSH_ALIAS_BEG__
{aliascmd}
echo __XONSH_ALIAS_END__
echo __XONSH_FUNCS_BEG__
{funcscmd}
echo __XONSH_FUNCS_END__
{postcmd}
{seterrpostcmd}
""".strip()

DEFAULT_BASH_FUNCSCMD = r"""
# get function names from declare
declstr=$(declare -F)
read -r -a decls <<< $declstr
funcnames=""
for((n=0;n<${#decls[@]};n++)); do
  if (( $(($n % 3 )) == 2 )); then
    # get every 3rd entry
    funcnames="$funcnames ${decls[$n]}"
  fi
done

# get functions locations: funcname lineno filename
shopt -s extdebug
namelocfilestr=$(declare -F $funcnames)
shopt -u extdebug

# print just names and files as JSON object
read -r -a namelocfile <<< $namelocfilestr
sep=" "
namefile="{"
while IFS='' read -r line || [[ -n "$line" ]]; do
  name=${line%%"$sep"*}
  locfile=${line#*"$sep"}
  loc=${locfile%%"$sep"*}
  file=${locfile#*"$sep"}
  namefile="${namefile}\"${name}\":\"${file//\\/\\\\}\","
done <<< "$namelocfilestr"
if [[ "{" == "${namefile}" ]]; then
  namefile="${namefile}}"
else
  namefile="${namefile%?}}"
fi
echo $namefile
""".strip()

DEFAULT_ZSH_FUNCSCMD = """
namefile="{"
for name in ${(ok)functions}; do
  loc=$(whence -v $name)
  loc=${(z)loc}
  file=${loc[7,-1]}
  namefile="${namefile}\\"${name}\\":\\"${(Q)file:A}\\","
done
if [[ "{" == "${namefile}" ]]; then
  namefile="${namefile}}"
else
  namefile="${namefile%?}}"
fi
echo ${namefile}
""".strip()

# mapping of shell name alises to keys in other lookup dictionaries.
CANON_SHELL_NAMES = {
    'bash': 'bash',
    '/bin/bash': 'bash',
    'zsh': 'zsh',
    '/bin/zsh': 'zsh',
    '/usr/bin/zsh': 'zsh',
    'cmd': 'cmd',
    'cmd.exe': 'cmd',
}

DEFAULT_ENVCMDS = {
    'bash': 'env',
    'zsh': 'env',
    'cmd': 'set',
}
DEFAULT_ALIASCMDS = {
    'bash': 'alias',
    'zsh': 'alias -L',
    'cmd': '',
}
DEFAULT_FUNCSCMDS = {
    'bash': DEFAULT_BASH_FUNCSCMD,
    'zsh': DEFAULT_ZSH_FUNCSCMD,
    'cmd': '',
}
DEFAULT_SOURCERS = {
    'bash': 'source',
    'zsh': 'source',
    'cmd': 'call',
}
DEFAULT_TMPFILE_EXT = {
    'bash': '.sh',
    'zsh': '.zsh',
    'cmd': '.bat',
}
DEFAULT_RUNCMD = {
    'bash': '-c',
    'zsh': '-c',
    'cmd': '/C',
}
DEFAULT_SETERRPREVCMD = {
    'bash': 'set -e',
    'zsh': 'set -e',
    'cmd': '@echo off',
}
DEFAULT_SETERRPOSTCMD = {
    'bash': '',
    'zsh': '',
    'cmd': 'if errorlevel 1 exit 1',
}


@lru_cache()
def foreign_shell_data(shell, interactive=True, login=False, envcmd=None,
                       aliascmd=None, extra_args=(), currenv=None,
                       safe=True, prevcmd='', postcmd='', funcscmd=None,
                       sourcer=None, use_tmpfile=False, tmpfile_ext=None,
                       runcmd=None, seterrprevcmd=None, seterrpostcmd=None):
    """Extracts data from a foreign (non-xonsh) shells. Currently this gets
    the environment, aliases, and functions but may be extended in the future.

    Parameters
    ----------
    shell : str
        The name of the shell, such as 'bash' or '/bin/sh'.
    interactive : bool, optional
        Whether the shell should be run in interactive mode.
    login : bool, optional
        Whether the shell should be a login shell.
    envcmd : str or None, optional
        The command to generate environment output with.
    aliascmd : str or None, optional
        The command to generate alias output with.
    extra_args : tuple of str, optional
        Addtional command line options to pass into the shell.
    currenv : tuple of items or None, optional
        Manual override for the current environment.
    safe : bool, optional
        Flag for whether or not to safely handle exceptions and other errors.
    prevcmd : str, optional
        A command to run in the shell before anything else, useful for
        sourcing and other commands that may require environment recovery.
    postcmd : str, optional
        A command to run after everything else, useful for cleaning up any
        damage that the prevcmd may have caused.
    funcscmd : str or None, optional
        This is a command or script that can be used to determine the names
        and locations of any functions that are native to the foreign shell.
        This command should print *only* a JSON object that maps
        function names to the filenames where the functions are defined.
        If this is None, then a default script will attempted to be looked
        up based on the shell name. Callable wrappers for these functions
        will be returned in the aliases dictionary.
    sourcer : str or None, optional
        How to source a foreign shell file for purposes of calling functions
        in that shell. If this is None, a default value will attempt to be
        looked up based on the shell name.
    use_tmpfile : bool, optional
        This specifies if the commands are written to a tmp file or just
        parsed directly to the shell
    tmpfile_ext : str or None, optional
        If tmpfile is True this sets specifies the extension used.
    runcmd : str or None, optional
        Command line switches to use when running the script, such as
        -c for Bash and /C for cmd.exe.
    seterrprevcmd : str or None, optional
        Command that enables exit-on-error for the shell that is run at the
        start of the script. For example, this is "set -e" in Bash. To disable
        exit-on-error behavior, simply pass in an empty string.
    seterrpostcmd : str or None, optional
        Command that enables exit-on-error for the shell that is run at the end
        of the script. For example, this is "if errorlevel 1 exit 1" in
        cmd.exe. To disable exit-on-error behavior, simply pass in an
        empty string.

    Returns
    -------
    env : dict
        Dictionary of shell's environment
    aliases : dict
        Dictionary of shell's alaiases, this includes foreign function
        wrappers.
    """
    cmd = [shell]
    cmd.extend(extra_args)  # needs to come here for GNU long options
    if interactive:
        cmd.append('-i')
    if login:
        cmd.append('-l')
    shkey = CANON_SHELL_NAMES[shell]
    envcmd = DEFAULT_ENVCMDS.get(shkey, 'env') if envcmd is None else envcmd
    aliascmd = DEFAULT_ALIASCMDS.get(shkey, 'alias') if aliascmd is None else aliascmd
    funcscmd = DEFAULT_FUNCSCMDS.get(shkey, 'echo {}') if funcscmd is None else funcscmd
    tmpfile_ext = DEFAULT_TMPFILE_EXT.get(shkey, 'sh') if tmpfile_ext is None else tmpfile_ext
    runcmd = DEFAULT_RUNCMD.get(shkey, '-c') if runcmd is None else runcmd
    seterrprevcmd = DEFAULT_SETERRPREVCMD.get(shkey, '') \
                        if seterrprevcmd is None else seterrprevcmd
    seterrpostcmd = DEFAULT_SETERRPOSTCMD.get(shkey, '') \
                        if seterrpostcmd is None else seterrpostcmd
    command = COMMAND.format(envcmd=envcmd, aliascmd=aliascmd, prevcmd=prevcmd,
                             postcmd=postcmd, funcscmd=funcscmd,
                             seterrprevcmd=seterrprevcmd,
                             seterrpostcmd=seterrpostcmd).strip()

    cmd.append(runcmd)

    if not use_tmpfile:
        cmd.append(command)
    else:
        tmpfile = tempfile.NamedTemporaryFile(suffix=tmpfile_ext, delete=False)
        tmpfile.write(command.encode('utf8'))
        tmpfile.close()
        cmd.append(tmpfile.name)

    if currenv is None and hasattr(builtins, '__xonsh_env__'):
        currenv = builtins.__xonsh_env__.detype()
    elif currenv is not None:
        currenv = dict(currenv)
    try:
        s = subprocess.check_output(cmd, stderr=subprocess.PIPE, env=currenv,
                                    # start new session to avoid hangs (doesn't work on Cygwin though)
                                    start_new_session=(not ON_CYGWIN),
                                    universal_newlines=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        if not safe:
            raise
        return None, None
    finally:
        if use_tmpfile:
            os.remove(tmpfile.name)
    env = parse_env(s)
    aliases = parse_aliases(s)
    funcs = parse_funcs(s, shell=shell, sourcer=sourcer)
    aliases.update(funcs)
    return env, aliases


ENV_RE = LazyObject(lambda: re.compile('__XONSH_ENV_BEG__\n(.*)'
                                       '__XONSH_ENV_END__', flags=re.DOTALL),
                    globals(), 'ENV_RE')
ENV_SPLIT_RE = LazyObject(lambda: re.compile('^([^=]+)=([^=]*|[^\n]*)$',
                                             flags=re.DOTALL|re.MULTILINE),
                          globals(), 'ENV_SPLIT_RE')


def parse_env(s):
    """Parses the environment portion of string into a dict."""
    m = ENV_RE.search(s)
    if m is None:
        return {}
    g1 = m.group(1)
    g1 = g1[:-1] if g1.endswith('\n') else g1
    env = dict(ENV_SPLIT_RE.findall(g1))
    return env


ALIAS_RE = re.compile('__XONSH_ALIAS_BEG__\n(.*)__XONSH_ALIAS_END__',
                      flags=re.DOTALL)


def parse_aliases(s):
    """Parses the aliases portion of string into a dict."""
    m = ALIAS_RE.search(s)
    if m is None:
        return {}
    g1 = m.group(1)
    items = [line.split('=', 1) for line in g1.splitlines() if
             line.startswith('alias ') and '=' in line]
    aliases = {}
    for key, value in items:
        try:
            key = key[6:]  # lstrip 'alias '
            # undo bash's weird quoting of single quotes (sh_single_quote)
            value = value.replace('\'\\\'\'', '\'')
            # strip one single quote at the start and end of value
            if value[0] == '\'' and value[-1] == '\'':
                value = value[1:-1]
            value = shlex.split(value)
        except ValueError as exc:
            warn('could not parse alias "{0}": {1!r}'.format(key, exc),
                 RuntimeWarning)
            continue
        aliases[key] = value
    return aliases


FUNCS_RE = re.compile('__XONSH_FUNCS_BEG__\n(.+)\n__XONSH_FUNCS_END__',
                      flags=re.DOTALL)


def parse_funcs(s, shell, sourcer=None):
    """Parses the funcs portion of a string into a dict of callable foreign
    function wrappers.
    """
    m = FUNCS_RE.search(s)
    if m is None:
        return {}
    g1 = m.group(1)
    if ON_WINDOWS:
        g1 = g1.replace(os.sep, os.altsep)
    try:
        namefiles = json.loads(g1.strip())
    except json.decoder.JSONDecodeError as exc:
        msg = ('{0!r}\n\ncould not parse {1} functions:\n'
               '  s  = {2!r}\n'
               '  g1 = {3!r}\n\n'
               'Note: you may be seeing this error if you use zsh with '
               'prezto. Prezto overwrites GNU coreutils functions (like echo) '
               'with its own zsh functions. Please try disabling prezto.')
        warn(msg.format(exc, shell, s, g1), RuntimeWarning)
        return {}
    sourcer = DEFAULT_SOURCERS.get(shell, 'source') if sourcer is None \
                                                    else sourcer
    funcs = {}
    for funcname, filename in namefiles.items():
        if funcname.startswith('_'):
            continue  # skip private functions
        if not os.path.isabs(filename):
            filename = os.path.abspath(filename)
        wrapper = ForeignShellFunctionAlias(name=funcname, shell=shell,
                                            sourcer=sourcer, filename=filename)
        funcs[funcname] = wrapper
    return funcs


class ForeignShellFunctionAlias(object):
    """This class is responsible for calling foreign shell functions as if
    they were aliases. This does not currently support taking stdin.
    """

    INPUT = ('{sourcer} "{filename}"\n'
             '{funcname} {args}\n')

    def __init__(self, name, shell, filename, sourcer=None):
        """
        Parameters
        ----------
        name : str
            function name
        shell : str
            Name or path to shell
        filename : str
            Where the function is defined, path to source.
        sourcer : str or None, optional
            Command to source foreing files with.
        """
        sourcer = DEFAULT_SOURCERS.get(shell, 'source') if sourcer is None \
                                                        else sourcer
        self.name = name
        self.shell = shell
        self.filename = filename
        self.sourcer = sourcer

    def __eq__(self, other):
        if not hasattr(other, 'name') or not hasattr(other, 'shell') or \
           not hasattr(other, 'filename') or not hasattr(other, 'sourcer'):
            return NotImplemented
        return (self.name == other.name) and (self.shell == other.shell) and \
               (self.filename == other.filename) and (self.sourcer == other.sourcer)

    def __call__(self, args, stdin=None):
        args, streaming = self._is_streaming(args)
        input = self.INPUT.format(sourcer=self.sourcer, filename=self.filename,
                                  funcname=self.name, args=' '.join(args))
        cmd = [self.shell, '-c', input]
        env = builtins.__xonsh_env__
        denv = env.detype()
        if streaming:
            subprocess.check_call(cmd, env=denv)
            out = None
        else:
            out = subprocess.check_output(cmd, env=denv, stderr=subprocess.STDOUT)
            out = out.decode(encoding=env.get('XONSH_ENCODING'),
                             errors=env.get('XONSH_ENCODING_ERRORS'))
            out = out.replace('\r\n', '\n')
        return out

    def _is_streaming(self, args):
        """Test and modify args if --xonsh-stream is present."""
        if '--xonsh-stream' not in args:
            return args, False
        args = list(args)
        args.remove('--xonsh-stream')
        return args, True


VALID_SHELL_PARAMS = frozenset(['shell', 'interactive', 'login', 'envcmd',
                                'aliascmd', 'extra_args', 'currenv', 'safe',
                                'prevcmd', 'postcmd', 'funcscmd', 'sourcer'])

def ensure_shell(shell):
    """Ensures that a mapping follows the shell specification."""
    if not isinstance(shell, MutableMapping):
        shell = dict(shell)
    shell_keys = set(shell.keys())
    if not (shell_keys <= VALID_SHELL_PARAMS):
        msg = 'unknown shell keys: {0}'
        raise KeyError(msg.format(shell_keys - VALID_SHELL_PARAMS))
    shell['shell'] = ensure_string(shell['shell'])
    if 'interactive' in shell_keys:
        shell['interactive'] = to_bool(shell['interactive'])
    if 'login' in shell_keys:
        shell['login'] = to_bool(shell['login'])
    if 'envcmd' in shell_keys:
        shell['envcmd'] = None if shell['envcmd'] is None \
                               else ensure_string(shell['envcmd'])
    if 'aliascmd' in shell_keys:
        shell['aliascmd'] = None if shell['aliascmd'] is None \
                                 else ensure_string(shell['aliascmd'])
    if 'extra_args' in shell_keys and not isinstance(shell['extra_args'], tuple):
        shell['extra_args'] = tuple(map(ensure_string, shell['extra_args']))
    if 'currenv' in shell_keys and not isinstance(shell['currenv'], tuple):
        ce = shell['currenv']
        if isinstance(ce, Mapping):
            ce = tuple([(ensure_string(k), v) for k, v in ce.items()])
        elif isinstance(ce, Sequence):
            ce = tuple([(ensure_string(k), v) for k, v in ce])
        else:
            raise RuntimeError('unrecognized type for currenv')
        shell['currenv'] = ce
    if 'safe' in shell_keys:
        shell['safe'] = to_bool(shell['safe'])
    if 'prevcmd' in shell_keys:
        shell['prevcmd'] = ensure_string(shell['prevcmd'])
    if 'postcmd' in shell_keys:
        shell['postcmd'] = ensure_string(shell['postcmd'])
    if 'funcscmd' in shell_keys:
        shell['funcscmd'] = None if shell['funcscmd'] is None \
                                 else ensure_string(shell['funcscmd'])
    if 'sourcer' in shell_keys:
        shell['sourcer'] = None if shell['sourcer'] is None \
                                 else ensure_string(shell['sourcer'])
    if 'seterrprevcmd' in shell_keys:
        shell['seterrprevcmd'] = None if shell['seterrprevcmd'] is None \
                                 else ensure_string(shell['seterrprevcmd'])
    if 'seterrpostcmd' in shell_keys:
        shell['seterrpostcmd'] = None if shell['seterrpostcmd'] is None \
                                 else ensure_string(shell['seterrpostcmd'])
    return shell


def _get_shells(shells=None, config=None, issue_warning=True):
    if shells is not None and config is not None:
        raise RuntimeError('Only one of shells and config may be non-None.')
    elif shells is not None:
        pass
    else:
        env = getattr(builtins, '__xonsh_env__', os.environ)
        if env.get('LOADED_CONFIG', False):
            conf = builtins.__xonsh_config__
        else:
            from xonsh.environ import load_static_config
            conf = load_static_config(env, config)
        shells = conf.get('foreign_shells', ())
    return shells


def load_foreign_envs(shells=None, config=None, issue_warning=True):
    """Loads environments from foreign shells.

    Parameters
    ----------
    shells : sequence of dicts, optional
        An iterable of dicts that can be passed into foreign_shell_data() as
        keyword arguments. Not compatible with config not being None.
    config : str of None, optional
        Path to the static config file. Not compatible with shell not being None.
        If both shell and config is None, then it will be read from the
        $XONSHCONFIG environment variable.
    issue_warning : bool, optional
        Issues warnings if config file cannot be found.

    Returns
    -------
    env : dict
        A dictionary of the merged environments.
    """
    shells = _get_shells(shells=shells, config=config, issue_warning=issue_warning)
    env = {}
    for shell in shells:
        shell = ensure_shell(shell)
        shenv, _ = foreign_shell_data(**shell)
        if shenv:
            env.update(shenv)
    return env


def load_foreign_aliases(shells=None, config=None, issue_warning=True):
    """Loads aliases from foreign shells.

    Parameters
    ----------
    shells : sequence of dicts, optional
        An iterable of dicts that can be passed into foreign_shell_data() as
        keyword arguments. Not compatible with config not being None.
    config : str of None, optional
        Path to the static config file. Not compatible with shell not being None.
        If both shell and config is None, then it will be read from the
        $XONSHCONFIG environment variable.
    issue_warning : bool, optional
        Issues warnings if config file cannot be found.

    Returns
    -------
    aliases : dict
        A dictionary of the merged aliases.
    """
    shells = _get_shells(shells=shells, config=config, issue_warning=issue_warning)
    aliases = {}
    for shell in shells:
        shell = ensure_shell(shell)
        _, shaliases = foreign_shell_data(**shell)
        if shaliases:
            aliases.update(shaliases)
    return aliases

#
# inspectors
#
# -*- coding: utf-8 -*-
"""Tools for inspecting Python objects.

This file was forked from the IPython project:

* Copyright (c) 2008-2014, IPython Development Team
* Copyright (C) 2001-2007 Fernando Perez <fperez@colorado.edu>
* Copyright (c) 2001, Janko Hauser <jhauser@zscout.de>
* Copyright (c) 2001, Nathaniel Gray <n8gray@caltech.edu>
"""
from collections import namedtuple
inspect = _LazyModule.load('inspect', 'inspect')
stdlib_io = _LazyModule.load('io', 'io', 'stdlib_io')
from itertools import zip_longest
linecache = _LazyModule.load('linecache', 'linecache')
# amalgamated os
# amalgamated sys
# amalgamated types
# amalgamated importlib
# amalgamated xonsh.lazyasd
# amalgamated xonsh.tokenize
# amalgamated xonsh.openpy
# amalgamated xonsh.tools
# amalgamated xonsh.platform
pygments = LazyObject(lambda: importlib.import_module('pygments'),
                      globals(), 'pygments')
pyghooks = LazyObject(lambda: importlib.import_module('xonsh.pyghooks'),
                      globals(), 'pyghooks')


# builtin docstrings to ignore
_func_call_docstring = types.FunctionType.__call__.__doc__
_object_init_docstring = object.__init__.__doc__
_builtin_type_docstrings = {
    t.__doc__
    for t in (types.ModuleType, types.MethodType, types.FunctionType)
}

_builtin_func_type = type(all)
_builtin_meth_type = type(
    str.upper)  # Bound methods have the same type as builtin functions

info_fields = [
    'type_name', 'base_class', 'string_form', 'namespace', 'length', 'file',
    'definition', 'docstring', 'source', 'init_definition', 'class_docstring',
    'init_docstring', 'call_def', 'call_docstring',
    # These won't be printed but will be used to determine how to
    # format the object
    'ismagic', 'isalias', 'isclass', 'argspec', 'found', 'name'
]


def object_info(**kw):
    """Make an object info dict with all fields present."""
    infodict = dict(zip_longest(info_fields, [None]))
    infodict.update(kw)
    return infodict


def get_encoding(obj):
    """Get encoding for python source file defining obj

    Returns None if obj is not defined in a sourcefile.
    """
    ofile = find_file(obj)
    # run contents of file through pager starting at line where the object
    # is defined, as long as the file isn't binary and is actually on the
    # filesystem.
    if ofile is None:
        return None
    elif ofile.endswith(('.so', '.dll', '.pyd')):
        return None
    elif not os.path.isfile(ofile):
        return None
    else:
        # Print only text files, not extension binaries.  Note that
        # getsourcelines returns lineno with 1-offset and page() uses
        # 0-offset, so we must adjust.
        with stdlib_io.open(ofile, 'rb') as buf:  # Tweaked to use io.open for Python 2
            encoding, _ = detect_encoding(buf.readline)
        return encoding


def getdoc(obj):
    """Stable wrapper around inspect.getdoc.

    This can't crash because of attribute problems.

    It also attempts to call a getdoc() method on the given object.  This
    allows objects which provide their docstrings via non-standard mechanisms
    (like Pyro proxies) to still be inspected by ipython's ? system."""
    # Allow objects to offer customized documentation via a getdoc method:
    try:
        ds = obj.getdoc()
    except Exception:  # pylint:disable=broad-except
        pass
    else:
        # if we get extra info, we add it to the normal docstring.
        if isinstance(ds, str):
            return inspect.cleandoc(ds)

    try:
        docstr = inspect.getdoc(obj)
        encoding = get_encoding(obj)
        return cast_unicode(docstr, encoding=encoding)
    except Exception:  # pylint:disable=broad-except
        # Harden against an inspect failure, which can occur with
        # SWIG-wrapped extensions.
        raise


def getsource(obj, is_binary=False):
    """Wrapper around inspect.getsource.

    This can be modified by other projects to provide customized source
    extraction.

    Inputs:

    - obj: an object whose source code we will attempt to extract.

    Optional inputs:

    - is_binary: whether the object is known to come from a binary source.
      This implementation will skip returning any output for binary objects,
      but custom extractors may know how to meaningfully process them."""

    if is_binary:
        return None
    else:
        # get source if obj was decorated with @decorator
        if hasattr(obj, "__wrapped__"):
            obj = obj.__wrapped__
        try:
            src = inspect.getsource(obj)
        except TypeError:
            if hasattr(obj, '__class__'):
                src = inspect.getsource(obj.__class__)
        encoding = get_encoding(obj)
        return cast_unicode(src, encoding=encoding)


def is_simple_callable(obj):
    """True if obj is a function ()"""
    return (inspect.isfunction(obj) or
            inspect.ismethod(obj) or
            isinstance(obj, _builtin_func_type) or
            isinstance(obj, _builtin_meth_type))


def getargspec(obj):
    """Wrapper around :func:`inspect.getfullargspec` on Python 3, and
    :func:inspect.getargspec` on Python 2.

    In addition to functions and methods, this can also handle objects with a
    ``__call__`` attribute.
    """
    if safe_hasattr(obj, '__call__') and not is_simple_callable(obj):
        obj = obj.__call__

    return inspect.getfullargspec(obj)


def format_argspec(argspec):
    """Format argspect, convenience wrapper around inspect's.

    This takes a dict instead of ordered arguments and calls
    inspect.format_argspec with the arguments in the necessary order.
    """
    return inspect.formatargspec(argspec['args'], argspec['varargs'],
                                 argspec['varkw'], argspec['defaults'])


def call_tip(oinfo, format_call=True):
    """Extract call tip data from an oinfo dict.

    Parameters
    ----------
    oinfo : dict

    format_call : bool, optional
      If True, the call line is formatted and returned as a string.  If not, a
      tuple of (name, argspec) is returned.

    Returns
    -------
    call_info : None, str or (str, dict) tuple.
      When format_call is True, the whole call information is formattted as a
      single string.  Otherwise, the object's name and its argspec dict are
      returned.  If no call information is available, None is returned.

    docstring : str or None
      The most relevant docstring for calling purposes is returned, if
      available.  The priority is: call docstring for callable instances, then
      constructor docstring for classes, then main object's docstring otherwise
      (regular functions).
    """
    # Get call definition
    argspec = oinfo.get('argspec')
    if argspec is None:
        call_line = None
    else:
        # Callable objects will have 'self' as their first argument, prune
        # it out if it's there for clarity (since users do *not* pass an
        # extra first argument explicitly).
        try:
            has_self = argspec['args'][0] == 'self'
        except (KeyError, IndexError):
            pass
        else:
            if has_self:
                argspec['args'] = argspec['args'][1:]

        call_line = oinfo['name'] + format_argspec(argspec)

    # Now get docstring.
    # The priority is: call docstring, constructor docstring, main one.
    doc = oinfo.get('call_docstring')
    if doc is None:
        doc = oinfo.get('init_docstring')
    if doc is None:
        doc = oinfo.get('docstring', '')

    return call_line, doc


def find_file(obj):
    """Find the absolute path to the file where an object was defined.

    This is essentially a robust wrapper around `inspect.getabsfile`.

    Returns None if no file can be found.

    Parameters
    ----------
    obj : any Python object

    Returns
    -------
    fname : str
      The absolute path to the file where the object was defined.
    """
    # get source if obj was decorated with @decorator
    if safe_hasattr(obj, '__wrapped__'):
        obj = obj.__wrapped__

    fname = None
    try:
        fname = inspect.getabsfile(obj)
    except TypeError:
        # For an instance, the file that matters is where its class was
        # declared.
        if hasattr(obj, '__class__'):
            try:
                fname = inspect.getabsfile(obj.__class__)
            except TypeError:
                # Can happen for builtins
                pass
    except:  # pylint:disable=bare-except
        pass
    return cast_unicode(fname)


def find_source_lines(obj):
    """Find the line number in a file where an object was defined.

    This is essentially a robust wrapper around `inspect.getsourcelines`.

    Returns None if no file can be found.

    Parameters
    ----------
    obj : any Python object

    Returns
    -------
    lineno : int
      The line number where the object definition starts.
    """
    # get source if obj was decorated with @decorator
    if safe_hasattr(obj, '__wrapped__'):
        obj = obj.__wrapped__

    try:
        try:
            lineno = inspect.getsourcelines(obj)[1]
        except TypeError:
            # For instances, try the class object like getsource() does
            if hasattr(obj, '__class__'):
                lineno = inspect.getsourcelines(obj.__class__)[1]
            else:
                lineno = None
    except:  # pylint:disable=bare-except
        return None

    return lineno


if PYTHON_VERSION_INFO < (3, 5, 0):
    FrameInfo = namedtuple('FrameInfo', ['frame', 'filename', 'lineno', 'function',
                                         'code_context', 'index'])
    def getouterframes(frame, context=1):
        """Wrapper for getouterframes so that it acts like the Python v3.5 version."""
        return [FrameInfo(*f) for f in inspect.getouterframes(frame, context=context)]
else:
    getouterframes = inspect.getouterframes


class Inspector(object):
    """Inspects objects."""

    def __init__(self, str_detail_level=0):
        self.str_detail_level = str_detail_level

    def _getdef(self, obj, oname=''):
        """Return the call signature for any callable object.

        If any exception is generated, None is returned instead and the
        exception is suppressed.
        """
        try:
            hdef = oname + inspect.formatargspec(*getargspec(obj))
            return cast_unicode(hdef)
        except:  # pylint:disable=bare-except
            return None

    def noinfo(self, msg, oname):
        """Generic message when no information is found."""
        print('No %s found' % msg, end=' ')
        if oname:
            print('for %s' % oname)
        else:
            print()

    def pdef(self, obj, oname=''):
        """Print the call signature for any callable object.

        If the object is a class, print the constructor information.
        """

        if not callable(obj):
            print('Object is not callable.')
            return

        header = ''

        if inspect.isclass(obj):
            header = self.__head('Class constructor information:\n')
            obj = obj.__init__

        output = self._getdef(obj, oname)
        if output is None:
            self.noinfo('definition header', oname)
        else:
            print(header, output, end=' ', file=sys.stdout)

    def pdoc(self, obj, oname=''):
        """Print the docstring for any object.

        Optional

        -formatter: a function to run the docstring through for specially
        formatted docstrings.
        """

        head = self.__head  # For convenience
        lines = []
        ds = getdoc(obj)
        if ds:
            lines.append(head("Class docstring:"))
            lines.append(indent(ds))
        if inspect.isclass(obj) and hasattr(obj, '__init__'):
            init_ds = getdoc(obj.__init__)
            if init_ds is not None:
                lines.append(head("Init docstring:"))
                lines.append(indent(init_ds))
        elif hasattr(obj, '__call__'):
            call_ds = getdoc(obj.__call__)
            if call_ds:
                lines.append(head("Call docstring:"))
                lines.append(indent(call_ds))

        if not lines:
            self.noinfo('documentation', oname)
        else:
            print('\n'.join(lines))

    def psource(self, obj, oname=''):
        """Print the source code for an object."""
        # Flush the source cache because inspect can return out-of-date source
        linecache.checkcache()
        try:
            src = getsource(obj)
        except:  # pylint:disable=bare-except
            self.noinfo('source', oname)
        else:
            print(src)

    def pfile(self, obj, oname=''):
        """Show the whole file where an object was defined."""
        lineno = find_source_lines(obj)
        if lineno is None:
            self.noinfo('file', oname)
            return

        ofile = find_file(obj)
        # run contents of file through pager starting at line where the object
        # is defined, as long as the file isn't binary and is actually on the
        # filesystem.
        if ofile.endswith(('.so', '.dll', '.pyd')):
            print('File %r is binary, not printing.' % ofile)
        elif not os.path.isfile(ofile):
            print('File %r does not exist, not printing.' % ofile)
        else:
            # Print only text files, not extension binaries.  Note that
            # getsourcelines returns lineno with 1-offset and page() uses
            # 0-offset, so we must adjust.
            o = read_py_file(ofile, skip_encoding_cookie=False)
            print(o, lineno - 1)

    def _format_fields_str(self, fields, title_width=0):
        """Formats a list of fields for display using color strings.

        Parameters
        ----------
        fields : list
          A list of 2-tuples: (field_title, field_content)
        title_width : int
          How many characters to pad titles to. Default to longest title.
        """
        out = []
        if title_width == 0:
            title_width = max(len(title) + 2 for title, _ in fields)
        for title, content in fields:
            title_len = len(title)
            title = '{BOLD_RED}' + title + ':{NO_COLOR}'
            if len(content.splitlines()) > 1:
                title += '\n'
            else:
                title += " ".ljust(title_width - title_len)
            out.append(cast_unicode(title) + cast_unicode(content))
        return format_color("\n".join(out) + '\n')

    def _format_fields_tokens(self, fields, title_width=0):
        """Formats a list of fields for display using color tokens from
        pygments.

        Parameters
        ----------
        fields : list
          A list of 2-tuples: (field_title, field_content)
        title_width : int
          How many characters to pad titles to. Default to longest title.
        """
        out = []
        if title_width == 0:
            title_width = max(len(title) + 2 for title, _ in fields)
        for title, content in fields:
            title_len = len(title)
            title = '{BOLD_RED}' + title + ':{NO_COLOR}'
            if not isinstance(content, str) or len(content.splitlines()) > 1:
                title += '\n'
            else:
                title += " ".ljust(title_width - title_len)
            out += pyghooks.partial_color_tokenize(title)
            if isinstance(content, str):
                out[-1] = (out[-1][0], out[-1][1] + content + '\n')
            else:
                out += content
                out[-1] = (out[-1][0], out[-1][1] + '\n')
        out[-1] = (out[-1][0], out[-1][1] + '\n')
        return out

    def _format_fields(self, fields, title_width=0):
        """Formats a list of fields for display using color tokens from
        pygments.

        Parameters
        ----------
        fields : list
          A list of 2-tuples: (field_title, field_content)
        title_width : int
          How many characters to pad titles to. Default to longest title.
        """
        if HAS_PYGMENTS:
            rtn = self._format_fields_tokens(fields, title_width=title_width)
        else:
            rtn = self._format_fields_str(fields, title_width=title_width)
        return rtn

    # The fields to be displayed by pinfo: (fancy_name, key_in_info_dict)
    pinfo_fields1 = [("Type", "type_name")]

    pinfo_fields2 = [("String form", "string_form")]

    pinfo_fields3 = [("Length", "length"),
                     ("File", "file"),
                     ("Definition", "definition"), ]

    pinfo_fields_obj = [("Class docstring", "class_docstring"),
                        ("Init docstring", "init_docstring"),
                        ("Call def", "call_def"),
                        ("Call docstring", "call_docstring"), ]

    def pinfo(self, obj, oname='', info=None, detail_level=0):
        """Show detailed information about an object.

        Parameters
        ----------
        obj : object
        oname : str, optional
            name of the variable pointing to the object.
        info : dict, optional
            a structure with some information fields which may have been
            precomputed already.
        detail_level : int, optional
            if set to 1, more information is given.
        """
        info = self.info(obj,
                         oname=oname,
                         info=info,
                         detail_level=detail_level)
        displayfields = []

        def add_fields(fields):
            for title, key in fields:
                field = info[key]
                if field is not None:
                    displayfields.append((title, field.rstrip()))

        add_fields(self.pinfo_fields1)
        add_fields(self.pinfo_fields2)

        # Namespace
        if (info['namespace'] is not None and
           info['namespace'] != 'Interactive'):
                displayfields.append(("Namespace", info['namespace'].rstrip()))

        add_fields(self.pinfo_fields3)
        if info['isclass'] and info['init_definition']:
            displayfields.append(("Init definition",
                                  info['init_definition'].rstrip()))

        # Source or docstring, depending on detail level and whether
        # source found.
        if detail_level > 0 and info['source'] is not None:
            displayfields.append(("Source", cast_unicode(info['source'])))
        elif info['docstring'] is not None:
            displayfields.append(("Docstring", info["docstring"]))

        # Constructor info for classes
        if info['isclass']:
            if info['init_docstring'] is not None:
                displayfields.append(("Init docstring",
                                      info['init_docstring']))

        # Info for objects:
        else:
            add_fields(self.pinfo_fields_obj)

        # Finally send to printer/pager:
        if displayfields:
            print_color(self._format_fields(displayfields))

    def info(self, obj, oname='', info=None, detail_level=0):
        """Compute a dict with detailed information about an object.

        Optional arguments:

        - oname: name of the variable pointing to the object.

        - info: a structure with some information fields which may have been
          precomputed already.

        - detail_level: if set to 1, more information is given.
        """
        obj_type = type(obj)
        if info is None:
            ismagic = 0
            isalias = 0
            ospace = ''
        else:
            ismagic = info.ismagic
            isalias = info.isalias
            ospace = info.namespace
        # Get docstring, special-casing aliases:
        if isalias:
            if not callable(obj):
                if len(obj) >= 2 and isinstance(obj[1], str):
                    ds = "Alias to the system command:\n  {0}".format(obj[1])
                else:  # pylint:disable=bare-except
                    ds = "Alias: " + str(obj)
            else:
                ds = "Alias to " + str(obj)
                if obj.__doc__:
                    ds += "\nDocstring:\n" + obj.__doc__
        else:
            ds = getdoc(obj)
            if ds is None:
                ds = '<no docstring>'

        # store output in a dict, we initialize it here and fill it as we go
        out = dict(name=oname, found=True, isalias=isalias, ismagic=ismagic)

        string_max = 200  # max size of strings to show (snipped if longer)
        shalf = int((string_max - 5) / 2)

        if ismagic:
            obj_type_name = 'Magic function'
        elif isalias:
            obj_type_name = 'System alias'
        else:
            obj_type_name = obj_type.__name__
        out['type_name'] = obj_type_name

        try:
            bclass = obj.__class__
            out['base_class'] = str(bclass)
        except:  # pylint:disable=bare-except
            pass

        # String form, but snip if too long in ? form (full in ??)
        if detail_level >= self.str_detail_level:
            try:
                ostr = str(obj)
                str_head = 'string_form'
                if not detail_level and len(ostr) > string_max:
                    ostr = ostr[:shalf] + ' <...> ' + ostr[-shalf:]
                    ostr = ("\n" + " " * len(str_head.expandtabs())).\
                           join(q.strip() for q in ostr.split("\n"))
                out[str_head] = ostr
            except:  # pylint:disable=bare-except
                pass

        if ospace:
            out['namespace'] = ospace

        # Length (for strings and lists)
        try:
            out['length'] = str(len(obj))
        except:  # pylint:disable=bare-except
            pass

        # Filename where object was defined
        binary_file = False
        fname = find_file(obj)
        if fname is None:
            # if anything goes wrong, we don't want to show source, so it's as
            # if the file was binary
            binary_file = True
        else:
            if fname.endswith(('.so', '.dll', '.pyd')):
                binary_file = True
            elif fname.endswith('<string>'):
                fname = ('Dynamically generated function. '
                         'No source code available.')
            out['file'] = fname

        # Docstrings only in detail 0 mode, since source contains them (we
        # avoid repetitions).  If source fails, we add them back, see below.
        if ds and detail_level == 0:
            out['docstring'] = ds

        # Original source code for any callable
        if detail_level:
            # Flush the source cache because inspect can return out-of-date
            # source
            linecache.checkcache()
            source = None
            try:
                try:
                    source = getsource(obj, binary_file)
                except TypeError:
                    if hasattr(obj, '__class__'):
                        source = getsource(obj.__class__, binary_file)
                if source is not None:
                    source = source.rstrip()
                    if HAS_PYGMENTS:
                        lexer = pyghooks.XonshLexer()
                        source = list(pygments.lex(source, lexer=lexer))
                    out['source'] = source
            except Exception:  # pylint:disable=broad-except
                pass

            if ds and source is None:
                out['docstring'] = ds

        # Constructor docstring for classes
        if inspect.isclass(obj):
            out['isclass'] = True
            # reconstruct the function definition and print it:
            try:
                obj_init = obj.__init__
            except AttributeError:
                init_def = init_ds = None
            else:
                init_def = self._getdef(obj_init, oname)
                init_ds = getdoc(obj_init)
                # Skip Python's auto-generated docstrings
                if init_ds == _object_init_docstring:
                    init_ds = None

            if init_def or init_ds:
                if init_def:
                    out['init_definition'] = init_def
                if init_ds:
                    out['init_docstring'] = init_ds

        # and class docstring for instances:
        else:
            # reconstruct the function definition and print it:
            defln = self._getdef(obj, oname)
            if defln:
                out['definition'] = defln

            # First, check whether the instance docstring is identical to the
            # class one, and print it separately if they don't coincide.  In
            # most cases they will, but it's nice to print all the info for
            # objects which use instance-customized docstrings.
            if ds:
                try:
                    cls = getattr(obj, '__class__')
                except:  # pylint:disable=bare-except
                    class_ds = None
                else:
                    class_ds = getdoc(cls)
                # Skip Python's auto-generated docstrings
                if class_ds in _builtin_type_docstrings:
                    class_ds = None
                if class_ds and ds != class_ds:
                    out['class_docstring'] = class_ds

            # Next, try to show constructor docstrings
            try:
                init_ds = getdoc(obj.__init__)
                # Skip Python's auto-generated docstrings
                if init_ds == _object_init_docstring:
                    init_ds = None
            except AttributeError:
                init_ds = None
            if init_ds:
                out['init_docstring'] = init_ds

            # Call form docstring for callable instances
            if safe_hasattr(obj, '__call__') and not is_simple_callable(obj):
                call_def = self._getdef(obj.__call__, oname)
                if call_def:
                    call_def = call_def
                    # it may never be the case that call def and definition
                    # differ, but don't include the same signature twice
                    if call_def != out.get('definition'):
                        out['call_def'] = call_def
                call_ds = getdoc(obj.__call__)
                # Skip Python's auto-generated docstrings
                if call_ds == _func_call_docstring:
                    call_ds = None
                if call_ds:
                    out['call_docstring'] = call_ds

        # Compute the object's argspec as a callable.  The key is to decide
        # whether to pull it from the object itself, from its __init__ or
        # from its __call__ method.

        if inspect.isclass(obj):
            # Old-style classes need not have an __init__
            callable_obj = getattr(obj, "__init__", None)
        elif callable(obj):
            callable_obj = obj
        else:
            callable_obj = None

        if callable_obj:
            try:
                argspec = getargspec(callable_obj)
            except (TypeError, AttributeError):
                # For extensions/builtins we can't retrieve the argspec
                pass
            else:
                # named tuples' _asdict() method returns an OrderedDict, but we
                # we want a normal
                out['argspec'] = argspec_dict = dict(argspec._asdict())
                # We called this varkw before argspec became a named tuple.
                # With getfullargspec it's also called varkw.
                if 'varkw' not in argspec_dict:
                    argspec_dict['varkw'] = argspec_dict.pop('keywords')

        return object_info(**out)

#
# lexer
#
# -*- coding: utf-8 -*-
"""Lexer for xonsh code.

Written using a hybrid of ``tokenize`` and PLY.
"""
from io import BytesIO
from keyword import kwlist

try:
    from ply.lex import LexToken
except ImportError:
    from xonsh.ply.lex import LexToken

# amalgamated xonsh.lazyasd
# amalgamated xonsh.platform
# amalgamated xonsh.tokenize
def _token_map():
    tm = {}
    # operators
    _op_map = {
        # punctuation
        ',': 'COMMA', '.': 'PERIOD', ';': 'SEMI', ':': 'COLON',
        '...': 'ELLIPSIS',
        # basic operators
        '+': 'PLUS', '-': 'MINUS', '*': 'TIMES', '@': 'AT', '/': 'DIVIDE',
        '//': 'DOUBLEDIV', '%': 'MOD', '**': 'POW', '|': 'PIPE',
        '~': 'TILDE', '^': 'XOR', '<<': 'LSHIFT', '>>': 'RSHIFT',
        '<': 'LT', '<=': 'LE', '>': 'GT', '>=': 'GE', '==': 'EQ',
        '!=': 'NE', '->': 'RARROW',
        # assignment operators
        '=': 'EQUALS', '+=': 'PLUSEQUAL', '-=': 'MINUSEQUAL',
        '*=': 'TIMESEQUAL', '@=': 'ATEQUAL', '/=': 'DIVEQUAL', '%=': 'MODEQUAL',
        '**=': 'POWEQUAL', '<<=': 'LSHIFTEQUAL', '>>=': 'RSHIFTEQUAL',
        '&=': 'AMPERSANDEQUAL', '^=': 'XOREQUAL', '|=': 'PIPEEQUAL',
        '//=': 'DOUBLEDIVEQUAL',
        # extra xonsh operators
        '?': 'QUESTION', '??': 'DOUBLE_QUESTION', '@$': 'ATDOLLAR',
        '&': 'AMPERSAND',
    }
    for (op, typ) in _op_map.items():
        tm[(OP, op)] = typ
    tm[IOREDIRECT] = 'IOREDIRECT'
    tm[STRING] = 'STRING'
    tm[DOLLARNAME] = 'DOLLAR_NAME'
    tm[NUMBER] = 'NUMBER'
    tm[SEARCHPATH] = 'SEARCHPATH'
    tm[NEWLINE] = 'NEWLINE'
    tm[INDENT] = 'INDENT'
    tm[DEDENT] = 'DEDENT'
    if PYTHON_VERSION_INFO >= (3, 5, 0):
        from xonsh.tokenize import ASYNC, AWAIT
        tm[ASYNC] = 'ASYNC'
        tm[AWAIT] = 'AWAIT'
    return tm


token_map = LazyObject(_token_map, globals(), 'token_map')
"""
Mapping from ``tokenize`` tokens (or token types) to PLY token types.  If a
simple one-to-one mapping from ``tokenize`` to PLY exists, the lexer will look
it up here and generate a single PLY token of the given type.  Otherwise, it
will fall back to handling that token using one of the handlers in
``special_handlers``.
"""
del _token_map


def _make_matcher_handler(tok, typ, pymode, ender):
    matcher = (')' if tok.endswith('(') else
               '}' if tok.endswith('{') else
               ']' if tok.endswith('[') else None)

    def _inner_handler(state, token):
        state['pymode'].append((pymode, tok, matcher, token.start))
        state['last'] = token
        yield _new_token(typ, tok, token.start)
    special_handlers[(OP, tok)] = _inner_handler


def handle_name(state, token):
    """
    Function for handling name tokens
    """
    typ = 'NAME'
    state['last'] = token
    if state['pymode'][-1][0]:
        if token.string in kwlist:
            typ = token.string.upper()
        yield _new_token(typ, token.string, token.start)
    else:
        if token.string == 'and':
            yield _new_token('AND', token.string, token.start)
        elif token.string == 'or':
            yield _new_token('OR', token.string, token.start)
        else:
            yield _new_token('NAME', token.string, token.start)


def _end_delimiter(state, token):
    py = state['pymode']
    s = token.string
    l, c = token.start
    if len(py) > 1:
        mode, orig, match, pos = py.pop()
        if s != match:
            e = '"{}" at {} ends "{}" at {} (expected "{}")'
            return e.format(s, (l, c), orig, pos, match)
    else:
        return 'Unmatched "{}" at line {}, column {}'.format(s, l, c)


def handle_rparen(state, token):
    """
    Function for handling ``)``
    """
    e = _end_delimiter(state, token)
    if e is None:
        state['last'] = token
        yield _new_token('RPAREN', ')', token.start)
    else:
        yield _new_token('ERRORTOKEN', e, token.start)


def handle_rbrace(state, token):
    """
    Function for handling ``}``
    """
    e = _end_delimiter(state, token)
    if e is None:
        state['last'] = token
        yield _new_token('RBRACE', '}', token.start)
    else:
        yield _new_token('ERRORTOKEN', e, token.start)


def handle_rbracket(state, token):
    """
    Function for handling ``]``
    """
    e = _end_delimiter(state, token)
    if e is None:
        state['last'] = token
        yield _new_token('RBRACKET', ']', token.start)
    else:
        yield _new_token('ERRORTOKEN', e, token.start)


def handle_error_space(state, token):
    """
    Function for handling special whitespace characters in subprocess mode
    """
    if not state['pymode'][-1][0]:
        state['last'] = token
        yield _new_token('WS', token.string, token.start)
    else:
        yield from []


def handle_error_token(state, token):
    """
    Function for handling error tokens
    """
    state['last'] = token
    if not state['pymode'][-1][0]:
        typ = 'NAME'
    else:
        typ = 'ERRORTOKEN'
    yield _new_token(typ, token.string, token.start)


def handle_ignore(state, token):
    """
    Function for handling tokens that should be ignored
    """
    yield from []


def handle_double_amps(state, token):
    yield _new_token('AND', 'and', token.start)


def handle_double_pipe(state, token):
    yield _new_token('OR', 'or', token.start)


special_handlers = {
    NL: handle_ignore,
    COMMENT: handle_ignore,
    ENCODING: handle_ignore,
    ENDMARKER: handle_ignore,
    NAME: handle_name,
    ERRORTOKEN: handle_error_token,
    (OP, ')'): handle_rparen,
    (OP, '}'): handle_rbrace,
    (OP, ']'): handle_rbracket,
    (OP, '&&'): handle_double_amps,
    (OP, '||'): handle_double_pipe,
    (ERRORTOKEN, ' '): handle_error_space,
}
"""
Mapping from ``tokenize`` tokens (or token types) to the proper function for
generating PLY tokens from them.  In addition to yielding PLY tokens, these
functions may manipulate the Lexer's state.
"""

_make_matcher_handler('(', 'LPAREN', True, ')')
_make_matcher_handler('[', 'LBRACKET', True, ']')
_make_matcher_handler('{', 'LBRACE', True, '}')
_make_matcher_handler('$(', 'DOLLAR_LPAREN', False, ')')
_make_matcher_handler('$[', 'DOLLAR_LBRACKET', False, ']')
_make_matcher_handler('${', 'DOLLAR_LBRACE', True, '}')
_make_matcher_handler('!(', 'BANG_LPAREN', False, ')')
_make_matcher_handler('![', 'BANG_LBRACKET', False, ']')
_make_matcher_handler('@(', 'AT_LPAREN', True, ')')
_make_matcher_handler('@$(', 'ATDOLLAR_LPAREN', False, ')')


def handle_token(state, token):
    """
    General-purpose token handler.  Makes use of ``token_map`` or
    ``special_map`` to yield one or more PLY tokens from the given input.

    Parameters
    ----------

    state :
        The current state of the lexer, including information about whether
        we are in Python mode or subprocess mode, which changes the lexer's
        behavior.  Also includes the stream of tokens yet to be considered.
    token :
        The token (from ``tokenize``) currently under consideration
    """
    typ = token.type
    st = token.string
    pymode = state['pymode'][-1][0]
    if not pymode:
        if state['last'] is not None and state['last'].end != token.start:
            cur = token.start
            old = state['last'].end
            if cur[0] == old[0] and cur[1] > old[1]:
                yield _new_token('WS', token.line[old[1]:cur[1]], old)
    if (typ, st) in special_handlers:
        yield from special_handlers[(typ, st)](state, token)
    elif (typ, st) in token_map:
        state['last'] = token
        yield _new_token(token_map[(typ, st)], st, token.start)
    elif typ in special_handlers:
        yield from special_handlers[typ](state, token)
    elif typ in token_map:
        state['last'] = token
        yield _new_token(token_map[typ], st, token.start)
    else:
        m = "Unexpected token: {0}".format(token)
        yield _new_token("ERRORTOKEN", m, token.start)


def get_tokens(s):
    """
    Given a string containing xonsh code, generates a stream of relevant PLY
    tokens using ``handle_token``.
    """
    state = {'indents': [0], 'last': None,
             'pymode': [(True, '', '', (0, 0))],
             'stream': tokenize(BytesIO(s.encode('utf-8')).readline)}
    while True:
        try:
            token = next(state['stream'])
            yield from handle_token(state, token)
        except StopIteration:
            if len(state['pymode']) > 1:
                pm, o, m, p = state['pymode'][-1]
                l, c = p
                e = 'Unmatched "{}" at line {}, column {}'
                yield _new_token('ERRORTOKEN', e.format(o, l, c), (0, 0))
            break
        except TokenError as e:
            # this is recoverable in single-line mode (from the shell)
            # (e.g., EOF while scanning string literal)
            yield _new_token('ERRORTOKEN', e.args[0], (0, 0))
            break
        except IndentationError as e:
            # this is never recoverable
            yield _new_token('ERRORTOKEN', e, (0, 0))
            break


# synthesize a new PLY token
def _new_token(type, value, pos):
    o = LexToken()
    o.type = type
    o.value = value
    o.lineno, o.lexpos = pos
    return o


class Lexer(object):
    """Implements a lexer for the xonsh language."""

    def __init__(self):
        """
        Attributes
        ----------
        fname : str
            Filename
        last : token
            The last token seen.
        lineno : int
            The last line number seen.

        """
        self.fname = ''
        self.last = None
        self.beforelast = None

    def build(self, **kwargs):
        """Part of the PLY lexer API."""
        pass

    def reset(self):
        pass

    def input(self, s):
        """Calls the lexer on the string s."""
        self.token_stream = get_tokens(s)

    def token(self):
        """Retrieves the next token."""
        self.beforelast = self.last
        self.last = next(self.token_stream, None)
        return self.last

    def __iter__(self):
        t = self.token()
        while t is not None:
            yield t
            t = self.token()

    #
    # All the tokens recognized by the lexer
    #
    tokens = tuple(token_map.values()) + (
        'NAME',                  # name tokens
        'WS',                    # whitespace in subprocess mode
        'LPAREN', 'RPAREN',      # ( )
        'LBRACKET', 'RBRACKET',  # [ ]
        'LBRACE', 'RBRACE',      # { }
        'AT_LPAREN',             # @(
        'BANG_LPAREN',           # !(
        'BANG_LBRACKET',         # ![
        'DOLLAR_LPAREN',         # $(
        'DOLLAR_LBRACE',         # ${
        'DOLLAR_LBRACKET',       # $[
        'ATDOLLAR_LPAREN',       # @$(
    ) + tuple(i.upper() for i in kwlist)

#
# proc
#
# -*- coding: utf-8 -*-
"""Interface for running Python functions as subprocess-mode commands.

Code for several helper methods in the `ProcProxy` class have been reproduced
without modification from `subprocess.py` in the Python 3.4.2 standard library.
The contents of `subprocess.py` (and, thus, the reproduced methods) are
Copyright (c) 2003-2005 by Peter Astrand <astrand@lysator.liu.se> and were
licensed to the Python Software foundation under a Contributor Agreement.
"""
# amalgamated io
# amalgamated os
# amalgamated sys
# amalgamated time
# amalgamated builtins
from functools import wraps
from threading import Thread
# amalgamated from collections import Sequence, namedtuple
from subprocess import Popen, PIPE, DEVNULL, STDOUT, TimeoutExpired
# amalgamated xonsh.tools
if ON_LINUX:
    from xonsh.teepty import TeePTY
else:
    TeePTY = None

if ON_WINDOWS:
    import _winapi
    import msvcrt

    class Handle(int):
        closed = False

        def Close(self, CloseHandle=_winapi.CloseHandle):
            if not self.closed:
                self.closed = True
                CloseHandle(self)

        def Detach(self):
            if not self.closed:
                self.closed = True
                return int(self)
            raise ValueError("already closed")

        def __repr__(self):
            return "Handle(%d)" % int(self)

        __del__ = Close
        __str__ = __repr__


class ProcProxy(Thread):
    """
    Class representing a function to be run as a subprocess-mode command.
    """
    def __init__(self, f, args,
                 stdin=None,
                 stdout=None,
                 stderr=None,
                 universal_newlines=False):
        """Parameters
        ----------
        f : function
            The function to be executed.
        args : list
            A (possibly empty) list containing the arguments that were given on
            the command line
        stdin : file-like, optional
            A file-like object representing stdin (input can be read from
            here).  If `stdin` is not provided or if it is explicitly set to
            `None`, then an instance of `io.StringIO` representing an empty
            file is used.
        stdout : file-like, optional
            A file-like object representing stdout (normal output can be
            written here).  If `stdout` is not provided or if it is explicitly
            set to `None`, then `sys.stdout` is used.
        stderr : file-like, optional
            A file-like object representing stderr (error output can be
            written here).  If `stderr` is not provided or if it is explicitly
            set to `None`, then `sys.stderr` is used.
        """
        self.f = f
        """
        The function to be executed.  It should be a function of four
        arguments, described below.

        Parameters
        ----------
        args : list
            A (possibly empty) list containing the arguments that were given on
            the command line
        stdin : file-like
            A file-like object representing stdin (input can be read from
            here).
        stdout : file-like
            A file-like object representing stdout (normal output can be
            written here).
        stderr : file-like
            A file-like object representing stderr (error output can be
            written here).
        """
        self.args = args
        self.pid = None
        self.returncode = None
        self.wait = self.join

        handles = self._get_handles(stdin, stdout, stderr)
        (self.p2cread, self.p2cwrite,
         self.c2pread, self.c2pwrite,
         self.errread, self.errwrite) = handles

        # default values
        self.stdin = stdin
        self.stdout = None
        self.stderr = None

        if ON_WINDOWS:
            if self.p2cwrite != -1:
                self.p2cwrite = msvcrt.open_osfhandle(self.p2cwrite.Detach(), 0)
            if self.c2pread != -1:
                self.c2pread = msvcrt.open_osfhandle(self.c2pread.Detach(), 0)
            if self.errread != -1:
                self.errread = msvcrt.open_osfhandle(self.errread.Detach(), 0)

        if self.p2cwrite != -1:
            self.stdin = io.open(self.p2cwrite, 'wb', -1)
            if universal_newlines:
                self.stdin = io.TextIOWrapper(self.stdin, write_through=True,
                                              line_buffering=False)
        if self.c2pread != -1:
            self.stdout = io.open(self.c2pread, 'rb', -1)
            if universal_newlines:
                self.stdout = io.TextIOWrapper(self.stdout)

        if self.errread != -1:
            self.stderr = io.open(self.errread, 'rb', -1)
            if universal_newlines:
                self.stderr = io.TextIOWrapper(self.stderr)

        Thread.__init__(self)
        self.start()

    def run(self):
        """Set up input/output streams and execute the child function in a new
        thread.  This is part of the `threading.Thread` interface and should
        not be called directly.
        """
        if self.f is None:
            return
        if self.stdin is not None:
            sp_stdin = io.TextIOWrapper(self.stdin)
        else:
            sp_stdin = io.StringIO("")

        if ON_WINDOWS:
            if self.c2pwrite != -1:
                self.c2pwrite = msvcrt.open_osfhandle(self.c2pwrite.Detach(), 0)
            if self.errwrite != -1:
                self.errwrite = msvcrt.open_osfhandle(self.errwrite.Detach(), 0)

        if self.c2pwrite != -1:
            sp_stdout = io.TextIOWrapper(io.open(self.c2pwrite, 'wb', -1))
        else:
            sp_stdout = sys.stdout
        if self.errwrite == self.c2pwrite:
            sp_stderr = sp_stdout
        elif self.errwrite != -1:
            sp_stderr = io.TextIOWrapper(io.open(self.errwrite, 'wb', -1))
        else:
            sp_stderr = sys.stderr

        r = self.f(self.args, sp_stdin, sp_stdout, sp_stderr)
        self.returncode = 0 if r is None else r

    def poll(self):
        """Check if the function has completed.

        Returns
        -------
        `None` if the function is still executing, `True` if the function
        finished successfully, and `False` if there was an error.
        """
        return self.returncode

    # The code below (_get_devnull, _get_handles, and _make_inheritable) comes
    # from subprocess.py in the Python 3.4.2 Standard Library
    def _get_devnull(self):
        if not hasattr(self, '_devnull'):
            self._devnull = os.open(os.devnull, os.O_RDWR)
        return self._devnull

    if ON_WINDOWS:
        def _make_inheritable(self, handle):
            """Return a duplicate of handle, which is inheritable"""
            h = _winapi.DuplicateHandle(
                _winapi.GetCurrentProcess(), handle,
                _winapi.GetCurrentProcess(), 0, 1,
                _winapi.DUPLICATE_SAME_ACCESS)
            return Handle(h)

        def _get_handles(self, stdin, stdout, stderr):
            """Construct and return tuple with IO objects:
            p2cread, p2cwrite, c2pread, c2pwrite, errread, errwrite
            """
            if stdin is None and stdout is None and stderr is None:
                return (-1, -1, -1, -1, -1, -1)

            p2cread, p2cwrite = -1, -1
            c2pread, c2pwrite = -1, -1
            errread, errwrite = -1, -1

            if stdin is None:
                p2cread = _winapi.GetStdHandle(_winapi.STD_INPUT_HANDLE)
                if p2cread is None:
                    p2cread, _ = _winapi.CreatePipe(None, 0)
                    p2cread = Handle(p2cread)
                    _winapi.CloseHandle(_)
            elif stdin == PIPE:
                p2cread, p2cwrite = _winapi.CreatePipe(None, 0)
                p2cread, p2cwrite = Handle(p2cread), Handle(p2cwrite)
            elif stdin == DEVNULL:
                p2cread = msvcrt.get_osfhandle(self._get_devnull())
            elif isinstance(stdin, int):
                p2cread = msvcrt.get_osfhandle(stdin)
            else:
                # Assuming file-like object
                p2cread = msvcrt.get_osfhandle(stdin.fileno())
            p2cread = self._make_inheritable(p2cread)

            if stdout is None:
                c2pwrite = _winapi.GetStdHandle(_winapi.STD_OUTPUT_HANDLE)
                if c2pwrite is None:
                    _, c2pwrite = _winapi.CreatePipe(None, 0)
                    c2pwrite = Handle(c2pwrite)
                    _winapi.CloseHandle(_)
            elif stdout == PIPE:
                c2pread, c2pwrite = _winapi.CreatePipe(None, 0)
                c2pread, c2pwrite = Handle(c2pread), Handle(c2pwrite)
            elif stdout == DEVNULL:
                c2pwrite = msvcrt.get_osfhandle(self._get_devnull())
            elif isinstance(stdout, int):
                c2pwrite = msvcrt.get_osfhandle(stdout)
            else:
                # Assuming file-like object
                c2pwrite = msvcrt.get_osfhandle(stdout.fileno())
            c2pwrite = self._make_inheritable(c2pwrite)

            if stderr is None:
                errwrite = _winapi.GetStdHandle(_winapi.STD_ERROR_HANDLE)
                if errwrite is None:
                    _, errwrite = _winapi.CreatePipe(None, 0)
                    errwrite = Handle(errwrite)
                    _winapi.CloseHandle(_)
            elif stderr == PIPE:
                errread, errwrite = _winapi.CreatePipe(None, 0)
                errread, errwrite = Handle(errread), Handle(errwrite)
            elif stderr == STDOUT:
                errwrite = c2pwrite
            elif stderr == DEVNULL:
                errwrite = msvcrt.get_osfhandle(self._get_devnull())
            elif isinstance(stderr, int):
                errwrite = msvcrt.get_osfhandle(stderr)
            else:
                # Assuming file-like object
                errwrite = msvcrt.get_osfhandle(stderr.fileno())
            errwrite = self._make_inheritable(errwrite)

            return (p2cread, p2cwrite,
                    c2pread, c2pwrite,
                    errread, errwrite)

    else:
        # POSIX versions
        def _get_handles(self, stdin, stdout, stderr):
            """Construct and return tuple with IO objects:
            p2cread, p2cwrite, c2pread, c2pwrite, errread, errwrite
            """
            p2cread, p2cwrite = -1, -1
            c2pread, c2pwrite = -1, -1
            errread, errwrite = -1, -1

            if stdin is None:
                pass
            elif stdin == PIPE:
                p2cread, p2cwrite = os.pipe()
            elif stdin == DEVNULL:
                p2cread = self._get_devnull()
            elif isinstance(stdin, int):
                p2cread = stdin
            else:
                # Assuming file-like object
                p2cread = stdin.fileno()

            if stdout is None:
                pass
            elif stdout == PIPE:
                c2pread, c2pwrite = os.pipe()
            elif stdout == DEVNULL:
                c2pwrite = self._get_devnull()
            elif isinstance(stdout, int):
                c2pwrite = stdout
            else:
                # Assuming file-like object
                c2pwrite = stdout.fileno()

            if stderr is None:
                pass
            elif stderr == PIPE:
                errread, errwrite = os.pipe()
            elif stderr == STDOUT:
                errwrite = c2pwrite
            elif stderr == DEVNULL:
                errwrite = self._get_devnull()
            elif isinstance(stderr, int):
                errwrite = stderr
            else:
                # Assuming file-like object
                errwrite = stderr.fileno()

            return (p2cread, p2cwrite,
                    c2pread, c2pwrite,
                    errread, errwrite)


def wrap_simple_command(f, args, stdin, stdout, stderr):
    """Decorator for creating 'simple' callable aliases."""
    bgable = getattr(f, '__xonsh_backgroundable__', True)
    @wraps(f)
    def wrapped_simple_command(args, stdin, stdout, stderr):
        try:
            i = stdin.read()
            if bgable:
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    r = f(args, i)
            else:
                r = f(args, i)

            cmd_result = 0
            if isinstance(r, str):
                stdout.write(r)
            elif isinstance(r, Sequence):
                if r[0] is not None:
                    stdout.write(r[0])
                if r[1] is not None:
                    stderr.write(r[1])
                if len(r) > 2 and r[2] is not None:
                    cmd_result = r[2]
            elif r is not None:
                stdout.write(str(r))
            return cmd_result
        except Exception:
            print_exception()
            return 1  # returncode for failure
    return wrapped_simple_command


class SimpleProcProxy(ProcProxy):
    """Variant of `ProcProxy` for simpler functions.

    The function passed into the initializer for `SimpleProcProxy` should have
    the form described in the xonsh tutorial.  This function is then wrapped to
    make a new function of the form expected by `ProcProxy`.
    """

    def __init__(self, f, args, stdin=None, stdout=None, stderr=None,
                 universal_newlines=False):
        f = wrap_simple_command(f, args, stdin, stdout, stderr)
        super().__init__(f, args, stdin, stdout, stderr, universal_newlines)

#
# Foreground Process Proxies
#

class ForegroundProcProxy(object):
    """This is process proxy class that runs its alias functions on the
    same thread that it was called from, which is typically the main thread.
    This prevents backgrounding the process, but enables debugger and
    profiler tools (functions) be run on the same thread that they are
    attempting to debug.
    """

    def __init__(self, f, args, stdin=None, stdout=None, stderr=None,
                 universal_newlines=False):
        self.f = f
        self.args = args
        self.pid = os.getpid()
        self.returncode = None
        self.stdin = stdin
        self.stdout = None
        self.stderr = None
        self.universal_newlines = universal_newlines

    def poll(self):
        """Check if the function has completed via the returncode or None.
        """
        return self.returncode

    def wait(self, timeout=None):
        """Runs the function and returns the result. Timeout argument only
        present for API compatability.
        """
        if self.f is None:
            return
        if self.stdin is None:
            stdin = io.StringIO("")
        else:
            stdin = io.TextIOWrapper(self.stdin)
        r = self.f(self.args, stdin, self.stdout, self.stderr)
        self.returncode = 0 if r is None else r
        return self.returncode


class SimpleForegroundProcProxy(ForegroundProcProxy):
    """Variant of `ForegroundProcProxy` for simpler functions.

    The function passed into the initializer for `SimpleForegroundProcProxy`
    should have the form described in the xonsh tutorial. This function is
    then wrapped to make a new function of the form expected by
    `ForegroundProcProxy`.
    """

    def __init__(self, f, args, stdin=None, stdout=None, stderr=None,
                 universal_newlines=False):
        f = wrap_simple_command(f, args, stdin, stdout, stderr)
        super().__init__(f, args, stdin, stdout, stderr, universal_newlines)


def foreground(f):
    """Decorator that specifies that a callable alias should be run only
    as a foreground process. This is often needed for debuggers and profilers.
    """
    f.__xonsh_backgroundable__ = False
    return f

#
# Pseudo-terminal Proxies
#


@fallback(ON_LINUX, Popen)
class TeePTYProc(object):

    def __init__(self, args, stdin=None, stdout=None, stderr=None, preexec_fn=None,
                 env=None, universal_newlines=False):
        """Popen replacement for running commands in teed psuedo-terminal. This
        allows the capturing AND streaming of stdout and stderr.  Availability
        is Linux-only.
        """
        self.stdin = stdin
        self._stdout = stdout
        self._stderr = stderr
        self.args = args
        self.universal_newlines = universal_newlines
        xenv = builtins.__xonsh_env__ if hasattr(builtins, '__xonsh_env__') \
                                      else {'XONSH_ENCODING': 'utf-8',
                                            'XONSH_ENCODING_ERRORS': 'strict'}

        if not os.access(args[0], os.F_OK):
            raise FileNotFoundError('command {0!r} not found'.format(args[0]))
        elif not os.access(args[0], os.X_OK) or os.path.isdir(args[0]):
            raise PermissionError('permission denied: {0!r}'.format(args[0]))
        self._tpty = tpty = TeePTY(encoding=xenv.get('XONSH_ENCODING'),
                                   errors=xenv.get('XONSH_ENCODING_ERRORS'))
        if preexec_fn is not None:
            preexec_fn()
        delay = xenv.get('TEEPTY_PIPE_DELAY')
        tpty.spawn(args, env=env, stdin=stdin, delay=delay)

    @property
    def pid(self):
        """The pid of the spawned process."""
        return self._tpty.pid

    @property
    def returncode(self):
        """The return value of the spawned process or None if the process
        exited due to a signal."""
        if os.WIFEXITED(self._tpty.wcode):
            return os.WEXITSTATUS(self._tpty.wcode)
        else:
            return None

    @property
    def signal(self):
        """If the process was terminated by a signal a 2-tuple is returned
        containing the signal number and a boolean indicating whether a core
        file was produced. Otherwise None is returned."""
        if os.WIFSIGNALED(self._tpty.wcode):
            return (os.WTERMSIG(self._tpty.wcode),
                    os.WCOREDUMP(self._tpty.wcode))
        else:
            return None

    def poll(self):
        """Polls the spawned process and returns the os.wait code."""
        return _wcode_to_popen(self._tpty.wcode)

    def wait(self, timeout=None):
        """Waits for the spawned process to finish, up to a timeout.
        Returns the return os.wait code."""
        tpty = self._tpty
        t0 = time.time()
        while tpty.wcode is None:
            if timeout is not None and timeout < (time.time() - t0):
                raise TimeoutExpired
        return _wcode_to_popen(tpty.wcode)

    @property
    def stdout(self):
        """The stdout (and stderr) that was tee'd into a buffer by the psuedo-terminal.
        """
        if self._stdout is not None:
            pass
        elif self.universal_newlines:
            self._stdout = io.StringIO(str(self._tpty))
            self._stdout.seek(0)
        else:
            self._stdout = self._tpty.buffer
        return self._stdout


def _wcode_to_popen(code):
    """Converts os.wait return code into Popen format."""
    if os.WIFEXITED(code):
        return os.WEXITSTATUS(code)
    elif os.WIFSIGNALED(code):
        return -1 * os.WTERMSIG(code)
    else:
        # Can this happen? Let's find out. Returning None is not an option.
        raise ValueError("Invalid os.wait code: {}".format(code))


_CCTuple = namedtuple("_CCTuple", ["stdin",
                                   "stdout",
                                   "stderr",
                                   "pid",
                                   "returncode",
                                   "args",
                                   "alias",
                                   "stdin_redirect",
                                   "stdout_redirect",
                                   "stderr_redirect",
                                   "timestamp",
                                   "executed_cmd"])


class CompletedCommand(_CCTuple):
    """Represents a completed subprocess-mode command."""

    def __bool__(self):
        return self.returncode == 0

    def __iter__(self):
        if not self.stdout:
            raise StopIteration()

        pre = self.stdout
        post = None

        while post != '':
            pre, sep, post = pre.partition('\n')
            # this line may be optional since we use universal newlines.
            pre = pre[:-1] if pre and pre[-1] == '\r' else pre
            yield pre
            pre = post


    def itercheck(self):
        yield from self
        if self.returncode:
            # I included self, as providing access to stderr and other details
            # useful when instance isn't assigned to a variable in the shell.
            raise XonshCalledProcessError(self.returncode, self.executed_cmd,
                                          self.stdout, self.stderr, self)

    @property
    def inp(self):
        """Creates normalized input string from args."""
        return ' '.join(self.args)

    @property
    def out(self):
        """Alias to stdout."""
        return self.stdout

    @property
    def err(self):
        """Alias to stderr."""
        return self.stderr

    @property
    def rtn(self):
        """Alias to return code."""
        return self.returncode

CompletedCommand.__new__.__defaults__ = (None,) * len(CompletedCommand._fields)


class HiddenCompletedCommand(CompletedCommand):
    def __repr__(self):
        return ''

#
# xontribs
#
"""Tools for helping manage xontributions."""
# amalgamated os
# amalgamated sys
# amalgamated json
# amalgamated builtins
# amalgamated functools
from warnings import catch_warnings, simplefilter
from argparse import ArgumentParser
from importlib import import_module
from importlib.util import find_spec

# amalgamated xonsh.tools
@functools.lru_cache(1)
def xontribs_json():
    return os.path.join(os.path.dirname(__file__), 'xontribs.json')

def find_xontrib(name):
    """Finds a xontribution from its name."""
    if name.startswith('.'):
        spec = find_spec(name, package='xontrib')
    else:
        spec = find_spec('.' + name, package='xontrib')
    return spec or find_spec(name)


def xontrib_context(name):
    """Return a context dictionary for a xontrib of a given name."""
    spec = find_xontrib(name)
    if spec is None:
        with catch_warnings():
            simplefilter('default', ImportWarning)
            warn('could not find xontrib module {0!r}'.format(name), ImportWarning)
        return {}
    m = import_module(spec.name)
    ctx = {k: getattr(m, k) for k in dir(m) if not k.startswith('_')}
    return ctx


def update_context(name, ctx=None):
    """Updates a context in place from a xontrib. If ctx is not provided,
    then __xonsh_ctx__ is updated.
    """
    if ctx is None:
        ctx = builtins.__xonsh_ctx__
    modctx = xontrib_context(name)
    return ctx.update(modctx)


@functools.lru_cache()
def xontrib_metadata():
    """Loads and returns the xontribs.json file."""
    with open(xontribs_json(), 'r') as f:
        md = json.load(f)
    return md


def _load(ns):
    """load xontribs"""
    ctx = builtins.__xonsh_ctx__
    for name in ns.names:
        if ns.verbose:
            print('loading xontrib {0!r}'.format(name))
        update_context(name, ctx=ctx)


def _list(ns):
    """Lists xontribs."""
    meta = xontrib_metadata()
    data = []
    nname = 6  # ensures some buffer space.
    names = None if len(ns.names) == 0 else set(ns.names)
    for md in meta['xontribs']:
        name = md['name']
        if names is not None and md['name'] not in names:
            continue
        nname = max(nname, len(name))
        spec = find_xontrib(name)
        if spec is None:
            installed = loaded = False
        else:
            installed = True
            loaded = spec.name in sys.modules
        d = {'name': name, 'installed': installed, 'loaded': loaded}
        data.append(d)
    if ns.json:
        jdata = {d.pop('name'): d for d in data}
        s = json.dumps(jdata)
        print(s)
    else:
        s = ""
        for d in data:
            name = d['name']
            lname = len(name)
            s += "{PURPLE}" + name + "{NO_COLOR}  " + " "*(nname - lname)
            if d['installed']:
                s += '{GREEN}installed{NO_COLOR}      '
            else:
                s += '{RED}not-installed{NO_COLOR}  '
            if d['loaded']:
                s += '{GREEN}loaded{NO_COLOR}'
            else:
                s += '{RED}not-loaded{NO_COLOR}'
            s += '\n'
        print_color(s[:-1])


@functools.lru_cache()
def _create_parser():
    # parse command line args
    parser = ArgumentParser(prog='xontrib',
                            description='Manages xonsh extensions')
    subp = parser.add_subparsers(title='action', dest='action')
    load = subp.add_parser('load', help='loads xontribs')
    load.add_argument('-v', '--verbose', action='store_true', default=False,
                        dest='verbose')
    load.add_argument('names', nargs='+', default=(),
                      help='names of xontribs')
    lyst = subp.add_parser('list', help=('list xontribs, whether they are '
                                         'installed, and loaded.'))
    lyst.add_argument('--json', action='store_true', default=False,
                      help='reports results as json')
    lyst.add_argument('names', nargs='*', default=(),
                      help='names of xontribs')
    return parser


_MAIN_ACTIONS = {
    'load': _load,
    'list': _list,
    }

def xontribs_main(args=None, stdin=None):
    """Alias that loads xontribs"""
    if not args or (args[0] not in _MAIN_ACTIONS and
                    args[0] not in {'-h', '--help'}):
        args.insert(0, 'load')
    parser = _create_parser()
    ns = parser.parse_args(args)
    if ns.action is None:  # apply default action
        ns = parser.parse_args(['load'] + args)
    return _MAIN_ACTIONS[ns.action](ns)


if __name__ == '__main__':
    main()
#
# commands_cache
#
# -*- coding: utf-8 -*-
# amalgamated builtins
# amalgamated os
# amalgamated collections.abc
# amalgamated xonsh.dirstack
# amalgamated xonsh.platform
# amalgamated xonsh.tools
class CommandsCache(abc.Mapping):
    """A lazy cache representing the commands available on the file system.
    The keys are the command names and the values a tuple of (loc, has_alias)
    where loc is either a str pointing to the executable on the file system or
    None (if no executable exists) and has_alias is a boolean flag for whether
    the command has an alias.
    """

    def __init__(self):
        self._cmds_cache = {}
        self._path_checksum = None
        self._alias_checksum = None
        self._path_mtime = -1

    def __contains__(self, key):
        return key in self.all_commands

    def __iter__(self):
        return iter(self.all_commands)

    def __len__(self):
        return len(self.all_commands)

    def __getitem__(self, key):
        return self.all_commands[key]

    def is_empty(self):
        """Returns whether the cache is populated or not."""
        return len(self._cmds_cache) == 0

    @staticmethod
    def get_possible_names(name):
        """Generates the possible `PATHEXT` extension variants of a given executable
         name on Windows as a list, conserving the ordering in `PATHEXT`.
         Returns a list as `name` being the only item in it on other platforms."""
        if ON_WINDOWS:
            name = name.upper()
            return [
                name + ext
                for ext in ([''] + builtins.__xonsh_env__['PATHEXT'])
            ]
        else:
            return [name]

    @property
    def all_commands(self):
        paths = builtins.__xonsh_env__.get('PATH', [])
        pathset = frozenset(x for x in paths if os.path.isdir(x))
        # did PATH change?
        path_hash = hash(pathset)
        cache_valid = path_hash == self._path_checksum
        self._path_checksum = path_hash
        # did aliases change?
        alss = getattr(builtins, 'aliases', set())
        al_hash = hash(frozenset(alss))
        cache_valid = cache_valid and al_hash == self._alias_checksum
        self._alias_checksum = al_hash
        # did the contents of any directory in PATH change?
        max_mtime = 0
        for path in pathset:
            mtime = os.stat(path).st_mtime
            if mtime > max_mtime:
                max_mtime = mtime
        cache_valid = cache_valid and (max_mtime <= self._path_mtime)
        self._path_mtime = max_mtime
        if cache_valid:
            return self._cmds_cache
        allcmds = {}
        for path in reversed(paths):
            # iterate backwards so that entries at the front of PATH overwrite
            # entries at the back.
            for cmd in executables_in(path):
                key = cmd.upper() if ON_WINDOWS else cmd
                allcmds[key] = (os.path.join(path, cmd), cmd in alss)
        only_alias = (None, True)
        for cmd in alss:
            if cmd not in allcmds:
                allcmds[cmd] = only_alias
        self._cmds_cache = allcmds
        return allcmds

    def lazyin(self, key):
        """Checks if the value is in the current cache without the potential to
        update the cache. It just says whether the value is known *now*. This
        may not reflect precisely what is on the $PATH.
        """
        return key in self._cmds_cache

    def lazyiter(self):
        """Returns an iterator over the current cache contents without the
        potential to update the cache. This may not reflect what is on the
        $PATH.
        """
        return iter(self._cmds_cache)

    def lazylen(self):
        """Returns the length of the current cache contents without the
        potential to update the cache. This may not reflect precisely
        what is on the $PATH.
        """
        return len(self._cmds_cache)

    def lazyget(self, key, default=None):
        """A lazy value getter."""
        return self._cmds_cache.get(key, default)

    def locate_binary(self, name):
        """Locates an executable on the file system using the cache."""
        # make sure the cache is up to date by accessing the property
        _ = self.all_commands
        return self.lazy_locate_binary(name)

    def lazy_locate_binary(self, name):
        """Locates an executable in the cache, without checking its validity."""
        possibilities = self.get_possible_names(name)

        if ON_WINDOWS:
            # Windows users expect to be able to execute files in the same
            # directory without `./`
            cwd = _get_cwd()
            local_bin = next((
                full_name for full_name in possibilities
                if os.path.isfile(full_name)
            ), None)
            if local_bin:
                return os.path.abspath(os.path.relpath(local_bin, cwd))

        cached = next((cmd for cmd in possibilities if cmd in self._cmds_cache), None)
        if cached:
            return self._cmds_cache[cached][0]
        elif os.path.isfile(name) and name != os.path.basename(name):
            return name

#
# environ
#
# -*- coding: utf-8 -*-
"""Environment for the xonsh shell."""
# amalgamated os
# amalgamated sys
# amalgamated time
# amalgamated json
locale = _LazyModule.load('locale', 'locale')
# amalgamated builtins
# amalgamated from contextlib import contextmanager
# amalgamated from itertools import chain
from pprint import pformat
# amalgamated re
socket = _LazyModule.load('socket', 'socket')
# amalgamated string
# amalgamated subprocess
# amalgamated shutil
# amalgamated from warnings import warn
from collections import MutableSequence, MutableSet
from xonsh import __version__ as XONSH_VERSION
# amalgamated xonsh.jobs
# amalgamated xonsh.codecache
# amalgamated xonsh.dirstack
# amalgamated xonsh.foreign_shells
# amalgamated xonsh.platform
# amalgamated xonsh.tools
LOCALE_CATS = {
    'LC_CTYPE': locale.LC_CTYPE,
    'LC_COLLATE': locale.LC_COLLATE,
    'LC_NUMERIC': locale.LC_NUMERIC,
    'LC_MONETARY': locale.LC_MONETARY,
    'LC_TIME': locale.LC_TIME,
}
if hasattr(locale, 'LC_MESSAGES'):
    LOCALE_CATS['LC_MESSAGES'] = locale.LC_MESSAGES


def locale_convert(key):
    """Creates a converter for a locale key."""
    def lc_converter(val):
        try:
            locale.setlocale(LOCALE_CATS[key], val)
            val = locale.setlocale(LOCALE_CATS[key])
        except (locale.Error, KeyError):
            warn('Failed to set locale {0!r} to {1!r}'.format(key, val),
                 RuntimeWarning)
        return val
    return lc_converter


def to_debug(x):
    """Converts value using to_bool_or_int() and sets this value on as the
    execer's debug level.
    """
    val = to_bool_or_int(x)
    if hasattr(builtins, '__xonsh_execer__'):
        builtins.__xonsh_execer__.debug_level = val
    return val

Ensurer = namedtuple('Ensurer', ['validate', 'convert', 'detype'])
Ensurer.__doc__ = """Named tuples whose elements are functions that
represent environment variable validation, conversion, detyping.
"""

DEFAULT_ENSURERS = {
    'AUTO_CD': (is_bool, to_bool, bool_to_str),
    'AUTO_PUSHD': (is_bool, to_bool, bool_to_str),
    'AUTO_SUGGEST': (is_bool, to_bool, bool_to_str),
    'BASH_COMPLETIONS': (is_env_path, str_to_env_path, env_path_to_str),
    'CASE_SENSITIVE_COMPLETIONS': (is_bool, to_bool, bool_to_str),
    re.compile('\w*DIRS$'): (is_env_path, str_to_env_path, env_path_to_str),
    'COLOR_INPUT': (is_bool, to_bool, bool_to_str),
    'COLOR_RESULTS': (is_bool, to_bool, bool_to_str),
    'COMPLETIONS_DISPLAY': (is_completions_display_value,
                            to_completions_display_value, str),
    'COMPLETIONS_MENU_ROWS': (is_int, int, str),
    'DYNAMIC_CWD_WIDTH': (is_dynamic_cwd_width, to_dynamic_cwd_tuple,
                          dynamic_cwd_tuple_to_str),
    'FORCE_POSIX_PATHS': (is_bool, to_bool, bool_to_str),
    'FUZZY_PATH_COMPLETION': (is_bool, to_bool, bool_to_str),
    'GLOB_SORTED': (is_bool, to_bool, bool_to_str),
    'HISTCONTROL': (is_string_set, csv_to_set, set_to_csv),
    'IGNOREEOF': (is_bool, to_bool, bool_to_str),
    'INTENSIFY_COLORS_ON_WIN':(always_false, intensify_colors_on_win_setter,
                               bool_to_str),
    'LC_COLLATE': (always_false, locale_convert('LC_COLLATE'), ensure_string),
    'LC_CTYPE': (always_false, locale_convert('LC_CTYPE'), ensure_string),
    'LC_MESSAGES': (always_false, locale_convert('LC_MESSAGES'), ensure_string),
    'LC_MONETARY': (always_false, locale_convert('LC_MONETARY'), ensure_string),
    'LC_NUMERIC': (always_false, locale_convert('LC_NUMERIC'), ensure_string),
    'LC_TIME': (always_false, locale_convert('LC_TIME'), ensure_string),
    'LOADED_CONFIG': (is_bool, to_bool, bool_to_str),
    'LOADED_RC_FILES': (is_bool_seq, csv_to_bool_seq, bool_seq_to_csv),
    'MOUSE_SUPPORT': (is_bool, to_bool, bool_to_str),
    'MULTILINE_PROMPT': (is_string_or_callable, ensure_string, ensure_string),
    re.compile('\w*PATH$'): (is_env_path, str_to_env_path, env_path_to_str),
    'PATHEXT': (is_nonstring_seq_of_strings, pathsep_to_upper_seq,
                seq_to_upper_pathsep),
    'PRETTY_PRINT_RESULTS': (is_bool, to_bool, bool_to_str),
    'PROMPT': (is_string_or_callable, ensure_string, ensure_string),
    'RAISE_SUBPROC_ERROR': (is_bool, to_bool, bool_to_str),
    'RIGHT_PROMPT': (is_string_or_callable, ensure_string, ensure_string),
    'SUBSEQUENCE_PATH_COMPLETION': (is_bool, to_bool, bool_to_str),
    'SUPPRESS_BRANCH_TIMEOUT_MESSAGE': (is_bool, to_bool, bool_to_str),
    'TEEPTY_PIPE_DELAY': (is_float, float, str),
    'UPDATE_OS_ENVIRON': (is_bool, to_bool, bool_to_str),
    'VC_BRANCH_TIMEOUT': (is_float, float, str),
    'VI_MODE': (is_bool, to_bool, bool_to_str),
    'VIRTUAL_ENV': (is_string, ensure_string, ensure_string),
    'WIN_UNICODE_CONSOLE': (always_false, setup_win_unicode_console, bool_to_str),
    'XONSHRC': (is_env_path, str_to_env_path, env_path_to_str),
    'XONSH_CACHE_SCRIPTS': (is_bool, to_bool, bool_to_str),
    'XONSH_CACHE_EVERYTHING': (is_bool, to_bool, bool_to_str),
    'XONSH_COLOR_STYLE': (is_string, ensure_string, ensure_string),
    'XONSH_DEBUG': (always_false, to_debug, bool_or_int_to_str),
    'XONSH_ENCODING': (is_string, ensure_string, ensure_string),
    'XONSH_ENCODING_ERRORS': (is_string, ensure_string, ensure_string),
    'XONSH_HISTORY_SIZE': (is_history_tuple, to_history_tuple, history_tuple_to_str),
    'XONSH_LOGIN': (is_bool, to_bool, bool_to_str),
    'XONSH_SHOW_TRACEBACK': (is_bool, to_bool, bool_to_str),
    'XONSH_STORE_STDOUT': (is_bool, to_bool, bool_to_str),
    'XONSH_STORE_STDIN': (is_bool, to_bool, bool_to_str),
    'XONSH_TRACEBACK_LOGFILE': (is_logfile_opt, to_logfile_opt,
                                logfile_opt_to_str)
}

#
# Defaults
#
def default_value(f):
    """Decorator for making callable default values."""
    f._xonsh_callable_default = True
    return f

def is_callable_default(x):
    """Checks if a value is a callable default."""
    return callable(x) and getattr(x, '_xonsh_callable_default', False)

if ON_CYGWIN:
    DEFAULT_PROMPT = ('{env_name}{BOLD_GREEN}{user}@{hostname}'
                      '{BOLD_BLUE} {cwd} {prompt_end}{NO_COLOR} ')
elif ON_WINDOWS:
    DEFAULT_PROMPT = ('{env_name}'
                      '{BOLD_INTENSE_GREEN}{user}@{hostname}{BOLD_INTENSE_CYAN} '
                      '{cwd}{branch_color}{curr_branch}{NO_COLOR} '
                      '{BOLD_INTENSE_CYAN}{prompt_end}{NO_COLOR} ')
else:
    DEFAULT_PROMPT = ('{env_name}'
                      '{BOLD_GREEN}{user}@{hostname}{BOLD_BLUE} '
                      '{cwd}{branch_color}{curr_branch}{NO_COLOR} '
                      '{BOLD_BLUE}{prompt_end}{NO_COLOR} ')

DEFAULT_TITLE = '{current_job}{user}@{hostname}: {cwd} | xonsh'

@default_value
def xonsh_data_dir(env):
    """Ensures and returns the $XONSH_DATA_DIR"""
    xdd = os.path.join(env.get('XDG_DATA_HOME'), 'xonsh')
    os.makedirs(xdd, exist_ok=True)
    return xdd


@default_value
def xonsh_config_dir(env):
    """Ensures and returns the $XONSH_CONFIG_DIR"""
    xcd = os.path.join(env.get('XDG_CONFIG_HOME'), 'xonsh')
    os.makedirs(xcd, exist_ok=True)
    return xcd


@default_value
def xonshconfig(env):
    """Ensures and returns the $XONSHCONFIG"""
    xcd = env.get('XONSH_CONFIG_DIR')
    xc = os.path.join(xcd, 'config.json')
    return xc

if ON_WINDOWS:
    DEFAULT_XONSHRC = (os.path.join(os.environ['ALLUSERSPROFILE'],
                                     'xonsh', 'xonshrc'),
                       os.path.expanduser('~/.xonshrc'))
else:
    DEFAULT_XONSHRC = ('/etc/xonshrc', os.path.expanduser('~/.xonshrc'))

# Default values should generally be immutable, that way if a user wants
# to set them they have to do a copy and write them to the environment.
# try to keep this sorted.
DEFAULT_VALUES = {
    'AUTO_CD': False,
    'AUTO_PUSHD': False,
    'AUTO_SUGGEST': True,
    'BASH_COMPLETIONS': BASH_COMPLETIONS_DEFAULT,
    'CASE_SENSITIVE_COMPLETIONS': ON_LINUX,
    'CDPATH': (),
    'COLOR_INPUT': True,
    'COLOR_RESULTS': True,
    'COMPLETIONS_DISPLAY': 'multi',
    'COMPLETIONS_MENU_ROWS': 5,
    'DIRSTACK_SIZE': 20,
    'DYNAMIC_CWD_WIDTH': (float('inf'), 'c'),
    'EXPAND_ENV_VARS': True,
    'FORCE_POSIX_PATHS': False,
    'FUZZY_PATH_COMPLETION': True,
    'GLOB_SORTED': True,
    'HISTCONTROL': set(),
    'IGNOREEOF': False,
    'INDENT': '    ',
    'INTENSIFY_COLORS_ON_WIN': True,
    'LC_CTYPE': locale.setlocale(locale.LC_CTYPE),
    'LC_COLLATE': locale.setlocale(locale.LC_COLLATE),
    'LC_TIME': locale.setlocale(locale.LC_TIME),
    'LC_MONETARY': locale.setlocale(locale.LC_MONETARY),
    'LC_NUMERIC': locale.setlocale(locale.LC_NUMERIC),
    'LOADED_CONFIG': False,
    'LOADED_RC_FILES': (),
    'MOUSE_SUPPORT': False,
    'MULTILINE_PROMPT': '.',
    'PATH': PATH_DEFAULT,
    'PATHEXT': ['.COM', '.EXE', '.BAT', '.CMD'] if ON_WINDOWS else [],
    'PRETTY_PRINT_RESULTS': True,
    'PROMPT': DEFAULT_PROMPT,
    'PUSHD_MINUS': False,
    'PUSHD_SILENT': False,
    'RAISE_SUBPROC_ERROR': False,
    'RIGHT_PROMPT': '',
    'SHELL_TYPE': 'best',
    'SUBSEQUENCE_PATH_COMPLETION': True,
    'SUPPRESS_BRANCH_TIMEOUT_MESSAGE': False,
    'SUGGEST_COMMANDS': True,
    'SUGGEST_MAX_NUM': 5,
    'SUGGEST_THRESHOLD': 3,
    'TEEPTY_PIPE_DELAY': 0.01,
    'TITLE': DEFAULT_TITLE,
    'UPDATE_OS_ENVIRON': False,
    'VC_BRANCH_TIMEOUT': 0.2 if ON_WINDOWS else 0.1,
    'VI_MODE': False,
    'WIN_UNICODE_CONSOLE': True,
    'XDG_CONFIG_HOME': os.path.expanduser(os.path.join('~', '.config')),
    'XDG_DATA_HOME': os.path.expanduser(os.path.join('~', '.local', 'share')),
    'XONSHCONFIG': xonshconfig,
    'XONSHRC': DEFAULT_XONSHRC,
    'XONSH_CACHE_SCRIPTS': True,
    'XONSH_CACHE_EVERYTHING': False,
    'XONSH_COLOR_STYLE': 'default',
    'XONSH_CONFIG_DIR': xonsh_config_dir,
    'XONSH_DATA_DIR': xonsh_data_dir,
    'XONSH_DEBUG': False,
    'XONSH_ENCODING': DEFAULT_ENCODING,
    'XONSH_ENCODING_ERRORS': 'surrogateescape',
    'XONSH_HISTORY_FILE': os.path.expanduser('~/.xonsh_history.json'),
    'XONSH_HISTORY_SIZE': (8128, 'commands'),
    'XONSH_LOGIN': False,
    'XONSH_SHOW_TRACEBACK': False,
    'XONSH_STORE_STDIN': False,
    'XONSH_STORE_STDOUT': False,
    'XONSH_TRACEBACK_LOGFILE': None
}
if hasattr(locale, 'LC_MESSAGES'):
    DEFAULT_VALUES['LC_MESSAGES'] = locale.setlocale(locale.LC_MESSAGES)

VarDocs = namedtuple('VarDocs', ['docstr', 'configurable', 'default',
                                 'store_as_str'])
VarDocs.__doc__ = """Named tuple for environment variable documentation

Parameters
----------
docstr : str
   The environment variable docstring.
configurable : bool, optional
    Flag for whether the environment variable is configurable or not.
default : str, optional
    Custom docstring for the default value for complex defaults.
    Is this is DefaultNotGiven, then the default will be looked up
    from DEFAULT_VALUES and converted to a str.
store_as_str : bool, optional
    Flag for whether the environment variable should be stored as a
    string. This is used when persisting a variable that is not JSON
    serializable to the config file. For example, sets, frozensets, and
    potentially other non-trivial data types. default, False.
"""
# iterates from back
VarDocs.__new__.__defaults__ = (True, DefaultNotGiven, False)

# Please keep the following in alphabetic order - scopatz
DEFAULT_DOCS = {
    'ANSICON': VarDocs('This is used on Windows to set the title, '
                       'if available.', configurable=False),
    'AUTO_CD': VarDocs(
        'Flag to enable changing to a directory by entering the dirname or '
        'full path only (without the cd command).'),
    'AUTO_PUSHD': VarDocs(
        'Flag for automatically pushing directories onto the directory stack.'
        ),
    'AUTO_SUGGEST': VarDocs(
        'Enable automatic command suggestions based on history, like in the fish '
        'shell.\n\nPressing the right arrow key inserts the currently '
        'displayed suggestion. Only usable with $SHELL_TYPE=prompt_toolkit.'),
    'BASH_COMPLETIONS': VarDocs(
        'This is a list (or tuple) of strings that specifies where the BASH '
        'completion files may be found. The default values are platform '
        'dependent, but sane. To specify an alternate list, do so in the run '
        'control file.', default=(
        "Normally this is:\n\n"
        "    ('/etc/bash_completion',\n"
        "     '/usr/share/bash-completion/completions/git')\n\n"
        "But, on Mac it is:\n\n"
        "    ('/usr/local/etc/bash_completion',\n"
        "     '/opt/local/etc/profile.d/bash_completion.sh')\n\n"
        "And on Arch Linux it is:\n\n"
        "    ('/usr/share/bash-completion/bash_completion',\n"
        "     '/usr/share/bash-completion/completions/git')\n\n"
        "Other OS-specific defaults may be added in the future.")),
    'CASE_SENSITIVE_COMPLETIONS': VarDocs(
        'Sets whether completions should be case sensitive or case '
        'insensitive.', default='True on Linux, False otherwise.'),
    'CDPATH': VarDocs(
        'A list of paths to be used as roots for a cd, breaking compatibility '
        'with Bash, xonsh always prefer an existing relative path.'),
    'COLOR_INPUT': VarDocs('Flag for syntax highlighting interactive input.'),
    'COLOR_RESULTS': VarDocs('Flag for syntax highlighting return values.'),
    'COMPLETIONS_DISPLAY': VarDocs(
        'Configure if and how Python completions are displayed by the '
        'prompt_toolkit shell.\n\nThis option does not affect Bash '
        'completions, auto-suggestions, etc.\n\nChanging it at runtime will '
        'take immediate effect, so you can quickly disable and enable '
        'completions during shell sessions.\n\n'
        "- If $COMPLETIONS_DISPLAY is 'none' or 'false', do not display\n"
        "  those completions.\n"
        "- If $COMPLETIONS_DISPLAY is 'single', display completions in a\n"
        '  single column while typing.\n'
        "- If $COMPLETIONS_DISPLAY is 'multi' or 'true', display completions\n"
        "  in multiple columns while typing.\n\n"
        'These option values are not case- or type-sensitive, so e.g.'
        "writing \"$COMPLETIONS_DISPLAY = None\" and \"$COMPLETIONS_DISPLAY "
        "= 'none'\" are equivalent. Only usable with "
        "$SHELL_TYPE=prompt_toolkit"),
    'COMPLETIONS_MENU_ROWS': VarDocs(
        'Number of rows to reserve for tab-completions menu if '
        "$COMPLETIONS_DISPLAY is 'single' or 'multi'. This only affects the "
        'prompt-toolkit shell.'),
    'DIRSTACK_SIZE': VarDocs('Maximum size of the directory stack.'),
    'DYNAMIC_CWD_WIDTH': VarDocs('Maximum length in number of characters '
        'or as a percentage for the `cwd` prompt variable. For example, '
        '"20" is a twenty character width and "10%" is ten percent of the '
        'number of columns available.'),
    'EXPAND_ENV_VARS': VarDocs(
        'Toggles whether environment variables are expanded inside of strings '
        'in subprocess mode.'),
    'FORCE_POSIX_PATHS': VarDocs(
        "Forces forward slashes ('/') on Windows systems when using auto "
        'completion if set to anything truthy.', configurable=ON_WINDOWS),
    'FORMATTER_DICT': VarDocs(
        'Dictionary containing variables to be used when formatting $PROMPT '
        "and $TITLE. See 'Customizing the Prompt' "
        'http://xon.sh/tutorial.html#customizing-the-prompt',
        configurable=False, default='xonsh.environ.FORMATTER_DICT'),
    'FUZZY_PATH_COMPLETION': VarDocs(
        "Toggles 'fuzzy' matching of paths for tab completion, which is only "
        "used as a fallback if no other completions succeed but can be used "
        "as a way to adjust for typographical errors. If ``True``, then, e.g.,"
        " ``xonhs`` will match ``xonsh``."),
    'GLOB_SORTED': VarDocs(
        "Toggles whether globbing results are manually sorted. If ``False``, "
        "the results are returned in arbitrary order."),
    'HISTCONTROL': VarDocs(
        'A set of strings (comma-separated list in string form) of options '
        'that determine what commands are saved to the history list. By '
        "default all commands are saved. The option 'ignoredups' will not "
        "save the command if it matches the previous command. The option "
        "'ignoreerr' will cause any commands that fail (i.e. return non-zero "
        "exit status) to not be added to the history list.",
        store_as_str=True),
    'IGNOREEOF': VarDocs('Prevents Ctrl-D from exiting the shell.'),
    'INDENT': VarDocs('Indentation string for multiline input'),
    'INTENSIFY_COLORS_ON_WIN': VarDocs('Enhance style colors for readability '
        'when using the default terminal (cmd.exe) on Windows. Blue colors, '
        'which are hard to read, are replaced with cyan. Other colors are '
        'generally replaced by their bright counter parts.',
        configurable=ON_WINDOWS),
    'LOADED_CONFIG': VarDocs('Whether or not the xonsh config file was loaded',
        configurable=False),
    'LOADED_RC_FILES': VarDocs(
        'Whether or not any of the xonsh run control files were loaded at '
        'startup. This is a sequence of bools in Python that is converted '
        "to a CSV list in string form, ie [True, False] becomes 'True,False'.",
        configurable=False),
    'MOUSE_SUPPORT': VarDocs(
        'Enable mouse support in the prompt_toolkit shell. This allows '
        'clicking for positioning the cursor or selecting a completion. In '
        'some terminals however, this disables the ability to scroll back '
        'through the history of the terminal. Only usable with '
        '$SHELL_TYPE=prompt_toolkit'),
    'MULTILINE_PROMPT': VarDocs(
        'Prompt text for 2nd+ lines of input, may be str or function which '
        'returns a str.'),
    'OLDPWD': VarDocs('Used to represent a previous present working directory.',
        configurable=False),
    'PATH': VarDocs(
        'List of strings representing where to look for executables.'),
    'PATHEXT': VarDocs('Sequence of extention strings (eg, ".EXE") for '
                       'filtering valid executables by. Each element must be '
                       'uppercase.'),
    'PRETTY_PRINT_RESULTS': VarDocs(
            'Flag for "pretty printing" return values.'),
    'PROMPT': VarDocs(
        'The prompt text. May contain keyword arguments which are '
        "auto-formatted, see 'Customizing the Prompt' at "
        'http://xon.sh/tutorial.html#customizing-the-prompt. '
        'This value is never inherited from parent processes.',
        default='xonsh.environ.DEFAULT_PROMPT'),
    'PUSHD_MINUS': VarDocs(
        'Flag for directory pushing functionality. False is the normal '
        'behavior.'),
    'PUSHD_SILENT': VarDocs(
        'Whether or not to suppress directory stack manipulation output.'),
    'RAISE_SUBPROC_ERROR': VarDocs(
        'Whether or not to raise an error if a subprocess (captured or '
        'uncaptured) returns a non-zero exit status, which indicates failure. '
        'This is most useful in xonsh scripts or modules where failures '
        'should cause an end to execution. This is less useful at a terminal. '
        'The error that is raised is a subprocess.CalledProcessError.'),
    'RIGHT_PROMPT': VarDocs('Template string for right-aligned text '
        'at the prompt. This may be parameterized in the same way as '
        'the $PROMPT variable. Currently, this is only available in the '
        'prompt-toolkit shell.'),
    'SHELL_TYPE': VarDocs(
        'Which shell is used. Currently two base shell types are supported:\n\n'
        "    - 'readline' that is backed by Python's readline module\n"
        "    - 'prompt_toolkit' that uses external library of the same name\n"
        "    - 'random' selects a random shell from the above on startup\n"
        "    - 'best' selects the most feature-rich shell available on the\n"
        "       user's system\n\n"
        'To use the prompt_toolkit shell you need to have the prompt_toolkit '
        '(https://github.com/jonathanslenders/python-prompt-toolkit) '
        'library installed. To specify which shell should be used, do so in '
        'the run control file.'),
    'SUBSEQUENCE_PATH_COMPLETION': VarDocs(
        "Toggles subsequence matching of paths for tab completion. "
        "If ``True``, then, e.g., ``~/u/ro`` can match ``~/lou/carcolh``."),
    'SUGGEST_COMMANDS': VarDocs(
        'When a user types an invalid command, xonsh will try to offer '
        'suggestions of similar valid commands if this is True.'),
    'SUGGEST_MAX_NUM': VarDocs(
        'xonsh will show at most this many suggestions in response to an '
        'invalid command. If negative, there is no limit to how many '
        'suggestions are shown.'),
    'SUGGEST_THRESHOLD': VarDocs(
        'An error threshold. If the Levenshtein distance between the entered '
        'command and a valid command is less than this value, the valid '
        'command will be offered as a suggestion.  Also used for "fuzzy" '
        'tab completion of paths.'),
    'SUPPRESS_BRANCH_TIMEOUT_MESSAGE': VarDocs(
        'Whether or not to supress branch timeout warning messages.'),
    'TEEPTY_PIPE_DELAY': VarDocs(
        'The number of [seconds] to delay a spawned process if it has '
        'information being piped in via stdin. This value must be a float. '
        'If a value less than or equal to zero is passed in, no delay is '
        'used. This can be used to fix situations where a spawned process, '
        'such as piping into \'grep\', exits too quickly for the piping '
        'operation itself. TeePTY (and thus this variable) are currently '
        'only used when $XONSH_STORE_STDOUT is True.',
        configurable=ON_LINUX),
    'TERM': VarDocs(
        'TERM is sometimes set by the terminal emulator. This is used (when '
        "valid) to determine whether or not to set the title. Users shouldn't "
        "need to set this themselves. Note that this variable should be set as "
        "early as possible in order to ensure it is effective. Here are a few "
        "options:\n\n"
        "* Set this from the program that launches xonsh. On POSIX systems, \n"
        "  this can be performed by using env, e.g. \n"
        "  '/usr/bin/env TERM=xterm-color xonsh' or similar.\n"
        "* From the xonsh command line, namely 'xonsh -DTERM=xterm-color'.\n"
        "* In the config file with '{\"env\": {\"TERM\": \"xterm-color\"}}'.\n"
        "* Lastly, in xonshrc with '$TERM'\n\n"
        "Ideally, your terminal emulator will set this correctly but that does "
        "not always happen.", configurable=False),
    'TITLE': VarDocs(
        'The title text for the window in which xonsh is running. Formatted '
        "in the same manner as $PROMPT, see 'Customizing the Prompt' "
        'http://xon.sh/tutorial.html#customizing-the-prompt.',
        default='xonsh.environ.DEFAULT_TITLE'),
    'UPDATE_OS_ENVIRON': VarDocs("If True os.environ will always be updated "
        "when the xonsh environment changes. The environment can be reset to "
        "the default value by calling '__xonsh_env__.undo_replace_env()'"),
    'VC_BRANCH_TIMEOUT': VarDocs('The timeout (in seconds) for version control '
        'branch computations. This is a timeout per subprocess call, so the '
        'total time to compute will be larger than this in many cases.'),
    'VI_MODE': VarDocs(
        "Flag to enable 'vi_mode' in the 'prompt_toolkit' shell."),
    'VIRTUAL_ENV': VarDocs(
        'Path to the currently active Python environment.', configurable=False),
    'WIN_UNICODE_CONSOLE': VarDocs(
        "Enables unicode support in windows terminals. Requires the external "
        "library 'win_unicode_console'.",
        configurable=ON_WINDOWS),
    'XDG_CONFIG_HOME': VarDocs(
        'Open desktop standard configuration home dir. This is the same '
        'default as used in the standard.', configurable=False,
        default="'~/.config'"),
    'XDG_DATA_HOME': VarDocs(
        'Open desktop standard data home dir. This is the same default as '
        'used in the standard.', default="'~/.local/share'"),
    'XONSHCONFIG': VarDocs(
        'The location of the static xonsh configuration file, if it exists. '
        'This is in JSON format.', configurable=False,
        default="'$XONSH_CONFIG_DIR/config.json'"),
    'XONSHRC': VarDocs(
        'A tuple of the locations of run control files, if they exist.  User '
        'defined run control file will supersede values set in system-wide '
        'control file if there is a naming collision.', default=(
        "On Linux & Mac OSX: ('/etc/xonshrc', '~/.xonshrc')\n"
        "On Windows: ('%ALLUSERSPROFILE%\\xonsh\\xonshrc', '~/.xonshrc')")),
    'XONSH_CACHE_SCRIPTS': VarDocs(
        'Controls whether the code for scripts run from xonsh will be cached'
        ' (``True``) or re-compiled each time (``False``).'),
    'XONSH_CACHE_EVERYTHING': VarDocs(
        'Controls whether all code (including code entered at the interactive'
        ' prompt) will be cached.'),
    'XONSH_COLOR_STYLE': VarDocs(
        'Sets the color style for xonsh colors. This is a style name, not '
        'a color map. Run ``xonfig styles`` to see the available styles.'),
    'XONSH_CONFIG_DIR': VarDocs(
        'This is the location where xonsh configuration information is stored.',
        configurable=False, default="'$XDG_CONFIG_HOME/xonsh'"),
    'XONSH_DEBUG': VarDocs(
        'Sets the xonsh debugging level. This may be an integer or a boolean, '
        'with higher values cooresponding to higher debuging levels and more '
        'information presented. Setting this variable prior to stating xonsh '
        'will supress amalgamated imports.', configurable=False),
    'XONSH_DATA_DIR': VarDocs(
        'This is the location where xonsh data files are stored, such as '
        'history.', default="'$XDG_DATA_HOME/xonsh'"),
    'XONSH_ENCODING': VarDocs(
        'This is the encoding that xonsh should use for subprocess operations.',
        default='sys.getdefaultencoding()'),
    'XONSH_ENCODING_ERRORS': VarDocs(
        'The flag for how to handle encoding errors should they happen. '
        'Any string flag that has been previously registered with Python '
        "is allowed. See the 'Python codecs documentation' "
        "(https://docs.python.org/3/library/codecs.html#error-handlers) "
        'for more information and available options.',
        default="'surrogateescape'"),
    'XONSH_HISTORY_FILE': VarDocs('Location of history file (deprecated).',
        configurable=False, default="'~/.xonsh_history'"),
    'XONSH_HISTORY_SIZE': VarDocs(
        'Value and units tuple that sets the size of history after garbage '
        'collection. Canonical units are:\n\n'
        "- 'commands' for the number of past commands executed,\n"
        "- 'files' for the number of history files to keep,\n"
        "- 's' for the number of seconds in the past that are allowed, and\n"
        "- 'b' for the number of bytes that history may consume.\n\n"
        "Common abbreviations, such as '6 months' or '1 GB' are also allowed.",
        default="(8128, 'commands') or '8128 commands'"),
    'XONSH_INTERACTIVE': VarDocs(
        'True if xonsh is running interactively, and False otherwise.',
        configurable=False),
    'XONSH_LOGIN': VarDocs(
        'True if xonsh is running as a login shell, and False otherwise.',
        configurable=False),
    'XONSH_SHOW_TRACEBACK': VarDocs(
        'Controls if a traceback is shown if exceptions occur in the shell. '
        'Set to True to always show traceback or False to always hide. '
        'If undefined then the traceback is hidden but a notice is shown on how '
        'to enable the full traceback.'),
    'XONSH_SOURCE': VarDocs(
        "When running a xonsh script, this variable contains the absolute path "
        "to the currently executing script's file.",
        configurable=False),
    'XONSH_STORE_STDIN': VarDocs(
        'Whether or not to store the stdin that is supplied to the !() and ![] '
        'operators.'),
    'XONSH_STORE_STDOUT': VarDocs(
        'Whether or not to store the stdout and stderr streams in the '
        'history files.'),
    'XONSH_TRACEBACK_LOGFILE': VarDocs(
        'Specifies a file to store the traceback log to, regardless of whether '
        'XONSH_SHOW_TRACEBACK has been set. Its value must be a writable file '
        'or None / the empty string if traceback logging is not desired. '
        'Logging to a file is not enabled by default.'),
}

#
# actual environment
#

class Env(MutableMapping):
    """A xonsh environment, whose variables have limited typing
    (unlike BASH). Most variables are, by default, strings (like BASH).
    However, the following rules also apply based on variable-name:

    * PATH: any variable whose name ends in PATH is a list of strings.
    * XONSH_HISTORY_SIZE: this variable is an (int | float, str) tuple.
    * LC_* (locale categories): locale catergory names get/set the Python
      locale via locale.getlocale() and locale.setlocale() functions.

    An Env instance may be converted to an untyped version suitable for
    use in a subprocess.
    """

    _arg_regex = re.compile(r'ARG(\d+)')

    def __init__(self, *args, **kwargs):
        """If no initial environment is given, os.environ is used."""
        self._d = {}
        self._orig_env = None
        self._ensurers = {k: Ensurer(*v) for k, v in DEFAULT_ENSURERS.items()}
        self._defaults = DEFAULT_VALUES
        self._docs = DEFAULT_DOCS
        if len(args) == 0 and len(kwargs) == 0:
            args = (os.environ, )
        for key, val in dict(*args, **kwargs).items():
            self[key] = val
        if 'PATH' not in self._d:
            # this is here so the PATH is accessible to subprocs and so that
            # it can be modified in-place in the xonshrc file
            self._d['PATH'] = list(PATH_DEFAULT)
        self._detyped = None

    @staticmethod
    def detypeable(val):
        return not (callable(val) or isinstance(val, MutableMapping))

    def detype(self):
        if self._detyped is not None:
            return self._detyped
        ctx = {}
        for key, val in self._d.items():
            if not self.detypeable(val):
                continue
            if not isinstance(key, str):
                key = str(key)
            ensurer = self.get_ensurer(key)
            val = ensurer.detype(val)
            ctx[key] = val
        self._detyped = ctx
        return ctx

    def replace_env(self):
        """Replaces the contents of os.environ with a detyped version
        of the xonsh environement.
        """
        if self._orig_env is None:
            self._orig_env = dict(os.environ)
        os.environ.clear()
        os.environ.update(self.detype())

    def undo_replace_env(self):
        """Replaces the contents of os.environ with a detyped version
        of the xonsh environement.
        """
        if self._orig_env is not None:
            os.environ.clear()
            os.environ.update(self._orig_env)
            self._orig_env = None

    def get_ensurer(self, key,
                    default=Ensurer(always_true, None, ensure_string)):
        """Gets an ensurer for the given key."""
        if key in self._ensurers:
            return self._ensurers[key]
        for k, ensurer in self._ensurers.items():
            if isinstance(k, str):
                continue
            if k.match(key) is not None:
                break
        else:
            ensurer = default
        self._ensurers[key] = ensurer
        return ensurer

    def get_docs(self, key, default=VarDocs('<no documentation>')):
        """Gets the documentation for the environment variable."""
        vd = self._docs.get(key, None)
        if vd is None:
            return default
        if vd.default is DefaultNotGiven:
            dval = pformat(self._defaults.get(key, '<default not set>'))
            vd = vd._replace(default=dval)
            self._docs[key] = vd
        return vd

    def is_manually_set(self, varname):
        """
        Checks if an environment variable has been manually set.
        """
        return varname in self._d

    @contextmanager
    def swap(self, other=None, **kwargs):
        """Provides a context manager for temporarily swapping out certain
        environment variables with other values. On exit from the context
        manager, the original values are restored.
        """
        old = {}
        # single positional argument should be a dict-like object
        if other is not None:
            for k, v in other.items():
                old[k] = self.get(k, NotImplemented)
                self[k] = v
        # kwargs could also have been sent in
        for k, v in kwargs.items():
            old[k] = self.get(k, NotImplemented)
            self[k] = v

        yield self
        # restore the values
        for k, v in old.items():
            if v is NotImplemented:
                del self[k]
            else:
                self[k] = v


    #
    # Mutable mapping interface
    #

    def __getitem__(self, key):
        if key is Ellipsis:
            return self
        m = self._arg_regex.match(key)
        if (m is not None) and (key not in self._d) and ('ARGS' in self._d):
            args = self._d['ARGS']
            ix = int(m.group(1))
            if ix >= len(args):
                e = "Not enough arguments given to access ARG{0}."
                raise KeyError(e.format(ix))
            val = self._d['ARGS'][ix]
        elif key in self._d:
            val = self._d[key]
        elif key in self._defaults:
            val = self._defaults[key]
            if is_callable_default(val):
                val = val(self)
        else:
            e = "Unknown environment variable: ${}"
            raise KeyError(e.format(key))
        if isinstance(val, (MutableSet, MutableSequence, MutableMapping)):
            self._detyped = None
        return val

    def __setitem__(self, key, val):
        ensurer = self.get_ensurer(key)
        if not ensurer.validate(val):
            val = ensurer.convert(val)
        self._d[key] = val
        if self.detypeable(val):
            self._detyped = None
            if self.get('UPDATE_OS_ENVIRON'):
                if self._orig_env is None:
                    self.replace_env()
                else:
                    os.environ[key] = ensurer.detype(val)

    def __delitem__(self, key):
        val = self._d.pop(key)
        if self.detypeable(val):
            self._detyped = None
            if self.get('UPDATE_OS_ENVIRON') and key in os.environ:
                del os.environ[key]

    def get(self, key, default=None):
        """The environment will look up default values from its own defaults if a
        default is not given here.
        """
        try:
            return self[key]
        except KeyError:
            return default

    def __iter__(self):
        yield from (set(self._d) | set(self._defaults))

    def __len__(self):
        return len(self._d)

    def __str__(self):
        return str(self._d)

    def __repr__(self):
        return '{0}.{1}(...)'.format(self.__class__.__module__,
                                     self.__class__.__name__, self._d)

    def _repr_pretty_(self, p, cycle):
        name = '{0}.{1}'.format(self.__class__.__module__,
                                self.__class__.__name__)
        with p.group(0, name + '(', ')'):
            if cycle:
                p.text('...')
            elif len(self):
                p.break_()
                p.pretty(dict(self))


def _yield_executables(directory, name):
    if ON_WINDOWS:
        base_name, ext = os.path.splitext(name.lower())
        for fname in executables_in(directory):
            fbase, fext = os.path.splitext(fname.lower())
            if base_name == fbase and (len(ext) == 0 or ext == fext):
                yield os.path.join(directory, fname)
    else:
        for x in executables_in(directory):
            if x == name:
                yield os.path.join(directory, name)
                return


def locate_binary(name):
    """Locates an executable on the file system."""
    return builtins.__xonsh_commands_cache__.locate_binary(name)


def get_git_branch():
    """Attempts to find the current git branch.  If no branch is found, then
    an empty string is returned. If a timeout occured, the timeout exception
    (subprocess.TimeoutExpired) is returned.
    """
    branch = None
    env = builtins.__xonsh_env__
    cwd = env['PWD']
    denv = env.detype()
    vcbt = env['VC_BRANCH_TIMEOUT']
    if not ON_WINDOWS:
        prompt_scripts = ['/usr/lib/git-core/git-sh-prompt',
                          '/usr/local/etc/bash_completion.d/git-prompt.sh']
        for script in prompt_scripts:
            # note that this is about 10x faster than bash -i "__git_ps1"
            inp = 'source {}; __git_ps1 "${{1:-%s}}"'.format(script)
            try:
                branch = subprocess.check_output(['bash'], cwd=cwd, input=inp,
                            stderr=subprocess.PIPE, timeout=vcbt, env=denv,
                            universal_newlines=True)
                break
            except subprocess.TimeoutExpired as e:
                branch = e
                break
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
    # fall back to using the git binary if the above failed
    if branch is None:
        cmd = ['git', 'rev-parse', '--abbrev-ref', 'HEAD']
        try:
            s = subprocess.check_output(cmd, cwd=cwd, timeout=vcbt, env=denv,
                    stderr=subprocess.PIPE, universal_newlines=True)
            if ON_WINDOWS and len(s) == 0:
                # Workaround for a bug in ConEMU/cmder, retry without redirection
                s = subprocess.check_output(cmd, cwd=cwd, timeout=vcbt,
                                            env=denv, universal_newlines=True)
            branch = s.strip()
        except subprocess.TimeoutExpired as e:
            branch = e
        except (subprocess.CalledProcessError, FileNotFoundError):
            branch = ''
    return branch


def _get_parent_dir_for(path, dir_name, timeout):
    # walk up the directory tree to see if we are inside an hg repo
    # the timeout makes sure that we don't thrash the file system
    previous_path = ''
    t0 = time.time()
    while path != previous_path and ((time.time() - t0) < timeout):
        if os.path.isdir(os.path.join(path, dir_name)):
            return path
        previous_path = path
        path, _ = os.path.split(path)
    return (path == previous_path)


def get_hg_branch(cwd=None, root=None):
    env = builtins.__xonsh_env__
    cwd = env['PWD']
    root = _get_parent_dir_for(cwd, '.hg', env['VC_BRANCH_TIMEOUT'])
    if not isinstance(root, str):
        # Bail if we are not in a repo or we timed out
        if root:
            return ''
        else:
            return subprocess.TimeoutExpired(['hg'], env['VC_BRANCH_TIMEOUT'])
    # get branch name
    branch_path = os.path.sep.join([root, '.hg', 'branch'])
    if os.path.exists(branch_path):
        with open(branch_path, 'r') as branch_file:
            branch = branch_file.read()
    else:
        branch = 'default'
    # add bookmark, if we can
    bookmark_path = os.path.sep.join([root, '.hg', 'bookmarks.current'])
    if os.path.exists(bookmark_path):
        with open(bookmark_path, 'r') as bookmark_file:
            active_bookmark = bookmark_file.read()
        branch = "{0}, {1}".format(*(b.strip(os.linesep) for b in
                                   (branch, active_bookmark)))
    else:
        branch = branch.strip(os.linesep)
    return branch


_FIRST_BRANCH_TIMEOUT = True

def _first_branch_timeout_message():
    global _FIRST_BRANCH_TIMEOUT
    sbtm = builtins.__xonsh_env__['SUPPRESS_BRANCH_TIMEOUT_MESSAGE']
    if not _FIRST_BRANCH_TIMEOUT or sbtm:
        return
    _FIRST_BRANCH_TIMEOUT = False
    print('xonsh: branch timeout: computing the branch name, color, or both '
          'timed out while formatting the prompt. You may avoid this by '
          'increaing the value of $VC_BRANCH_TIMEOUT or by removing branch '
          'fields, like {curr_branch}, from your $PROMPT. See the FAQ '
          'for more details. This message will be suppressed for the remainder '
          'of this session. To suppress this message permanently, set '
          '$SUPPRESS_BRANCH_TIMEOUT_MESSAGE = True in your xonshrc file.',
          file=sys.stderr)


def current_branch(pad=True):
    """Gets the branch for a current working directory. Returns an empty string
    if the cwd is not a repository.  This currently only works for git and hg
    and should be extended in the future.  If a timeout occurred, the string
    '<branch-timeout>' is returned.
    """
    branch = ''
    cmds = builtins.__xonsh_commands_cache__
    if cmds.lazy_locate_binary('git') or cmds.is_empty():
        branch = get_git_branch()
    if (cmds.lazy_locate_binary('hg') or cmds.is_empty()) and not branch:
        branch = get_hg_branch()
    if isinstance(branch, subprocess.TimeoutExpired):
        branch = '<branch-timeout>'
        _first_branch_timeout_message()
    if pad and branch:
        branch = ' ' + branch
    return branch


def git_dirty_working_directory(cwd=None, include_untracked=False):
    """Returns whether or not the git directory is dirty. If this could not
    be determined (timeout, file not sound, etc.) then this returns None.
    """
    cmd = ['git', 'status', '--porcelain']
    if include_untracked:
        cmd.append('--untracked-files=normal')
    else:
        cmd.append('--untracked-files=no')
    env = builtins.__xonsh_env__
    cwd = env['PWD']
    denv = env.detype()
    vcbt = env['VC_BRANCH_TIMEOUT']
    try:
        s = subprocess.check_output(cmd, stderr=subprocess.PIPE, cwd=cwd,
                                    timeout=vcbt, universal_newlines=True,
                                    env=denv)
        if ON_WINDOWS and len(s) == 0:
            # Workaround for a bug in ConEMU/cmder, retry without redirection
            s = subprocess.check_output(cmd, cwd=cwd, timeout=vcbt,
                                        env=denv, universal_newlines=True)
        return bool(s)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired,
            FileNotFoundError):
        return None


def hg_dirty_working_directory():
    """Computes whether or not the mercurial working directory is dirty or not.
    If this cannot be deterimined, None is returned.
    """
    env = builtins.__xonsh_env__
    cwd = env['PWD']
    denv = env.detype()
    vcbt = env['VC_BRANCH_TIMEOUT']
    # Override user configurations settings and aliases
    denv['HGRCPATH'] = ''
    try:
        s = subprocess.check_output(['hg', 'identify', '--id'],
                stderr=subprocess.PIPE, cwd=cwd, timeout=vcbt,
                universal_newlines=True, env=denv)
        return s.strip(os.linesep).endswith('+')
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired,
            FileNotFoundError):
        return None


def dirty_working_directory(cwd=None):
    """Returns a boolean as to whether there are uncommitted files in version
    control repository we are inside. If this cannot be determined, returns
    None. Currently supports git and hg.
    """
    dwd = None
    cmds = builtins.__xonsh_commands_cache__
    if cmds.lazy_locate_binary('git') or cmds.is_empty():
        dwd = git_dirty_working_directory()
    if (cmds.lazy_locate_binary('hg') or cmds.is_empty()) and (dwd is None):
        dwd = hg_dirty_working_directory()
    return dwd


def branch_color():
    """Return red if the current branch is dirty, yellow if the dirtiness can
    not be determined, and green if it clean. These are bold, intense colors
    for the foreground.
    """
    dwd = dirty_working_directory()
    if dwd is None:
        color = '{BOLD_INTENSE_YELLOW}'
    elif dwd:
        color = '{BOLD_INTENSE_RED}'
    else:
        color = '{BOLD_INTENSE_GREEN}'
    return color


def branch_bg_color():
    """Return red if the current branch is dirty, yellow if the dirtiness can
    not be determined, and green if it clean. These are bacground colors.
    """
    dwd = dirty_working_directory()
    if dwd is None:
        color = '{BACKGROUND_YELLOW}'
    elif dwd:
        color = '{BACKGROUND_RED}'
    else:
        color = '{BACKGROUND_GREEN}'
    return color


def _replace_home(x):
    if ON_WINDOWS:
        home = (builtins.__xonsh_env__['HOMEDRIVE'] +
                builtins.__xonsh_env__['HOMEPATH'][0])
        if x.startswith(home):
            x = x.replace(home, '~', 1)

        if builtins.__xonsh_env__.get('FORCE_POSIX_PATHS'):
            x = x.replace(os.sep, os.altsep)

        return x
    else:
        home = builtins.__xonsh_env__['HOME']
        if x.startswith(home):
            x = x.replace(home, '~', 1)
        return x

_replace_home_cwd = lambda: _replace_home(builtins.__xonsh_env__['PWD'])

def _collapsed_pwd():
    sep = get_sep()
    pwd = _replace_home_cwd().split(sep)
    l = len(pwd)
    leader = sep if l>0 and len(pwd[0])==0 else ''
    base = [i[0] if ix != l-1 else i for ix,i in enumerate(pwd) if len(i) > 0]
    return leader + sep.join(base)

def _dynamically_collapsed_pwd():
    """Return the compact current working directory.  It respects the
    environment variable DYNAMIC_CWD_WIDTH.
    """
    originial_path = _replace_home_cwd()
    target_width, units = builtins.__xonsh_env__['DYNAMIC_CWD_WIDTH']
    if target_width == float('inf'):
        return originial_path
    if (units == '%'):
        cols, _ = shutil.get_terminal_size()
        target_width = (cols * target_width) // 100
    sep = get_sep()
    pwd = originial_path.split(sep)
    last = pwd.pop()
    remaining_space = target_width - len(last)
    # Reserve space for separators
    remaining_space_for_text = remaining_space - len(pwd)
    parts = []
    for i  in range(len(pwd)):
        part = pwd[i]
        part_len = int(min(len(part), max(1, remaining_space_for_text // (len(pwd) - i))))
        remaining_space_for_text -= part_len
        reduced_part = part[0:part_len]
        parts.append(reduced_part)
    parts.append(last)
    full = sep.join(parts)
    # If even if displaying one letter per dir we are too long
    if (len(full) > target_width):
        # We truncate the left most part
        full = "..." + full[int(-target_width) + 3:]
        # if there is not even a single separator we still
        # want to display at least the beginning of the directory
        if full.find(sep) == -1:
            full = ("..." + sep + last)[0:int(target_width)]
    return full


def _current_job():
    j = get_next_task()
    if j is not None:
        if not j['bg']:
            cmd = j['cmds'][-1]
            s = cmd[0]
            if s == 'sudo' and len(cmd) > 1:
                s = cmd[1]
            return '{} | '.format(s)
    return ''


def env_name(pre_chars='(', post_chars=') '):
    """Extract the current environment name from $VIRTUAL_ENV or
    $CONDA_DEFAULT_ENV if that is set
    """
    env_path = builtins.__xonsh_env__.get('VIRTUAL_ENV', '')
    if len(env_path) == 0 and ON_ANACONDA:
        pre_chars, post_chars = '[', '] '
        env_path = builtins.__xonsh_env__.get('CONDA_DEFAULT_ENV', '')
    env_name = os.path.basename(env_path)
    return pre_chars + env_name + post_chars if env_name else ''


if ON_WINDOWS:
    USER = 'USERNAME'
else:
    USER = 'USER'


FORMATTER_DICT = dict(
    user=os.environ.get(USER, '<user>'),
    prompt_end='#' if is_superuser() else '$',
    hostname=socket.gethostname().split('.', 1)[0],
    cwd=_dynamically_collapsed_pwd,
    cwd_dir=lambda: os.path.dirname(_replace_home_cwd()),
    cwd_base=lambda: os.path.basename(_replace_home_cwd()),
    short_cwd=_collapsed_pwd,
    curr_branch=current_branch,
    branch_color=branch_color,
    branch_bg_color=branch_bg_color,
    current_job=_current_job,
    env_name=env_name,
    )

DEFAULT_VALUES['FORMATTER_DICT'] = dict(FORMATTER_DICT)

_FORMATTER = string.Formatter()


def is_template_string(template, formatter_dict=None):
    """Returns whether or not the string is a valid template."""
    template = template() if callable(template) else template
    try:
        included_names = set(i[1] for i in _FORMATTER.parse(template))
    except ValueError:
        return False
    included_names.discard(None)
    if formatter_dict is None:
        fmtter = builtins.__xonsh_env__.get('FORMATTER_DICT', FORMATTER_DICT)
    else:
        fmtter = formatter_dict
    known_names = set(fmtter.keys())
    return included_names <= known_names


def _get_fmtter(formatter_dict=None):
    if formatter_dict is None:
        fmtter = builtins.__xonsh_env__.get('FORMATTER_DICT', FORMATTER_DICT)
    else:
        fmtter = formatter_dict
    return fmtter


def _failover_template_format(template):
    if callable(template):
        try:
            # Exceptions raises from function of producing $PROMPT
            # in user's xonshrc should not crash xonsh
            return template()
        except Exception:
            print_exception()
            return '$ '
    return template


def format_prompt(template=DEFAULT_PROMPT, formatter_dict=None):
    try:
        return _format_prompt_main(template, formatter_dict)
    except:
        return _failover_template_format(template)


def _format_prompt_main(template, formatter_dict):
    """Formats a xonsh prompt template string."""
    template = template() if callable(template) else template
    fmtter = _get_fmtter(formatter_dict)
    included_names = set(i[1] for i in _FORMATTER.parse(template))
    fmt = {}
    for name in included_names:
        if name is None:
            continue
        if name.startswith('$'):
            v = builtins.__xonsh_env__[name[1:]]
        else:
            v = fmtter[name]
        val = v() if callable(v) else v
        val = '' if val is None else val
        fmt[name] = val
    return template.format(**fmt)


def partial_format_prompt(template=DEFAULT_PROMPT, formatter_dict=None):
    """Formats a xonsh prompt template string."""
    try:
        return _partial_format_prompt_main(template=template,
                                           formatter_dict=formatter_dict)
    except:
        return _failover_template_format(template)


def _partial_format_prompt_main(template=DEFAULT_PROMPT, formatter_dict=None):
    template = template() if callable(template) else template
    fmtter = _get_fmtter(formatter_dict)
    bopen = '{'
    bclose = '}'
    colon = ':'
    expl = '!'
    toks = []
    for literal, field, spec, conv in _FORMATTER.parse(template):
        toks.append(literal)
        if field is None:
            continue
        elif field.startswith('$'):
            v = builtins.__xonsh_env__[field[1:]]
            v = _FORMATTER.convert_field(v, conv)
            v = _FORMATTER.format_field(v, spec)
            toks.append(v)
            continue
        elif field in fmtter:
            v = fmtter[field]
            val = v() if callable(v) else v
            val = '' if val is None else val
            toks.append(val)
        else:
            toks.append(bopen)
            toks.append(field)
            if conv is not None and len(conv) > 0:
                toks.append(expl)
                toks.append(conv)
            if spec is not None and len(spec) > 0:
                toks.append(colon)
                toks.append(spec)
            toks.append(bclose)
    return ''.join(toks)


RE_HIDDEN = re.compile('\001.*?\002')

def multiline_prompt(curr=''):
    """Returns the filler text for the prompt in multiline scenarios."""
    line = curr.rsplit('\n', 1)[1] if '\n' in curr else curr
    line = RE_HIDDEN.sub('', line)  # gets rid of colors
    # most prompts end in whitespace, head is the part before that.
    head = line.rstrip()
    headlen = len(head)
    # tail is the trailing whitespace
    tail = line if headlen == 0 else line.rsplit(head[-1], 1)[1]
    # now to constuct the actual string
    dots = builtins.__xonsh_env__.get('MULTILINE_PROMPT')
    dots = dots() if callable(dots) else dots
    if dots is None or len(dots) == 0:
        return ''
    tokstr = format_color(dots, hide=True)
    baselen = 0
    basetoks = []
    for x in tokstr.split('\001'):
        pre, sep, post = x.partition('\002')
        if len(sep) == 0:
            basetoks.append(('', pre))
            baselen += len(pre)
        else:
            basetoks.append(('\001' + pre + '\002', post))
            baselen += len(post)
    if baselen == 0:
        return format_color('{NO_COLOR}' + tail, hide=True)
    toks = basetoks * (headlen // baselen)
    n = headlen % baselen
    count = 0
    for tok in basetoks:
        slen = len(tok[1])
        newcount = slen + count
        if slen == 0:
            continue
        elif newcount <= n:
            toks.append(tok)
        else:
            toks.append((tok[0], tok[1][:n-count]))
        count = newcount
        if n <= count:
            break
    toks.append((format_color('{NO_COLOR}', hide=True), tail))
    rtn = ''.join(chain.from_iterable(toks))
    return rtn


BASE_ENV = {
    'BASH_COMPLETIONS': list(DEFAULT_VALUES['BASH_COMPLETIONS']),
    'FORMATTER_DICT': dict(DEFAULT_VALUES['FORMATTER_DICT']),
    'XONSH_VERSION': XONSH_VERSION,
}

def load_static_config(ctx, config=None):
    """Loads a static configuration file from a given context, rather than the
    current environment.  Optionally may pass in configuration file name.
    """
    env = {}
    env['XDG_CONFIG_HOME'] = ctx.get('XDG_CONFIG_HOME',
                                     DEFAULT_VALUES['XDG_CONFIG_HOME'])
    env['XONSH_CONFIG_DIR'] = ctx['XONSH_CONFIG_DIR'] if 'XONSH_CONFIG_DIR' in ctx \
                              else xonsh_config_dir(env)
    if config is not None:
        env['XONSHCONFIG'] = ctx['XONSHCONFIG'] = config
    elif 'XONSHCONFIG' in ctx:
        config = env['XONSHCONFIG'] = ctx['XONSHCONFIG']
    else:
        # don't set in ctx in order to maintain default
        config = env['XONSHCONFIG'] = xonshconfig(env)
    if os.path.isfile(config):
        # Note that an Env instance at __xonsh_env__ has not been started yet,
        # per se, so we have to use os.environ
        encoding = os.environ.get('XONSH_ENCODING',
                                  DEFAULT_VALUES.get('XONSH_ENCODING', 'utf8'))
        errors = os.environ.get('XONSH_ENCODING_ERRORS',
                                DEFAULT_VALUES.get('XONSH_ENCODING_ERRORS',
                                                   'surrogateescape'))
        with open(config, 'r', encoding=encoding, errors=errors) as f:
            try:
                conf = json.load(f)
                assert isinstance(conf, Mapping)
                ctx['LOADED_CONFIG'] = True
            except Exception as e:
                conf = {}
                ctx['LOADED_CONFIG'] = False
                print_exception()
                # JSONDecodeError was added in Python v3.5
                jerr = json.JSONDecodeError \
                       if hasattr(json, 'JSONDecodeError') else ValueError
                if isinstance(e, jerr):
                    msg = 'Xonsh config file is not valid JSON.'
                else:
                    msg = 'Could not load xonsh config.'
                print(msg, file=sys.stderr)
    else:
        conf = {}
        ctx['LOADED_CONFIG'] = False
    builtins.__xonsh_config__ = conf
    return conf


def xonshrc_context(rcfiles=None, execer=None, initial=None):
    """Attempts to read in xonshrc file, and return the contents."""
    loaded = builtins.__xonsh_env__['LOADED_RC_FILES'] = []
    if initial is None:
        env = {}
    else:
        env = initial
    if rcfiles is None or execer is None:
        return env
    env['XONSHRC'] = tuple(rcfiles)
    for rcfile in rcfiles:
        if not os.path.isfile(rcfile):
            loaded.append(False)
            continue
        try:
            run_script_with_cache(rcfile, execer, env)
            loaded.append(True)
        except SyntaxError as err:
            loaded.append(False)
            msg = 'syntax error in xonsh run control file {0!r}: {1!s}'
            warn(msg.format(rcfile, err), RuntimeWarning)
            continue
        except Exception as err:
            loaded.append(False)
            msg = 'error running xonsh run control file {0!r}: {1!s}'
            warn(msg.format(rcfile, err), RuntimeWarning)
            continue
    return env


def windows_foreign_env_fixes(ctx):
    """Environment fixes for Windows. Operates in-place."""
    # remove these bash variables which only cause problems.
    for ev in ['HOME', 'OLDPWD']:
        if ev in ctx:
            del ctx[ev]
    # Override path-related bash variables; on Windows bash uses
    # /c/Windows/System32 syntax instead of C:\\Windows\\System32
    # which messes up these environment variables for xonsh.
    for ev in ['PATH', 'TEMP', 'TMP']:
        if ev in os.environ:
            ctx[ev] = os.environ[ev]
        elif ev in ctx:
            del ctx[ev]
    ctx['PWD'] = _get_cwd() or ''


def foreign_env_fixes(ctx):
    """Environment fixes for all operating systems"""
    if 'PROMPT' in ctx:
        del ctx['PROMPT']

def default_env(env=None, config=None, login=True):
    """Constructs a default xonsh environment."""
    # in order of increasing precedence
    ctx = dict(BASE_ENV)
    ctx.update(os.environ)
    ctx['PWD'] = _get_cwd() or ''
    # other shells' PROMPT definitions generally don't work in XONSH:
    try:
        del ctx['PROMPT']
    except KeyError:
        pass

    if login:
        conf = load_static_config(ctx, config=config)

        foreign_env = load_foreign_envs(shells=conf.get('foreign_shells', ()),
                                        issue_warning=False)
        if ON_WINDOWS:
            windows_foreign_env_fixes(foreign_env)
        foreign_env_fixes(foreign_env)

        ctx.update(foreign_env)

        # Do static config environment last, to allow user to override any of
        # our environment choices
        ctx.update(conf.get('env', ()))

    # finalize env
    if env is not None:
        ctx.update(env)
    return ctx

#
# history
#
# -*- coding: utf-8 -*-
"""Implements the xonsh history object."""
# amalgamated os
# amalgamated sys
# amalgamated argparse
# amalgamated functools
operator = _LazyModule.load('operator', 'operator')
uuid = _LazyModule.load('uuid', 'uuid')
# amalgamated time
# amalgamated datetime
# amalgamated builtins
from glob import iglob
from collections import OrderedDict
from threading import Condition
# amalgamated xonsh.lazyjson
# amalgamated xonsh.tools
# amalgamated xonsh.diff_history
def _gc_commands_to_rmfiles(hsize, files):
    """Return the history files to remove to get under the command limit."""
    rmfiles = []
    n = 0
    ncmds = 0
    for ts, fcmds, f in files[::-1]:
        if fcmds == 0:
            # we need to make sure that 'empty' history files don't hang around
            rmfiles.append((ts, fcmds, f))
        if ncmds + fcmds > hsize:
            break
        ncmds += fcmds
        n += 1
    rmfiles += files[:-n]
    return rmfiles


def _gc_files_to_rmfiles(hsize, files):
    """Return the history files to remove to get under the file limit."""
    rmfiles = files[:-hsize] if len(files) > hsize else []
    return rmfiles


def _gc_seconds_to_rmfiles(hsize, files):
    """Return the history files to remove to get under the age limit."""
    rmfiles = []
    now = time.time()
    for ts, _, f in files:
        if (now - ts) < hsize:
            break
        rmfiles.append((None, None, f))
    return rmfiles


def _gc_bytes_to_rmfiles(hsize, files):
    """Return the history files to remove to get under the byte limit."""
    rmfiles = []
    n = 0
    nbytes = 0
    for _, _, f in files[::-1]:
        fsize = os.stat(f).st_size
        if nbytes + fsize > hsize:
            break
        nbytes += fsize
        n += 1
    rmfiles = files[:-n]
    return rmfiles


class HistoryGC(Thread):
    """Shell history garbage collection."""

    def __init__(self, wait_for_shell=True, size=None, *args, **kwargs):
        """Thread responsible for garbage collecting old history.

        May wait for shell (and for xonshrc to have been loaded) to start work.
        """
        super().__init__(*args, **kwargs)
        self.daemon = True
        self.size = size
        self.wait_for_shell = wait_for_shell
        self.start()
        self.gc_units_to_rmfiles = {'commands': _gc_commands_to_rmfiles,
                                    'files': _gc_files_to_rmfiles,
                                    's': _gc_seconds_to_rmfiles,
                                    'b': _gc_bytes_to_rmfiles}

    def run(self):
        while self.wait_for_shell:
            time.sleep(0.01)
        env = builtins.__xonsh_env__  # pylint: disable=no-member
        if self.size is None:
            hsize, units = env.get('XONSH_HISTORY_SIZE')
        else:
            hsize, units = to_history_tuple(self.size)
        files = self.files(only_unlocked=True)
        rmfiles_fn = self.gc_units_to_rmfiles.get(units)
        if rmfiles_fn is None:
            raise ValueError('Units type {0!r} not understood'.format(units))

        for _, _, f in rmfiles_fn(hsize, files):
            try:
                os.remove(f)
            except OSError:
                pass

    def files(self, only_unlocked=False):
        """Find and return the history files. Optionally locked files may be
        excluded.

        This is sorted by the last closed time. Returns a list of (timestamp,
        file) tuples.
        """
        _ = self  # this could be a function but is intimate to this class
        # pylint: disable=no-member
        xdd = builtins.__xonsh_env__.get('XONSH_DATA_DIR')
        xdd = expanduser_abs_path(xdd)

        fs = [f for f in iglob(os.path.join(xdd, 'xonsh-*.json'))]
        files = []
        for f in fs:
            try:
                lj = LazyJSON(f, reopen=False)
                if only_unlocked and lj['locked']:
                    continue
                # info: closing timestamp, number of commands, filename
                files.append((lj['ts'][1] or time.time(),
                              len(lj.sizes['cmds']) - 1,
                              f))
                lj.close()
            except (IOError, OSError, ValueError):
                continue
        files.sort()
        return files


class HistoryFlusher(Thread):
    """Flush shell history to disk periodically."""

    def __init__(self, filename, buffer, queue, cond, at_exit=False, *args,
                 **kwargs):
        """Thread for flushing history."""
        super(HistoryFlusher, self).__init__(*args, **kwargs)
        self.filename = filename
        self.buffer = buffer
        self.queue = queue
        queue.append(self)
        self.cond = cond
        self.at_exit = at_exit
        if at_exit:
            self.dump()
            queue.popleft()
        else:
            self.start()

    def run(self):
        with self.cond:
            self.cond.wait_for(self.i_am_at_the_front)
            self.dump()
            self.queue.popleft()

    def i_am_at_the_front(self):
        """Tests if the flusher is at the front of the queue."""
        return self is self.queue[0]

    def dump(self):
        """Write the cached history to external storage."""
        with open(self.filename, 'r', newline='\n') as f:
            hist = LazyJSON(f).load()
        hist['cmds'].extend(self.buffer)
        if self.at_exit:
            hist['ts'][1] = time.time()  # apply end time
            hist['locked'] = False
        with open(self.filename, 'w', newline='\n') as f:
            ljdump(hist, f, sort_keys=True)


class CommandField(Sequence):
    """A field in the 'cmds' portion of history."""

    def __init__(self, field, hist, default=None):
        """Represents a field in the 'cmds' portion of history.

        Will query the buffer for the relevant data, if possible. Otherwise it
        will lazily acquire data from the file.

        Parameters
        ----------
        field : str
            The name of the field to query.
        hist : History object
            The history object to query.
        default : optional
            The default value to return if key is not present.
        """
        self.field = field
        self.hist = hist
        self.default = default

    def __len__(self):
        return len(self.hist)

    def __getitem__(self, key):
        size = len(self)
        if isinstance(key, slice):
            return [self[i] for i in range(*key.indices(size))]
        elif not isinstance(key, int):
            raise IndexError(
                'CommandField may only be indexed by int or slice.')
        elif size == 0:
            raise IndexError('CommandField is empty.')
        # now we know we have an int
        key = size + key if key < 0 else key  # ensure key is non-negative
        bufsize = len(self.hist.buffer)
        if size - bufsize <= key:  # key is in buffer
            return self.hist.buffer[key + bufsize - size].get(
                self.field, self.default)
        # now we know we have to go into the file
        queue = self.hist._queue
        queue.append(self)
        with self.hist._cond:
            self.hist._cond.wait_for(self.i_am_at_the_front)
            with open(self.hist.filename, 'r', newline='\n') as f:
                lj = LazyJSON(f, reopen=False)
                rtn = lj['cmds'][key].get(self.field, self.default)
                if isinstance(rtn, LJNode):
                    rtn = rtn.load()
            queue.popleft()
        return rtn

    def i_am_at_the_front(self):
        """Tests if the command field is at the front of the queue."""
        return self is self.hist._queue[0]


def _find_histfile_var(file_list=None, default=None):
    if file_list is None:
        return None
    hist_file = None

    found_hist = False
    for f in file_list:
        f = expanduser_abs_path(f)
        if not os.path.isfile(f):
            continue
        with open(f, 'r') as rc_file:
            for line in rc_file:
                if "HISTFILE=" in line:
                    evar = line.split(' ', 1)[-1]
                    hist_file = evar.split('=', 1)[-1]
                    for char in ['"', "'", '\n']:
                        hist_file = hist_file.replace(char, '')
                    hist_file = expanduser_abs_path(hist_file)
                    if os.path.isfile(hist_file):
                        found_hist = True
                        break
        if found_hist:
            break

    if hist_file is None:
        default = expanduser_abs_path(default)
        if os.path.isfile(default):
            hist_file = default

    return hist_file


def _all_xonsh_parser(*args):
    """
    Returns all history as found in XONSH_DATA_DIR.

    return format: (name, start_time, index)
    """
    data_dir = builtins.__xonsh_env__.get('XONSH_DATA_DIR')
    data_dir = expanduser_abs_path(data_dir)

    files = [os.path.join(data_dir, f) for f in os.listdir(data_dir)
             if f.startswith('xonsh-') and f.endswith('.json')]
    file_hist = []
    for f in files:
        try:
            json_file = LazyJSON(f, reopen=False)
            file_hist.append(json_file.load()['cmds'])
        except ValueError:
            # Invalid json file
            pass
    commands = [(c['inp'][:-1] if c['inp'].endswith('\n') else c['inp'],
                 c['ts'][0])
                for commands in file_hist for c in commands if c]
    commands.sort(key=operator.itemgetter(1))
    return [(c, t, ind) for ind, (c, t) in enumerate(commands)]


def _curr_session_parser(hist=None):
    """
    Take in History object and return command list tuple with
    format: (name, start_time, index)
    """
    if hist is None:
        hist = builtins.__xonsh_history__
    if not hist:
        return None
    start_times = [start for start, end in hist.tss]
    names = [name[:-1] if name.endswith('\n') else name
             for name in hist.inps]
    commands = enumerate(zip(names, start_times))
    return [(c, t, ind) for ind, (c, t) in commands]


def _zsh_hist_parser(location=None):
    default_location = os.path.join('~', '.zsh_history')
    location_list = [os.path.join('~', '.zshrc'),
                     os.path.join('~', '.zprofile')]
    if location is None:
        location = _find_histfile_var(location_list, default_location)
    z_hist_formatted = []
    if os.path.isfile(location):
        with open(location, 'r', errors='backslashreplace') as z_file:
            z_txt = z_file.read()
            z_hist = z_txt.splitlines()
            if z_hist:
                for ind, line in enumerate(z_hist):
                    try:
                        start_time, command = line.split(';', 1)
                    except ValueError:
                        # Invalid history entry
                        continue
                    try:
                        start_time = float(start_time.split(':')[1])
                    except ValueError:
                        start_time = -1
                    z_hist_formatted.append((command, start_time, ind))
                return z_hist_formatted

    else:
        print("No zsh history file found at: {}".format(location),
              file=sys.stderr)


def _bash_hist_parser(location=None):
    default_location = os.path.join('~', '.bash_history')
    location_list = [os.path.join('~', '.bashrc'),
                     os.path.join('~', '.bash_profile')]
    if location is None:
        location = _find_histfile_var(location_list, default_location)
    bash_hist_formatted = []
    if os.path.isfile(location):
        with open(location, 'r', errors='backslashreplace') as bash_file:
            b_txt = bash_file.read()
            bash_hist = b_txt.splitlines()
            if bash_hist:
                for ind, command in enumerate(bash_hist):
                    bash_hist_formatted.append((command, 0.0, ind))
                return bash_hist_formatted
    else:
        import ipdb
        ipdb.set_trace()
        print("No bash history file found at: {}".format(location),
              file=sys.stderr)


@functools.lru_cache()
def _hist_create_parser():
    """Create a parser for the "history" command."""
    p = argparse.ArgumentParser(prog='history',
                                description='Tools for dealing with history')
    subp = p.add_subparsers(title='action', dest='action')
    # session action
    show = subp.add_parser('show', aliases=['session'],
                           help='displays session history, default action')
    show.add_argument('-r', dest='reverse', default=False,
                      action='store_true',
                      help='reverses the direction')
    show.add_argument('n', nargs='?', default=None,
                      help='display n\'th history entry if n is a simple '
                           'int, or range of entries if it is Python '
                           'slice notation')
    # all action
    xonsh = subp.add_parser('xonsh', aliases=['all'],
                            help='displays history from all sessions')
    xonsh.add_argument('-r', dest='reverse', default=False,
                       action='store_true',
                       help='reverses the direction')
    xonsh.add_argument('n', nargs='?', default=None,
                       help='display n\'th history entry if n is a '
                            'simple int, or range of entries if it '
                            'is Python slice notation')
    # zsh action
    zsh = subp.add_parser('zsh', help='displays history from zsh sessions')
    zsh.add_argument('-r', dest='reverse', default=False,
                     action='store_true',
                     help='reverses the direction')
    zsh.add_argument('n', nargs='?', default=None,
                     help='display n\'th history entry if n is a '
                     'simple int, or range of entries if it '
                     'is Python slice notation')
    # bash action
    bash = subp.add_parser('bash', help='displays history from bash sessions')
    bash.add_argument('-r', dest='reverse', default=False,
                      action='store_true',
                      help='reverses the direction')
    bash.add_argument('n', nargs='?', default=None,
                      help='display n\'th history entry if n is a '
                      'simple int, or range of entries if it '
                      'is Python slice notation')
    # 'id' subcommand
    subp.add_parser('id', help='displays the current session id')
    # 'file' subcommand
    subp.add_parser('file', help='displays the current history filename')
    # 'info' subcommand
    info = subp.add_parser('info', help=('displays information about the '
                                         'current history'))
    info.add_argument('--json', dest='json', default=False,
                      action='store_true', help='print in JSON format')
    # diff
    diff = subp.add_parser('diff', help='diffs two xonsh history files')
    _dh_create_parser(p=diff)
    # replay, dynamically
    from xonsh import replay
    rp = subp.add_parser('replay', help='replays a xonsh history file')
    replay._rp_create_parser(p=rp)
    _HIST_MAIN_ACTIONS['replay'] = replay._rp_main_action
    # gc
    gcp = subp.add_parser(
        'gc', help='launches a new history garbage collector')
    gcp.add_argument('--size', nargs=2, dest='size', default=None,
                     help=('next two arguments represent the history size and '
                           'units; e.g. "--size 8128 commands"'))
    bgcp = gcp.add_mutually_exclusive_group()
    bgcp.add_argument('--blocking', dest='blocking', default=True,
                      action='store_true',
                      help=('ensures that the gc blocks the main thread, '
                            'default True'))
    bgcp.add_argument('--non-blocking', dest='blocking', action='store_false',
                      help='makes the gc non-blocking, and thus return sooner')
    return p


def _show(ns=None, hist=None, start_index=None, end_index=None,
          start_time=None, end_time=None, location=None):
    """
    Show the requested portion of shell history.
    Accepts multiple history sources (xonsh, bash, zsh)

    May be invoked as an alias with `history all/bash/zsh` which will
    provide history as stdout or with `__xonsh_history__.show()`
    which will return the history as a list with each item
    in the tuple form (name, start_time, index).

    If invoked via __xonsh_history__.show() then the ns parameter
    can be supplied as a str with the follow options:
        `session` - returns xonsh history from current session
        `all`     - returns xonsh history from all sessions
        `zsh`     - returns all zsh history
        `bash`    - returns all bash history
    """
    # Check if ns is a string, meaning it was invoked from
    # __xonsh_history__
    alias = True
    valid_formats = {'session': functools.partial(_curr_session_parser, hist),
                     'show': functools.partial(_curr_session_parser, hist),
                     'all': _all_xonsh_parser,
                     'xonsh': _all_xonsh_parser,
                     'zsh': functools.partial(_zsh_hist_parser, location),
                     'bash': functools.partial(_bash_hist_parser, location)}
    if isinstance(ns, str) and ns in valid_formats.keys():
        ns = _hist_create_parser().parse_args([ns])
        alias = False
    if not ns:
        ns = _hist_create_parser().parse_args(['all'])
        alias = False
    try:
        commands = valid_formats[ns.action]()
    except KeyError:
        print("{} is not a valid history format".format(ns.action))
        return None
    if not commands:
        return None
    if start_time:
        if isinstance(start_time, datetime.datetime):
            start_time = start_time.timestamp()
        if isinstance(start_time, float):
            commands = [c for c in commands if c[1] >= start_time]
        else:
            print("Invalid start time, must be float or datetime.")
    if end_time:
        if isinstance(end_time, datetime.datetime):
            end_time = end_time.timestamp()
        if isinstance(end_time, float):
            commands = [c for c in commands if c[1] <= end_time]
        else:
            print("Invalid end time, must be float or datetime.")
    idx = None
    if ns:
        idx = ensure_int_or_slice(ns.n)
        if idx is False:
            print("{} is not a valid input.".format(ns.n),
                  file=sys.stderr)
            return
        elif isinstance(idx, int):
            try:
                commands = [commands[idx]]
            except IndexError:
                err = "Index likely not in range. Only {} commands."
                print(err.format(len(commands)))
                return
    else:
        idx = slice(start_index, end_index)

    if (isinstance(idx, slice) and
            start_time is None and end_time is None):
        commands = commands[idx]

    if ns and ns.reverse:
        commands = list(reversed(commands))

    if commands:
        digits = len(str(max([i for c, t, i in commands])))
        if alias:
            for c, t, i in commands:
                for line_ind, line in enumerate(c.split('\n')):
                    if line_ind == 0:
                        print('{:>{width}}: {}'.format(i, line,
                                                       width=digits + 1))
                    else:
                        print(' {:>>{width}} {}'.format('', line,
                                                        width=digits + 1))
        else:
            return commands


#
# Interface to History
#
class History(object):
    """Xonsh session history."""

    def __init__(self, filename=None, sessionid=None, buffersize=100, gc=True,
                 **meta):
        """Represents a xonsh session's history as an in-memory buffer that is
        periodically flushed to disk.

        Parameters
        ----------
        filename : str, optional
            Location of history file, defaults to
            ``$XONSH_DATA_DIR/xonsh-{sessionid}.json``.
        sessionid : int, uuid, str, optional
            Current session identifier, will generate a new sessionid if not
            set.
        buffersize : int, optional
            Maximum buffersize in memory.
        meta : optional
            Top-level metadata to store along with the history. The kwargs
            'cmds' and 'sessionid' are not allowed and will be overwritten.
        gc : bool, optional
            Run garbage collector flag.
        """
        self.sessionid = sid = uuid.uuid4() if sessionid is None else sessionid
        if filename is None:
            # pylint: disable=no-member
            data_dir = builtins.__xonsh_env__.get('XONSH_DATA_DIR')
            data_dir = os.path.expanduser(data_dir)
            self.filename = os.path.join(
                data_dir, 'xonsh-{0}.json'.format(sid))
        else:
            self.filename = filename
        self.buffer = []
        self.buffersize = buffersize
        self._queue = deque()
        self._cond = Condition()
        self._len = 0
        self.last_cmd_out = None
        self.last_cmd_rtn = None
        meta['cmds'] = []
        meta['sessionid'] = str(sid)
        with open(self.filename, 'w', newline='\n') as f:
            ljdump(meta, f, sort_keys=True)
        self.gc = HistoryGC() if gc else None
        # command fields that are known
        self.tss = CommandField('ts', self)
        self.inps = CommandField('inp', self)
        self.outs = CommandField('out', self)
        self.rtns = CommandField('rtn', self)

    def __len__(self):
        return self._len

    def append(self, cmd):
        """Appends command to history. Will periodically flush the history to file.

        Parameters
        ----------
        cmd : dict
            Command dictionary that should be added to the ordered history.

        Returns
        -------
        hf : HistoryFlusher or None
            The thread that was spawned to flush history
        """
        opts = builtins.__xonsh_env__.get('HISTCONTROL')
        if ('ignoredups' in opts and len(self) > 0 and
                cmd['inp'] == self.inps[-1]):
            # Skipping dup cmd
            return None
        elif 'ignoreerr' in opts and cmd['rtn'] != 0:
            # Skipping failed cmd
            return None

        self.buffer.append(cmd)
        self._len += 1  # must come before flushing
        if len(self.buffer) >= self.buffersize:
            hf = self.flush()
        else:
            hf = None
        return hf

    def flush(self, at_exit=False):
        """Flushes the current command buffer to disk.

        Parameters
        ----------
        at_exit : bool, optional
            Whether the HistoryFlusher should act as a thread in the
            background, or execute immeadiately and block.

        Returns
        -------
        hf : HistoryFlusher or None
            The thread that was spawned to flush history
        """
        if len(self.buffer) == 0:
            return
        hf = HistoryFlusher(self.filename, tuple(self.buffer), self._queue,
                            self._cond, at_exit=at_exit)
        self.buffer.clear()
        return hf

    def show(self, *args, **kwargs):
        """
        Returns shell history as a list

        Valid options:
            `session` - returns xonsh history from current session
            `show`    - alias of `session`
            `all`     - returns xonsh history from all sessions
            `xonsh`   - alias of `all`
            `zsh`     - returns all zsh history
            `bash`    - returns all bash history
        """
        return _show(*args, **kwargs)


def _info(ns, hist):
    """Display information about the shell history."""
    data = OrderedDict()
    data['sessionid'] = str(hist.sessionid)
    data['filename'] = hist.filename
    data['length'] = len(hist)
    data['buffersize'] = hist.buffersize
    data['bufferlength'] = len(hist.buffer)
    if ns.json:
        import json
        s = json.dumps(data)
        print(s)
    else:
        lines = ['{0}: {1}'.format(k, v) for k, v in data.items()]
        print('\n'.join(lines))


def _gc(ns, hist):
    """Start and monitor garbage collection of the shell history."""
    hist.gc = gc = HistoryGC(wait_for_shell=False, size=ns.size)
    if ns.blocking:
        while gc.is_alive():
            continue


_HIST_MAIN_ACTIONS = {
    'show': _show,
    'xonsh': _show,
    'zsh': _show,
    'bash': _show,
    'session': _show,
    'all': _show,
    'id': lambda ns, hist: print(hist.sessionid),
    'file': lambda ns, hist: print(hist.filename),
    'info': _info,
    'diff': _dh_main_action,
    'gc': _gc,
    }


def _hist_main(hist, args):
    """This implements the history CLI."""
    if not args or args[0] in ['-r'] or ensure_int_or_slice(args[0]):
        args.insert(0, 'show')
    elif args[0] not in list(_HIST_MAIN_ACTIONS) + ['-h', '--help']:
        print("{} is not a valid input.".format(args[0]),
              file=sys.stderr)
        return
    if (args[0] in ['show', 'xonsh', 'zsh', 'bash', 'session', 'all'] and
        len(args) > 1 and args[-1].startswith('-') and
            args[-1][1].isdigit()):
        args.insert(-1, '--')  # ensure parsing stops before a negative int
    ns = _hist_create_parser().parse_args(args)
    if ns.action is None:  # apply default action
        ns = _hist_create_parser().parse_args(['show'] + args)
    _HIST_MAIN_ACTIONS[ns.action](ns, hist)


def history_main(args=None, stdin=None):
    """This is the history command entry point."""
    _ = stdin
    _hist_main(builtins.__xonsh_history__, args)  # pylint: disable=no-member

#
# base_shell
#
# -*- coding: utf-8 -*-
"""The base class for xonsh shell"""
# amalgamated io
# amalgamated os
# amalgamated sys
# amalgamated time
# amalgamated builtins
# amalgamated xonsh.tools
# amalgamated xonsh.platform
# amalgamated xonsh.codecache
# amalgamated xonsh.completer
# amalgamated xonsh.environ
class _TeeOut(object):
    """Tees stdout into the original sys.stdout and another buffer."""

    def __init__(self, buf):
        self.buffer = buf
        self.stdout = sys.stdout
        self.encoding = self.stdout.encoding
        sys.stdout = self

    def __del__(self):
        sys.stdout = self.stdout

    def close(self):
        """Restores the original stdout."""
        sys.stdout = self.stdout

    def write(self, data):
        """Writes data to the original stdout and the buffer."""
        #data = data.replace('\001', '').replace('\002', '')
        self.stdout.write(data)
        self.buffer.write(data)

    def flush(self):
        """Flushes both the original stdout and the buffer."""
        self.stdout.flush()
        self.buffer.flush()

    def fileno(self):
        """Tunnel fileno() calls."""
        return self.stdout.fileno()


class _TeeErr(object):
    """Tees stderr into the original sys.stdout and another buffer."""

    def __init__(self, buf):
        self.buffer = buf
        self.stderr = sys.stderr
        self.encoding = self.stderr.encoding
        sys.stderr = self

    def __del__(self):
        sys.stderr = self.stderr

    def close(self):
        """Restores the original stderr."""
        sys.stderr = self.stderr

    def write(self, data):
        """Writes data to the original stderr and the buffer."""
        #data = data.replace('\001', '').replace('\002', '')
        self.stderr.write(data)
        self.buffer.write(data)

    def flush(self):
        """Flushes both the original stderr and the buffer."""
        self.stderr.flush()
        self.buffer.flush()

    def fileno(self):
        """Tunnel fileno() calls."""
        return self.stderr.fileno()


class Tee(io.StringIO):
    """Class that merges tee'd stdout and stderr into a single buffer.

    This represents what a user would actually see on the command line.
    """
    # pylint is a stupid about counting public methods when using inheritance.
    # pylint: disable=too-few-public-methods

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stdout = _TeeOut(self)
        self.stderr = _TeeErr(self)

    def __del__(self):
        del self.stdout, self.stderr
        super().__del__()

    def close(self):
        """Closes the buffer as well as the stdout and stderr tees."""
        self.stdout.close()
        self.stderr.close()
        super().close()


class BaseShell(object):
    """The xonsh shell."""

    def __init__(self, execer, ctx, **kwargs):
        super().__init__()
        self.execer = execer
        self.ctx = ctx
        self.completer = Completer() if kwargs.get('completer', True) else None
        self.buffer = []
        self.need_more_lines = False
        self.mlprompt = None
        self._styler = DefaultNotGiven

    @property
    def styler(self):
        if self._styler is DefaultNotGiven:
            if HAS_PYGMENTS:
                from xonsh.pyghooks import XonshStyle
                env = builtins.__xonsh_env__
                self._styler = XonshStyle(env.get('XONSH_COLOR_STYLE'))
            else:
                self._styler = None
        return self._styler

    @styler.setter
    def styler(self, value):
        self._styler = value

    @styler.deleter
    def styler(self):
        self._styler = DefaultNotGiven

    def emptyline(self):
        """Called when an empty line has been entered."""
        self.need_more_lines = False
        self.default('')

    def singleline(self, **kwargs):
        """Reads a single line of input from the shell."""
        msg = '{0} has not implemented singleline().'
        raise RuntimeError(msg.format(self.__class__.__name__))

    def precmd(self, line):
        """Called just before execution of line."""
        return line if self.need_more_lines else line.lstrip()

    def default(self, line):
        """Implements code execution."""
        line = line if line.endswith('\n') else line + '\n'
        src, code = self.push(line)
        if code is None:
            return
        hist = builtins.__xonsh_history__  # pylint: disable=no-member
        ts1 = None
        store_stdout = builtins.__xonsh_env__.get('XONSH_STORE_STDOUT')  # pylint: disable=no-member
        tee = Tee() if store_stdout else io.StringIO()
        try:
            ts0 = time.time()
            run_compiled_code(code, self.ctx, None, 'single')
            ts1 = time.time()
            if hist.last_cmd_rtn is None:
                hist.last_cmd_rtn = 0  # returncode for success
        except XonshError as e:
            print(e.args[0], file=sys.stderr)
            if hist.last_cmd_rtn is None:
                hist.last_cmd_rtn = 1  # return code for failure
        except Exception:  # pylint: disable=broad-except
            print_exception()
            if hist.last_cmd_rtn is None:
                hist.last_cmd_rtn = 1  # return code for failure
        finally:
            ts1 = ts1 or time.time()
            self._append_history(inp=src, ts=[ts0, ts1], tee_out=tee.getvalue())
            tee.close()
        if builtins.__xonsh_exit__:  # pylint: disable=no-member
            return True

    def push(self, line):
        """Pushes a line onto the buffer and compiles the code in a way that
        enables multiline input.
        """
        code = None
        self.buffer.append(line)
        if self.need_more_lines:
            return None, code
        src = ''.join(self.buffer)
        _cache = should_use_cache(self.execer, 'single')
        if _cache:
            codefname = code_cache_name(src)
            cachefname = get_cache_filename(codefname, code=True)
            usecache, code = code_cache_check(cachefname)
            if usecache:
                self.reset_buffer()
                return src, code
        try:
            code = self.execer.compile(src,
                                       mode='single',
                                       glbs=self.ctx,
                                       locs=None)
            if _cache:
                update_cache(code, cachefname)
            self.reset_buffer()
        except SyntaxError:
            if line == '\n':
                self.reset_buffer()
                print_exception()
                return src, None
            self.need_more_lines = True
        except Exception:  # pylint: disable=broad-except
            self.reset_buffer()
            print_exception()
            return src, None
        return src, code

    def reset_buffer(self):
        """Resets the line buffer."""
        self.buffer.clear()
        self.need_more_lines = False
        self.mlprompt = None

    def settitle(self):
        """Sets terminal title."""
        _ = self
        env = builtins.__xonsh_env__  # pylint: disable=no-member
        term = env.get('TERM', None)
        # Shells running in emacs sets TERM to "dumb" or "eterm-color".
        # Do not set title for these to avoid garbled prompt.
        if term is None or term in ['dumb', 'eterm-color', 'linux']:
            return
        t = env.get('TITLE')
        if t is None:
            return
        t = format_prompt(t)
        if ON_WINDOWS and 'ANSICON' not in env:
            t = escape_windows_cmd_string(t)
            os.system('title {}'.format(t))
        else:
            os.write(1, "\x1b]2;{0}\x07".format(t).encode())

    @property
    def prompt(self):
        """Obtains the current prompt string."""
        if self.need_more_lines:
            if self.mlprompt is None:
                try:
                    self.mlprompt = multiline_prompt()
                except Exception:  # pylint: disable=broad-except
                    print_exception()
                    self.mlprompt = '<multiline prompt error> '
            return self.mlprompt
        env = builtins.__xonsh_env__  # pylint: disable=no-member
        p = env.get('PROMPT')
        try:
            p = partial_format_prompt(p)
        except Exception:  # pylint: disable=broad-except
            print_exception()
        self.settitle()
        return p

    def _append_history(self, tee_out=None, **info):
        """Append information about the command to the history."""
        _ = self
        hist = builtins.__xonsh_history__  # pylint: disable=no-member
        info['rtn'] = hist.last_cmd_rtn
        tee_out = tee_out or None
        last_out = hist.last_cmd_out or None
        if last_out is None and tee_out is None:
            pass
        elif last_out is None and tee_out is not None:
            info['out'] = tee_out
        elif last_out is not None and tee_out is None:
            info['out'] = last_out
        else:
            info['out'] = tee_out + '\n' + last_out
        hist.append(info)
        hist.last_cmd_rtn = hist.last_cmd_out = None

    def format_color(self, string, **kwargs):
        """Formats the colors in a string. This base implmentation does not
        actually do any coloring, but just returns the string directly.
        """
        return string

    def print_color(self, string, **kwargs):
        """Prints a string in color. This base implmentation does not actually
        do any coloring, but just prints the string directly.
        """
        if not isinstance(string, str):
            string = ''.join([x for _, x in string])
        print(string, **kwargs)

    def color_style_names(self):
        """Returns an iterable of all available style names."""
        return ()

    def color_style(self):
        """Returns the current color map."""
        return {}

#
# replay
#
# -*- coding: utf-8 -*-
"""Tools to replay xonsh history files."""
# amalgamated time
# amalgamated builtins
# amalgamated from collections.abc import Mapping
# amalgamated xonsh.tools
# amalgamated xonsh.lazyjson
# amalgamated xonsh.environ
# amalgamated xonsh.history
# amalgamated xonsh.history
DEFAULT_MERGE_ENVS = ('replay', 'native')


class Replayer(object):
    """Replays a xonsh history file."""

    def __init__(self, f, reopen=True):
        """
        Parameters
        ----------
        f : file handle or str
            Path to xonsh history file.
        reopen : bool, optional
            Whether new file handle should be opened for each load, passed directly into
            LazyJSON class.
        """
        self._lj = LazyJSON(f, reopen=reopen)

    def __del__(self):
        self._lj.close()

    def replay(self, merge_envs=DEFAULT_MERGE_ENVS, target=None):
        """Replays the history specified, returns the history object where the code
        was executed.

        Parameters
        ----------
        merge_env : tuple of str or Mappings, optional
            Describes how to merge the environments, in order of increasing precednce.
            Available strings are 'replay' and 'native'. The 'replay' env comes from the
            history file that we are replaying. The 'native' env comes from what this
            instance of xonsh was started up with. Instead of a string, a dict or other
            mapping may be passed in as well. Defaults to ('replay', 'native').
        target : str, optional
            Path to new history file.
        """
        shell = builtins.__xonsh_shell__
        re_env = self._lj['env'].load()
        new_env = self._merge_envs(merge_envs, re_env)
        new_hist = History(env=new_env.detype(), locked=True, ts=[time.time(), None],
                           gc=False, filename=target)
        with swap(builtins, '__xonsh_env__', new_env), \
             swap(builtins, '__xonsh_history__', new_hist):
            for cmd in self._lj['cmds']:
                inp = cmd['inp']
                shell.default(inp)
                if builtins.__xonsh_exit__:  # prevent premature exit
                    builtins.__xonsh_exit__ = False
        new_hist.flush(at_exit=True)
        return new_hist

    def _merge_envs(self, merge_envs, re_env):
        new_env = {}
        for e in merge_envs:
            if e == 'replay':
                new_env.update(re_env)
            elif e == 'native':
                new_env.update(builtins.__xonsh_env__)
            elif isinstance(e, Mapping):
                new_env.update(e)
            else:
                raise TypeError('Type of env not understood: {0!r}'.format(e))
        new_env = Env(**new_env)
        return new_env


_REPLAY_PARSER = None

def _rp_create_parser(p=None):
    global _REPLAY_PARSER
    p_was_none = (p is None)
    if _REPLAY_PARSER is not None and p_was_none:
        return _REPLAY_PARSER
    if p_was_none:
        from argparse import ArgumentParser
        p = ArgumentParser('replay', description='replays a xonsh history file')
    p.add_argument('--merge-envs', dest='merge_envs', default=DEFAULT_MERGE_ENVS,
                   nargs='+',
                   help="Describes how to merge the environments, in order of "
                        "increasing precedence. Available strings are 'replay' and "
                        "'native'. The 'replay' env comes from the history file that we "
                        "are replaying. The 'native' env comes from what this instance "
                        "of xonsh was started up with. One or more of these options may "
                        "be passed in. Defaults to '--merge-envs replay native'.")
    p.add_argument('--json', dest='json', default=False, action='store_true',
                   help='print history info in JSON format')
    p.add_argument('-o', '--target', dest='target', default=None,
                   help='path to new history file')
    p.add_argument('path', help='path to replay history file')
    if p_was_none:
        _REPLAY_PARSER = p
    return p


def _rp_main_action(ns, h=None):
    replayer = Replayer(ns.path)
    hist = replayer.replay(merge_envs=ns.merge_envs, target=ns.target)
    print('----------------------------------------------------------------')
    print('Just replayed history, new history has the following information')
    print('----------------------------------------------------------------')
    history_info(ns, hist)


def replay_main(args, stdin=None):
    """Acts as main function for replaying a xonsh history file."""
    parser = _rp_create_parser()
    ns = parser.parse_args(args)
    _rp_main_action(ns)

#
# tracer
#
"""Implements a xonsh tracer."""
# amalgamated os
# amalgamated re
# amalgamated sys
# amalgamated inspect
# amalgamated linecache
# amalgamated importlib
# amalgamated from functools import lru_cache
# amalgamated from argparse import ArgumentParser
# amalgamated xonsh.lazyasd
# amalgamated xonsh.platform
# amalgamated xonsh.tools
# amalgamated xonsh.inspectors
# amalgamated xonsh.environ
pygments = LazyObject(lambda: importlib.import_module('pygments'),
                      globals(), 'pygments')
terminal = LazyObject(lambda: importlib.import_module(
                                'pygments.formatters.terminal'),
                      globals(), 'terminal')
pyghooks = LazyObject(lambda: importlib.import_module('xonsh.pyghooks'),
                      globals(), 'pyghooks')

class TracerType(object):
    """Represents a xonsh tracer object, which keeps track of all tracing
    state. This is a singleton.
    """
    _inst = None
    valid_events = frozenset(['line', 'call'])

    def __new__(cls, *args, **kwargs):
        if cls._inst is None:
            cls._inst = super(TracerType, cls).__new__(cls, *args, **kwargs)
        return cls._inst

    def __init__(self):
        self.prev_tracer = DefaultNotGiven
        self.files = set()
        self.usecolor = True
        self.lexer = pyghooks.XonshLexer()
        self.formatter = terminal.TerminalFormatter()
        self._last = ('', -1)  # filename, lineno tuple

    def __del__(self):
        for f in set(self.files):
            self.stop(f)

    def start(self, filename):
        """Starts tracing a file."""
        files = self.files
        if len(files) == 0:
            self.prev_tracer = sys.gettrace()
        files.add(normabspath(filename))
        sys.settrace(self.trace)
        curr = inspect.currentframe()
        for frame, fname, *_ in getouterframes(curr, context=0):
            if normabspath(fname) in files:
                frame.f_trace = self.trace

    def stop(self, filename):
        """Stops tracing a file."""
        filename = normabspath(filename)
        self.files.discard(filename)
        if len(self.files) == 0:
            sys.settrace(self.prev_tracer)
            curr = inspect.currentframe()
            for frame, fname, *_ in getouterframes(curr, context=0):
                if normabspath(fname) == filename:
                    frame.f_trace = self.prev_tracer
            self.prev_tracer = DefaultNotGiven

    def trace(self, frame, event, arg):
        """Implements a line tracing function."""
        if event not in self.valid_events:
            return self.trace
        fname = find_file(frame)
        if fname in self.files:
            lineno = frame.f_lineno
            curr = (fname, lineno)
            if curr != self._last:
                line = linecache.getline(fname, lineno).rstrip()
                s = tracer_format_line(fname, lineno, line,
                                       color=self.usecolor,
                                       lexer=self.lexer,
                                       formatter=self.formatter)
                print_color(s)
                self._last = curr
        return self.trace


tracer = LazyObject(TracerType, globals(), 'tracer')

COLORLESS_LINE = '{fname}:{lineno}:{line}'
COLOR_LINE = ('{{PURPLE}}{fname}{{BLUE}}:'
              '{{GREEN}}{lineno}{{BLUE}}:'
              '{{NO_COLOR}}')


def tracer_format_line(fname, lineno, line, color=True, lexer=None, formatter=None):
    """Formats a trace line suitable for printing."""
    fname = min(fname, _replace_home(fname), os.path.relpath(fname), key=len)
    if not color:
        return COLORLESS_LINE.format(fname=fname, lineno=lineno, line=line)
    cline = COLOR_LINE.format(fname=fname, lineno=lineno)
    if not HAS_PYGMENTS:
        return cline + line
    # OK, so we have pygments
    tokens = pyghooks.partial_color_tokenize(cline)
    lexer = lexer or pyghooks.XonshLexer()
    tokens += pygments.lex(line, lexer=lexer)
    return tokens


#
# Command line interface
#

def _find_caller(args):
    """Somewhat hacky method of finding the __file__ based on the line executed."""
    re_line = re.compile(r'[^;\s|&<>]+\s+' + r'\s+'.join(args))
    curr = inspect.currentframe()
    for _, fname, lineno, _, lines, _ in getouterframes(curr, context=1)[3:]:
        if lines is not None and re_line.search(lines[0]) is not None:
            return fname
        elif lineno == 1 and re_line.search(linecache.getline(fname, lineno)) is not None:
            # There is a bug in CPython such that getouterframes(curr, context=1)
            # will actually return the 2nd line in the code_context field, even though
            # line number is itself correct. We manually fix that in this branch.
            return fname
    else:
        msg = ('xonsh: warning: __file__ name could not be found. You may be '
               'trying to trace interactively. Please pass in the file names '
               'you want to trace explicitly.')
        print(msg, file=sys.stderr)


def _on(ns, args):
    """Turns on tracing for files."""
    for f in ns.files:
        if f == '__file__':
            f = _find_caller(args)
        if f is None:
            continue
        tracer.start(f)


def _off(ns, args):
    """Turns off tracing for files."""
    for f in ns.files:
        if f == '__file__':
            f = _find_caller(args)
        if f is None:
            continue
        tracer.stop(f)


def _color(ns, args):
    """Manages color action for tracer CLI."""
    tracer.usecolor = ns.toggle


@lru_cache(1)
def _tracer_create_parser():
    """Creates tracer argument parser"""
    p = ArgumentParser(prog='trace',
                       description='tool for tracing xonsh code as it runs.')
    subp = p.add_subparsers(title='action', dest='action')
    onp = subp.add_parser('on', aliases=['start', 'add'],
                          help='begins tracing selected files.')
    onp.add_argument('files', nargs='*', default=['__file__'],
                     help=('file paths to watch, use "__file__" (default) to select '
                           'the current file.'))
    off = subp.add_parser('off', aliases=['stop', 'del', 'rm'],
                          help='removes selected files fom tracing.')
    off.add_argument('files', nargs='*', default=['__file__'],
                     help=('file paths to stop watching, use "__file__" (default) to '
                           'select the current file.'))
    col = subp.add_parser('color', help='output color management for tracer.')
    col.add_argument('toggle', type=to_bool,
                     help='true/false, y/n, etc. to toggle color usage.')
    return p


_TRACER_MAIN_ACTIONS = {
    'on': _on,
    'add': _on,
    'start': _on,
    'rm': _off,
    'off': _off,
    'del': _off,
    'stop': _off,
    'color': _color,
    }


def tracermain(args=None):
    """Main function for tracer command-line interface."""
    parser = _tracer_create_parser()
    ns = parser.parse_args(args)
    return _TRACER_MAIN_ACTIONS[ns.action](ns, args)


if __name__ == '__main__':
    tracermain()

#
# xonfig
#
"""The xonsh configuration (xonfig) utility."""
ast = _LazyModule.load('ast', 'ast')
# amalgamated json
# amalgamated shutil
# amalgamated textwrap
# amalgamated builtins
# amalgamated functools
# amalgamated itertools
# amalgamated from pprint import pformat
# amalgamated from argparse import ArgumentParser
# amalgamated from contextlib import contextmanager
try:
    import ply
except ImportError:
    from xonsh import ply

wiz = _LazyModule.load('xonsh', 'xonsh.wizard', 'wiz')
from xonsh import __version__ as XONSH_VERSION
# amalgamated xonsh.environ
# amalgamated xonsh.platform
# amalgamated xonsh.tools
# amalgamated xonsh.xontribs
HR = "'`-.,_,.-*'`-.,_,.-*'`-.,_,.-*'`-.,_,.-*'`-.,_,.-*'`-.,_,.-*'`-.,_,.-*'"
WIZARD_HEAD = """
          {{BOLD_WHITE}}Welcome to the xonsh configuration wizard!{{NO_COLOR}}
          {{YELLOW}}------------------------------------------{{NO_COLOR}}
This will present a guided tour through setting up the xonsh static
config file. Xonsh will automatically ask you if you want to run this
wizard if the configuration file does not exist. However, you can
always rerun this wizard with the xonfig command:

    $ xonfig wizard

This wizard will load an existing configuration, if it is available.
Also never fear when this wizard saves its results! It will create
a backup of any existing configuration automatically.

This wizard has two main phases: foreign shell setup and environment
variable setup. Each phase may be skipped in its entirety.

For the configuration to take effect, you will need to restart xonsh.

{hr}
""".format(hr=HR)

WIZARD_FS = """
{hr}

                      {{BOLD_WHITE}}Foreign Shell Setup{{NO_COLOR}}
                      {{YELLOW}}-------------------{{NO_COLOR}}
The xonsh shell has the ability to interface with foreign shells such
as Bash, zsh, or fish.

For configuration, this means that xonsh can load the environment,
aliases, and functions specified in the config files of these shells.
Naturally, these shells must be available on the system to work.
Being able to share configuration (and source) from foreign shells
makes it easier to transition to and from xonsh.
""".format(hr=HR)

WIZARD_ENV = """
{hr}

                  {{BOLD_WHITE}}Environment Variable Setup{{NO_COLOR}}
                  {{YELLOW}}--------------------------{{NO_COLOR}}
The xonsh shell also allows you to setup environment variables from
the static configuration file. Any variables set in this way are
superceded by the definitions in the xonshrc or on the command line.
Still, setting environment variables in this way can help define
options that are global to the system or user.

The following lists the environment variable name, its documentation,
the default value, and the current value. The default and current
values are presented as pretty repr strings of their Python types.

{{BOLD_GREEN}}Note:{{NO_COLOR}} Simply hitting enter for any environment variable
will accept the default value for that entry.
""".format(hr=HR)

WIZARD_ENV_QUESTION = "Would you like to set env vars now, " + wiz.YN

WIZARD_XONTRIB = """
{hr}

                           {{BOLD_WHITE}}Xontribs{{NO_COLOR}}
                           {{YELLOW}}--------{{NO_COLOR}}
No shell is complete without extensions, and xonsh is no exception. Xonsh
extensions are called {{BOLD_GREEN}}xontribs{{NO_COLOR}}, or xonsh contributions.
Xontribs are dynamically loadable, either by importing them directly or by
using the 'xontrib' command. However, you can also configure xonsh to load
xontribs automatically on startup prior to loading the run control files.
This allows the xontrib to be used immediately in your xonshrc files.

The following describes all xontribs that have been registered with xonsh.
These come from users, 3rd party developers, or xonsh itself!
""".format(hr=HR)

WIZARD_XONTRIB_QUESTION = "Would you like to enable xontribs now, " + wiz.YN


WIZARD_TAIL = """
Thanks for using the xonsh configuration wizard!"""



def make_fs_wiz():
    """Makes the foreign shell part of the wizard."""
    cond = wiz.create_truefalse_cond(prompt='Add a new foreign shell, ' + wiz.YN)
    fs = wiz.While(cond=cond, body=[
        wiz.Input('shell name (e.g. bash): ',
                  path='/foreign_shells/{idx}/shell'),
        wiz.StoreNonEmpty('interactive shell [bool, default=True]: ',
                          converter=to_bool,
                          show_conversion=True,
                          path='/foreign_shells/{idx}/interactive'),
        wiz.StoreNonEmpty('login shell [bool, default=False]: ',
                          converter=to_bool,
                          show_conversion=True,
                          path='/foreign_shells/{idx}/login'),
        wiz.StoreNonEmpty("env command [str, default='env']: ",
                          path='/foreign_shells/{idx}/envcmd'),
        wiz.StoreNonEmpty("alias command [str, default='alias']: ",
                          path='/foreign_shells/{idx}/aliascmd'),
        wiz.StoreNonEmpty(("extra command line arguments [list of str, "
                           "default=[]]: "),
                          converter=ast.literal_eval,
                          show_conversion=True,
                          path='/foreign_shells/{idx}/extra_args'),
        wiz.StoreNonEmpty('current environment [dict, default=None]: ',
                          converter=ast.literal_eval,
                          show_conversion=True,
                          path='/foreign_shells/{idx}/currenv'),
        wiz.StoreNonEmpty('safely handle exceptions [bool, default=True]: ',
                          converter=to_bool,
                          show_conversion=True,
                          path='/foreign_shells/{idx}/safe'),
        wiz.StoreNonEmpty("pre-command [str, default='']: ",
                          path='/foreign_shells/{idx}/prevcmd'),
        wiz.StoreNonEmpty("post-command [str, default='']: ",
                          path='/foreign_shells/{idx}/postcmd'),
        wiz.StoreNonEmpty("foreign function command [str, default=None]: ",
                          path='/foreign_shells/{idx}/funcscmd'),
        wiz.StoreNonEmpty("source command [str, default=None]: ",
                          path='/foreign_shells/{idx}/sourcer'),
        wiz.Message(message='Foreign shell added.\n')
        ])
    return fs


def _wrap_paragraphs(text, width=70, **kwargs):
    """Wraps paragraphs instead."""
    pars = text.split('\n')
    pars = ['\n'.join(textwrap.wrap(p, width=width, **kwargs)) for p in pars]
    s = '\n'.join(pars)
    return s

ENVVAR_MESSAGE = """
{{BOLD_CYAN}}${name}{{NO_COLOR}}
{docstr}
{{RED}}default value:{{NO_COLOR}} {default}
{{RED}}current value:{{NO_COLOR}} {current}"""

ENVVAR_PROMPT = "{BOLD_GREEN}>>>{NO_COLOR} "

def make_envvar(name):
    """Makes a StoreNonEmpty node for an environment variable."""
    env = builtins.__xonsh_env__
    vd = env.get_docs(name)
    if not vd.configurable:
        return
    default = vd.default
    if '\n' in default:
        default = '\n' + _wrap_paragraphs(default, width=69)
    curr = env.get(name)
    if is_string(curr) and is_template_string(curr):
        curr = curr.replace('{', '{{').replace('}', '}}')
    curr = pformat(curr, width=69)
    if '\n' in curr:
        curr = '\n' + curr
    msg = ENVVAR_MESSAGE.format(name=name, default=default, current=curr,
                                docstr=_wrap_paragraphs(vd.docstr, width=69))
    mnode = wiz.Message(message=msg)
    ens = env.get_ensurer(name)
    path = '/env/' + name
    pnode = wiz.StoreNonEmpty(ENVVAR_PROMPT, converter=ens.convert,
                              show_conversion=True, path=path, retry=True,
                              store_raw=vd.store_as_str)
    return mnode, pnode


def _make_flat_wiz(kidfunc, *args):
    kids = map(kidfunc, *args)
    flatkids = []
    for k in kids:
        if k is None:
            continue
        flatkids.extend(k)
    wizard = wiz.Wizard(children=flatkids)
    return wizard


def make_env_wiz():
    """Makes an environment variable wizard."""
    w = _make_flat_wiz(make_envvar, sorted(builtins.__xonsh_env__._docs.keys()))
    return w


XONTRIB_PROMPT = '{BOLD_GREEN}Add this xontrib{NO_COLOR}, ' + wiz.YN

def _xontrib_path(visitor=None, node=None, val=None):
    # need this to append only based on user-selected size
    return ('xontribs', len(visitor.state.get('xontribs', ())))


def make_xontrib(xontrib, package):
    """Makes a message and StoreNonEmpty node for a xontrib."""
    name = xontrib.get('name', '<unknown-xontrib-name>')
    msg = '\n{BOLD_CYAN}' + name + '{NO_COLOR}\n'
    if 'url' in xontrib:
        msg += '{RED}url:{NO_COLOR} ' + xontrib['url'] + '\n'
    if 'package' in xontrib:
        msg += '{RED}package:{NO_COLOR} ' + xontrib['package'] + '\n'
    if 'url' in package:
        if 'url' in xontrib and package['url'] != xontrib['url']:
            msg += '{RED}package-url:{NO_COLOR} ' + package['url'] + '\n'
    if 'license' in package:
        msg += '{RED}license:{NO_COLOR} ' + package['license'] + '\n'
    msg += '{PURPLE}installed?{NO_COLOR} '
    msg += ('no' if find_xontrib(name) is None else 'yes') + '\n'
    desc = xontrib.get('description', '')
    if not isinstance(desc, str):
        desc = ''.join(desc)
    msg += _wrap_paragraphs(desc, width=69)
    if msg.endswith('\n'):
        msg = msg[:-1]
    mnode = wiz.Message(message=msg)
    convert = lambda x: name if to_bool(x) else Unstorable
    pnode = wiz.StoreNonEmpty(XONTRIB_PROMPT, converter=convert,
                              path=_xontrib_path)
    return mnode, pnode


def make_xontribs_wiz():
    """Makes a xontrib wizard."""
    md = xontrib_metadata()
    pkgs = [md['packages'].get(d.get('package', None), {}) for d in md['xontribs']]
    w = _make_flat_wiz(make_xontrib, md['xontribs'], pkgs)
    return w


def make_xonfig_wizard(default_file=None, confirm=False):
    """Makes a configuration wizard for xonsh config file.

    Parameters
    ----------
    default_file : str, optional
        Default filename to save and load to. User will still be prompted.
    confirm : bool, optional
        Confirm that the main part of the wizard should be run.
    """
    w = wiz.Wizard(children=[
            wiz.Message(message=WIZARD_HEAD),
            wiz.Load(default_file=default_file, check=True),
            wiz.Message(message=WIZARD_FS),
            make_fs_wiz(),
            wiz.Message(message=WIZARD_ENV),
            wiz.YesNo(question=WIZARD_ENV_QUESTION, yes=make_env_wiz(),
                      no=wiz.Pass()),
            wiz.Message(message=WIZARD_XONTRIB),
            wiz.YesNo(question=WIZARD_XONTRIB_QUESTION, yes=make_xontribs_wiz(),
                      no=wiz.Pass()),
            wiz.Message(message='\n' + HR + '\n'),
            wiz.Save(default_file=default_file, check=True),
            wiz.Message(message=WIZARD_TAIL),
            ])
    if confirm:
        q = ("Would you like to run the xonsh configuration wizard now?\n\n"
             "1. Yes\n2. No, but ask me later.\n3. No, and don't ask me again."
             "\n\n1, 2, or 3 [default: 2]? ")
        passer = wiz.Pass()
        saver = wiz.Save(check=False, ask_filename=False,
                         default_file=default_file)
        w = wiz.Question(q, {1: w, 2: passer, 3: saver},
                         converter=lambda x: int(x) if x != '' else 2)
    return w


def _wizard(ns):
    env = builtins.__xonsh_env__
    shell = builtins.__xonsh_shell__.shell
    fname = env.get('XONSHCONFIG') if ns.file is None else ns.file
    w = make_xonfig_wizard(default_file=fname, confirm=ns.confirm)
    tempenv = {'PROMPT': '', 'XONSH_STORE_STDOUT': False}
    pv = wiz.PromptVisitor(w, store_in_history=False, multiline=False)
    @contextmanager
    def force_hide():
        if env.get('XONSH_STORE_STDOUT') and hasattr(shell, '_force_hide'):
            orig, shell._force_hide = shell._force_hide, False
            yield
            shell._force_hide = orig
        else:
            yield
    with force_hide(), env.swap(tempenv):
        try:
            pv.visit()
        except (KeyboardInterrupt, Exception):
            print_exception()


def _xonfig_format_human(data):
    wcol1 = wcol2 = 0
    for key, val in data:
        wcol1 = max(wcol1, len(key))
        wcol2 = max(wcol2, len(str(val)))
    hr = '+' + ('-'*(wcol1+2)) + '+' + ('-'*(wcol2+2)) + '+\n'
    row = '| {key!s:<{wcol1}} | {val!s:<{wcol2}} |\n'
    s = hr
    for key, val in data:
        s += row.format(key=key, wcol1=wcol1, val=val, wcol2=wcol2)
    s += hr
    return s


def _xonfig_format_json(data):
    data = {k.replace(' ', '_'): v for k, v in data}
    s = json.dumps(data, sort_keys=True, indent=1) + '\n'
    return s


def _info(ns):
    data = [
        ('xonsh', XONSH_VERSION),
        ('Python', '{}.{}.{}'.format(*PYTHON_VERSION_INFO)),
        ('PLY', ply.__version__),
        ('have readline', is_readline_available()),
        ('prompt toolkit', ptk_version() or None),
        ('shell type', builtins.__xonsh_env__.get('SHELL_TYPE')),
        ('pygments', pygments_version()),
        ('on posix', ON_POSIX),
        ('on linux', ON_LINUX)]
    if ON_LINUX:
        data.append(('distro', linux_distro()))
    data.extend([
        ('on darwin', ON_DARWIN),
        ('on windows', ON_WINDOWS),
        ('on cygwin', ON_CYGWIN),
        ('is superuser', is_superuser()),
        ('default encoding', DEFAULT_ENCODING),
        ('git SHA', githash())
        ])
    formatter = _xonfig_format_json if ns.json else _xonfig_format_human
    s = formatter(data)
    return s


def _styles(ns):
    env = builtins.__xonsh_env__
    curr = env.get('XONSH_COLOR_STYLE')
    styles = sorted(color_style_names())
    if ns.json:
        s = json.dumps(styles, sort_keys=True, indent=1)
        print(s)
        return
    lines = []
    for style in styles:
        if style == curr:
            lines.append('* {GREEN}' + style + '{NO_COLOR}')
        else:
            lines.append('  ' + style)
    s = '\n'.join(lines)
    print_color(s)


def _str_colors(cmap, cols):
    color_names = sorted(cmap.keys(), key=(lambda s: (len(s), s)))
    grper = lambda s: min(cols // (len(s) + 1), 8)
    lines = []
    for n, group in itertools.groupby(color_names, key=grper):
        width = cols // n
        line = ''
        for i, name in enumerate(group):
            buf = ' ' * (width - len(name))
            line += '{' + name + '}' + name + '{NO_COLOR}' + buf
            if (i+1)%n == 0:
                lines.append(line)
                line = ''
        if len(line) != 0:
            lines.append(line)
    return '\n'.join(lines)

def _tok_colors(cmap, cols):
    from xonsh.pyghooks import Color
    nc = Color.NO_COLOR
    names_toks = {}
    for t in cmap.keys():
        name = str(t)
        if name.startswith('Token.Color.'):
            _, _, name = name.rpartition('.')
        names_toks[name] = t
    color_names = sorted(names_toks.keys(), key=(lambda s: (len(s), s)))
    grper = lambda s: min(cols // (len(s) + 1), 8)
    toks = []
    for n, group in itertools.groupby(color_names, key=grper):
        width = cols // n
        for i, name in enumerate(group):
            toks.append((names_toks[name], name))
            buf = ' ' * (width - len(name))
            if (i+1)%n == 0:
                buf += '\n'
            toks.append((nc, buf))
        if not toks[-1][1].endswith('\n'):
            toks[-1] = (nc, toks[-1][1] + '\n')
    return toks

def _colors(ns):
    cols, _ = shutil.get_terminal_size()
    if ON_WINDOWS:
        cols -= 1
    cmap = color_style()
    akey = next(iter(cmap))
    if isinstance(akey, str):
        s = _str_colors(cmap, cols)
    else:
        s = _tok_colors(cmap, cols)
    print_color(s)


@functools.lru_cache(1)
def _xonfig_create_parser():
    p = ArgumentParser(prog='xonfig',
                       description='Manages xonsh configuration.')
    subp = p.add_subparsers(title='action', dest='action')
    info = subp.add_parser('info', help=('displays configuration information, '
                                         'default action'))
    info.add_argument('--json', action='store_true', default=False,
                      help='reports results as json')
    wiz = subp.add_parser('wizard', help=('displays configuration information, '
                                         'default action'))
    wiz.add_argument('--file', default=None,
                     help='config file location, default=$XONSHCONFIG')
    wiz.add_argument('--confirm', action='store_true', default=False,
                      help='confirm that the wizard should be run.')
    sty = subp.add_parser('styles', help='prints available xonsh color styles')
    sty.add_argument('--json', action='store_true', default=False,
                     help='reports results as json')
    clrs = subp.add_parser('colors', help=('displays the color palette for '
                                           'the current xonsh color style'))
    return p


_XONFIG_MAIN_ACTIONS = {
    'info': _info,
    'wizard': _wizard,
    'styles': _styles,
    'colors': _colors,
    }

def xonfig_main(args=None):
    """Main xonfig entry point."""
    if not args or (args[0] not in _XONFIG_MAIN_ACTIONS and
                    args[0] not in {'-h', '--help'}):
        args.insert(0, 'info')
    parser = _xonfig_create_parser()
    ns = parser.parse_args(args)
    if ns.action is None:  # apply default action
        ns = parser.parse_args(['info'] + args)
    return _XONFIG_MAIN_ACTIONS[ns.action](ns)


if __name__ == '__main__':
    xonfig_main()

#
# aliases
#
# -*- coding: utf-8 -*-
"""Aliases for the xonsh shell."""

from argparse import Action
# amalgamated builtins
from collections.abc import MutableMapping, Iterable, Sequence
# amalgamated os
# amalgamated sys
# amalgamated shlex
# amalgamated xonsh.dirstack
# amalgamated xonsh.environ
# amalgamated xonsh.foreign_shells
# amalgamated xonsh.jobs
# amalgamated xonsh.history
# amalgamated xonsh.platform
# amalgamated xonsh.proc
# amalgamated xonsh.replay
# amalgamated xonsh.timings
# amalgamated xonsh.tools
# amalgamated xonsh.vox
# amalgamated xonsh.xontribs
from xonsh.xoreutils import _which
from xonsh.completers._aliases import completer_alias


class Aliases(MutableMapping):
    """Represents a location to hold and look up aliases."""

    def __init__(self, *args, **kwargs):
        self._raw = {}
        self.update(*args, **kwargs)

    def get(self, key, default=None):
        """Returns the (possibly modified) value. If the key is not present,
        then `default` is returned.
        If the value is callable, it is returned without modification. If it
        is an iterable of strings it will be evaluated recursively to expand
        other aliases, resulting in a new list or a "partially applied"
        callable.
        """
        val = self._raw.get(key)
        if val is None:
            return default
        elif isinstance(val, Iterable) or callable(val):
            return self.eval_alias(val, seen_tokens={key})
        else:
            msg = 'alias of {!r} has an inappropriate type: {!r}'
            raise TypeError(msg.format(key, val))

    def eval_alias(self, value, seen_tokens=frozenset(), acc_args=()):
        """
        "Evaluates" the alias `value`, by recursively looking up the leftmost
        token and "expanding" if it's also an alias.

        A value like ["cmd", "arg"] might transform like this:
        > ["cmd", "arg"] -> ["ls", "-al", "arg"] -> callable()
        where `cmd=ls -al` and `ls` is an alias with its value being a
        callable.  The resulting callable will be "partially applied" with
        ["-al", "arg"].
        """
        # Beware of mutability: default values for keyword args are evaluated
        # only once.
        if callable(value):
            if acc_args:  # Partial application
                def _alias(args, stdin=None):
                    args = list(acc_args) + args
                    return value(args, stdin=stdin)
                return _alias
            else:
                return value
        else:
            expand_path = builtins.__xonsh_expand_path__
            token, *rest = map(expand_path, value)
            if token in seen_tokens or token not in self._raw:
                # ^ Making sure things like `egrep=egrep --color=auto` works,
                # and that `l` evals to `ls --color=auto -CF` if `l=ls -CF`
                # and `ls=ls --color=auto`
                rtn = [token]
                rtn.extend(rest)
                rtn.extend(acc_args)
                return rtn
            else:
                seen_tokens = seen_tokens | {token}
                acc_args = rest + list(acc_args)
                return self.eval_alias(self._raw[token], seen_tokens, acc_args)

    def expand_alias(self, line):
        """Expands any aliases present in line if alias does not point to a
        builtin function and if alias is only a single command.
        """
        word = line.split(' ', 1)[0]
        if word in builtins.aliases and isinstance(self.get(word), Sequence):
            word_idx = line.find(word)
            expansion = ' '.join(self.get(word))
            line = line[:word_idx] + expansion + line[word_idx+len(word):]
        return line

    #
    # Mutable mapping interface
    #

    def __getitem__(self, key):
        return self._raw[key]

    def __setitem__(self, key, val):
        if isinstance(val, str):
            self._raw[key] = shlex.split(val)
        else:
            self._raw[key] = val

    def __delitem__(self, key):
        del self._raw[key]

    def update(self, *args, **kwargs):
        for key, val in dict(*args, **kwargs).items():
            self[key] = val

    def __iter__(self):
        yield from self._raw

    def __len__(self):
        return len(self._raw)

    def __str__(self):
        return str(self._raw)

    def __repr__(self):
        return '{0}.{1}({2})'.format(self.__class__.__module__,
                                     self.__class__.__name__, self._raw)

    def _repr_pretty_(self, p, cycle):
        name = '{0}.{1}'.format(self.__class__.__module__,
                                self.__class__.__name__)
        with p.group(0, name + '(', ')'):
            if cycle:
                p.text('...')
            elif len(self):
                p.break_()
                p.pretty(dict(self))



def xonsh_exit(args, stdin=None):
    """Sends signal to exit shell."""
    if not clean_jobs():
        # Do not exit if jobs not cleaned up
        return None, None
    builtins.__xonsh_exit__ = True
    print()  # gimme a newline
    return None, None


_SOURCE_FOREIGN_PARSER = None


def _ensure_source_foreign_parser():
    global _SOURCE_FOREIGN_PARSER
    if _SOURCE_FOREIGN_PARSER is not None:
        return _SOURCE_FOREIGN_PARSER
    desc = "Sources a file written in a foreign shell language."
    parser = ArgumentParser('source-foreign', description=desc)
    parser.add_argument('shell', help='Name or path to the foreign shell')
    parser.add_argument('files_or_code', nargs='+',
                        help='file paths to source or code in the target '
                             'language.')
    parser.add_argument('-i', '--interactive', type=to_bool, default=True,
                        help='whether the sourced shell should be interactive',
                        dest='interactive')
    parser.add_argument('-l', '--login', type=to_bool, default=False,
                        help='whether the sourced shell should be login',
                        dest='login')
    parser.add_argument('--envcmd', default=None, dest='envcmd',
                        help='command to print environment')
    parser.add_argument('--aliascmd', default=None, dest='aliascmd',
                        help='command to print aliases')
    parser.add_argument('--extra-args', default=(), dest='extra_args',
                        type=(lambda s: tuple(s.split())),
                        help='extra arguments needed to run the shell')
    parser.add_argument('-s', '--safe', type=to_bool, default=True,
                        help='whether the source shell should be run safely, '
                             'and not raise any errors, even if they occur.',
                        dest='safe')
    parser.add_argument('-p', '--prevcmd', default=None, dest='prevcmd',
                        help='command(s) to run before any other commands, '
                             'replaces traditional source.')
    parser.add_argument('--postcmd', default='', dest='postcmd',
                        help='command(s) to run after all other commands')
    parser.add_argument('--funcscmd', default=None, dest='funcscmd',
                        help='code to find locations of all native functions '
                             'in the shell language.')
    parser.add_argument('--sourcer', default=None, dest='sourcer',
                        help='the source command in the target shell '
                        'language, default: source.')
    parser.add_argument('--use-tmpfile', type=to_bool, default=False,
                        help='whether the commands for source shell should be '
                             'written to a temporary file.',
                        dest='use_tmpfile')
    parser.add_argument('--seterrprevcmd', default=None, dest='seterrprevcmd',
                        help='command(s) to set exit-on-error before any'
                             'other commands.')
    parser.add_argument('--seterrpostcmd', default=None, dest='seterrpostcmd',
                        help='command(s) to set exit-on-error after all'
                             'other commands.')
    _SOURCE_FOREIGN_PARSER = parser
    return parser


def source_foreign(args, stdin=None):
    """Sources a file written in a foreign shell language."""
    parser = _ensure_source_foreign_parser()
    ns = parser.parse_args(args)
    if ns.prevcmd is not None:
        pass  # don't change prevcmd if given explicitly
    elif os.path.isfile(ns.files_or_code[0]):
        # we have filename to source
        ns.prevcmd = '{} "{}"'.format(ns.sourcer, '" "'.join(ns.files_or_code))
    elif ns.prevcmd is None:
        ns.prevcmd = ' '.join(ns.files_or_code)  # code to run, no files
    foreign_shell_data.cache_clear()  # make sure that we don't get prev src
    fsenv, fsaliases = foreign_shell_data(shell=ns.shell, login=ns.login,
                                          interactive=ns.interactive,
                                          envcmd=ns.envcmd,
                                          aliascmd=ns.aliascmd,
                                          extra_args=ns.extra_args,
                                          safe=ns.safe, prevcmd=ns.prevcmd,
                                          postcmd=ns.postcmd,
                                          funcscmd=ns.funcscmd,
                                          sourcer=ns.sourcer,
                                          use_tmpfile=ns.use_tmpfile,
                                          seterrprevcmd=ns.seterrprevcmd,
                                          seterrpostcmd=ns.seterrpostcmd)
    if fsenv is None:
        return (None, 'xonsh: error: Source failed: '
                      '{}\n'.format(ns.prevcmd), 1)
    # apply results
    env = builtins.__xonsh_env__
    denv = env.detype()
    for k, v in fsenv.items():
        if k in denv and v == denv[k]:
            continue  # no change from original
        env[k] = v
    # Remove any env-vars that were unset by the script.
    for k in denv:
        if k not in fsenv:
            env.pop(k, None)
    # Update aliases
    baliases = builtins.aliases
    for k, v in fsaliases.items():
        if k in baliases and v == baliases[k]:
            continue  # no change from original
        baliases[k] = v


def source_alias(args, stdin=None):
    """Executes the contents of the provided files in the current context.
    If sourced file isn't found in cwd, search for file along $PATH to source
    instead"""
    for fname in args:
        if not os.path.isfile(fname):
            fname = locate_binary(fname)
        with open(fname, 'r') as fp:
            builtins.execx(fp.read(), 'exec', builtins.__xonsh_ctx__)


def source_cmd(args, stdin=None):
    """Simple cmd.exe-specific wrapper around source-foreign."""
    args = list(args)
    fpath = locate_binary(args[0])
    args[0] = fpath if fpath else args[0]
    if not os.path.isfile(args[0]):
        return (None, 'xonsh: error: File not found: {}\n'.format(args[0]), 1)
    prevcmd = 'call '
    prevcmd += ' '.join([argvquote(arg, force=True) for arg in args])
    prevcmd = escape_windows_cmd_string(prevcmd)
    args.append('--prevcmd={}'.format(prevcmd))
    args.insert(0, 'cmd')
    args.append('--interactive=0')
    args.append('--sourcer=call')
    args.append('--envcmd=set')
    args.append('--seterrpostcmd=if errorlevel 1 exit 1')
    args.append('--use-tmpfile=1')
    with builtins.__xonsh_env__.swap(PROMPT='$P$G'):
        return source_foreign(args, stdin=stdin)


def xexec(args, stdin=None):
    """Replaces current process with command specified and passes in the
    current xonsh environment.
    """
    env = builtins.__xonsh_env__
    denv = env.detype()
    if len(args) > 0:
        try:
            os.execvpe(args[0], args, denv)
        except FileNotFoundError as e:
            return (None, 'xonsh: exec: file not found: {}: {}'
                          '\n'.format(e.args[1], args[0]), 1)
    else:
        return (None, 'xonsh: exec: no args specified\n', 1)


_BANG_N_PARSER = None


def bang_n(args, stdin=None):
    """Re-runs the nth command as specified in the argument."""
    global _BANG_N_PARSER
    if _BANG_N_PARSER is None:
        parser = _BANG_N_PARSER = ArgumentParser('!n', usage='!n <n>',
                    description="Re-runs the nth command as specified in the argument.")
        parser.add_argument('n', type=int, help='the command to rerun, may be negative')
    else:
        parser = _BANG_N_PARSER
    ns = parser.parse_args(args)
    hist = builtins.__xonsh_history__
    nhist = len(hist)
    n = nhist + ns.n if ns.n < 0 else ns.n
    if n < 0 or n >= nhist:
        raise IndexError('n out of range, {0} for history len {1}'.format(ns.n, nhist))
    cmd = hist.inps[n]
    if cmd.startswith('!'):
        raise XonshError('xonsh: error: recursive call to !n')
    builtins.execx(cmd)


def bang_bang(args, stdin=None):
    """Re-runs the last command. Just a wrapper around bang_n."""
    return bang_n(['-1'])


class AWitchAWitch(Action):
    SUPPRESS = '==SUPPRESS=='
    def __init__(self, option_strings, version=None, dest=SUPPRESS,
                 default=SUPPRESS, **kwargs):
        super().__init__(option_strings=option_strings, dest=dest,
                         default=default, nargs=0, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        import webbrowser
        webbrowser.open('https://github.com/xonsh/xonsh/commit/f49b400')
        parser.exit()


def which(args, stdin=None, stdout=None, stderr=None):
    """
    Checks if each arguments is a xonsh aliases, then if it's an executable,
    then finally return an error code equal to the number of misses.
    If '-a' flag is passed, run both to return both `xonsh` match and
    `which` match.
    """
    desc = "Parses arguments to which wrapper"
    parser = ArgumentParser('which', description=desc)
    parser.add_argument('args', type=str, nargs='+',
                        help='The executables or aliases to search for')
    parser.add_argument('-a','--all', action='store_true', dest='all',
                        help='Show all matches in $PATH and xonsh.aliases')
    parser.add_argument('-s', '--skip-alias', action='store_true',
                        help='Do not search in xonsh.aliases', dest='skip')
    parser.add_argument('-V', '--version', action='version',
                        version='{}'.format(_which.__version__),
                        help='Display the version of the python which module '
                        'used by xonsh')
    parser.add_argument('-v', '--verbose', action='store_true', dest='verbose',
                        help='Print out how matches were located and show '
                        'near misses on stderr')
    parser.add_argument('-p', '--plain', action='store_true', dest='plain',
                        help='Do not display alias expansions or location of '
                             'where binaries are found. This is the '
                             'default behavior, but the option can be used to '
                             'override the --verbose option')
    parser.add_argument('--very-small-rocks', action=AWitchAWitch)
    if ON_WINDOWS:
        parser.add_argument('-e', '--exts', nargs='*', type=str,
                            help='Specify a list of extensions to use instead '
                            'of the standard list for this system. This can '
                            'effectively be used as an optimization to, for '
                            'example, avoid stat\'s of "foo.vbs" when '
                            'searching for "foo" and you know it is not a '
                            'VisualBasic script but ".vbs" is on PATHEXT. '
                            'This option is only supported on Windows',
                            dest='exts')
    if len(args) == 0:
        parser.print_usage(file=stderr)
        return -1
    pargs = parser.parse_args(args)

    if pargs.all:
        pargs.verbose = True

    if ON_WINDOWS:
        if pargs.exts:
            exts = pargs.exts
        else:
            exts = builtins.__xonsh_env__['PATHEXT']
    else:
        exts = None

    failures = []
    for arg in pargs.args:
        nmatches = 0
        # skip alias check if user asks to skip
        if (arg in builtins.aliases and not pargs.skip):
            if pargs.plain or not pargs.verbose:
                if isinstance(builtins.aliases[arg], list):
                    print(' '.join(builtins.aliases[arg]), file=stdout)
                else:
                    print(arg, file=stdout)
            else:
                print("aliases['{}'] = {}".format(arg, builtins.aliases[arg]), file=stdout)
            nmatches += 1
            if not pargs.all:
                continue
        # which.whichgen gives the nicest 'verbose' output if PATH is taken
        # from os.environ so we temporarily override it with
        # __xosnh_env__['PATH']
        original_os_path = os.environ['PATH']
        os.environ['PATH'] = builtins.__xonsh_env__.detype()['PATH']
        matches = _which.whichgen(arg, exts=exts, verbose=pargs.verbose)
        for abs_name, from_where in matches:
            if ON_WINDOWS:
                # Use list dir to get correct case for the filename
                # i.e. windows is case insensitive but case preserving
                p, f = os.path.split(abs_name)
                f = next(s.name for s in scandir(p) if s.name.lower() == f.lower())
                abs_name = os.path.join(p, f)
                if builtins.__xonsh_env__.get('FORCE_POSIX_PATHS', False):
                    abs_name.replace(os.sep, os.altsep)
            if pargs.plain or not pargs.verbose:
                print(abs_name, file=stdout)
            else:
                print('{} ({})'.format(abs_name, from_where), file=stdout)
            nmatches += 1
            if not pargs.all:
                break
        os.environ['PATH'] = original_os_path
        if not nmatches:
            failures.append(arg)
    if len(failures) == 0:
        return 0
    else:
        print('{} not in $PATH'.format(', '.join(failures)), file=stderr, end='')
        if not pargs.skip:
            print(' or xonsh.builtins.aliases', file=stderr, end='')
        print('', end='\n')
        return len(failures)


def xonfig(args, stdin=None):
    """Runs the xonsh configuration utility."""
    from xonsh.xonfig import xonfig_main  # lazy import
    return xonfig_main(args)


@foreground
def trace(args, stdin=None):
    """Runs the xonsh tracer utility."""
    from xonsh.tracer import tracermain  # lazy import
    try:
        return tracermain(args)
    except SystemExit:
        pass


def vox(args, stdin=None):
    """Runs Vox environment manager."""
    vox = Vox()
    return vox(args, stdin=stdin)


def showcmd(args, stdin=None):
    """usage: showcmd [-h|--help|cmd args]

    Displays the command and arguments as a list of strings that xonsh would
    run in subprocess mode. This is useful for determining how xonsh evaluates
    your commands and arguments prior to running these commands.

    optional arguments:
      -h, --help            show this help message and exit

    example:
      >>> showcmd echo $USER can't hear "the sea"
      ['echo', 'I', "can't", 'hear', 'the sea']
    """
    if len(args) == 0 or (len(args) == 1 and args[0] in {'-h', '--help'}):
        print(showcmd.__doc__.rstrip().replace('\n    ', '\n'))
    else:
        sys.displayhook(args)


def make_default_aliases():
    """Creates a new default aliases dictionary."""
    default_aliases = {
        'cd': cd,
        'pushd': pushd,
        'popd': popd,
        'dirs': dirs,
        'jobs': jobs,
        'fg': fg,
        'bg': bg,
        'EOF': xonsh_exit,
        'exit': xonsh_exit,
        'quit': xonsh_exit,
        'xexec': xexec,
        'source': source_alias,
        'source-zsh': ['source-foreign', 'zsh', '--sourcer=source'],
        'source-bash':  ['source-foreign', 'bash', '--sourcer=source'],
        'source-cmd': source_cmd,
        'source-foreign': source_foreign,
        'history': history_main,
        'replay': replay_main,
        '!!': bang_bang,
        '!n': bang_n,
        'trace': trace,
        'timeit': timeit_alias,
        'xonfig': xonfig,
        'scp-resume': ['rsync', '--partial', '-h', '--progress', '--rsh=ssh'],
        'showcmd': showcmd,
        'ipynb': ['jupyter', 'notebook', '--no-browser'],
        'vox': vox,
        'which': which,
        'xontrib': xontribs_main,
        'completer': completer_alias
    }
    if ON_WINDOWS:
        # Borrow builtin commands from cmd.exe.
        windows_cmd_aliases = {
            'cls',
            'copy',
            'del',
            'dir',
            'erase',
            'md',
            'mkdir',
            'mklink',
            'move',
            'rd',
            'ren',
            'rename',
            'rmdir',
            'time',
            'type',
            'vol'
        }
        for alias in windows_cmd_aliases:
            default_aliases[alias] = ['cmd', '/c', alias]
        default_aliases['call'] = ['source-cmd']
        default_aliases['source-bat'] = ['source-cmd']
        default_aliases['clear'] = 'cls'
        if ON_ANACONDA:
            # Add aliases specific to the Anaconda python distribution.
            default_aliases['activate'] = ['source-cmd', 'activate.bat']
            default_aliases['deactivate'] = ['source-cmd', 'deactivate.bat']
        if not locate_binary('sudo'):
            import xonsh.winutils as winutils

            def sudo(args, sdin=None):
                if len(args) < 1:
                    print('You need to provide an executable to run as '
                          'Administrator.')
                    return
                cmd = args[0]
                if locate_binary(cmd):
                    return winutils.sudo(cmd, args[1:])
                elif cmd.lower() in windows_cmd_aliases:
                    args = ['/D', '/C', 'CD', _get_cwd(), '&&'] + args
                    return winutils.sudo('cmd', args)
                else:
                    msg = 'Cannot find the path for executable "{0}".'
                    print(msg.format(cmd))

            default_aliases['sudo'] = sudo
    elif ON_DARWIN:
        default_aliases['ls'] = ['ls', '-G']
    else:
        default_aliases['grep'] = ['grep', '--color=auto']
        default_aliases['egrep'] = ['egrep', '--color=auto']
        default_aliases['fgrep'] = ['fgrep', '--color=auto']
        default_aliases['ls'] = ['ls', '--color=auto', '-v']
    return default_aliases

#
# readline_shell
#
# -*- coding: utf-8 -*-
"""The readline based xonsh shell.

Portions of this code related to initializing the readline library
are included from the IPython project.  The IPython project is:

* Copyright (c) 2008-2014, IPython Development Team
* Copyright (c) 2001-2007, Fernando Perez <fernando.perez@colorado.edu>
* Copyright (c) 2001, Janko Hauser <jhauser@zscout.de>
* Copyright (c) 2001, Nathaniel Gray <n8gray@caltech.edu>

"""
# amalgamated os
# amalgamated sys
# amalgamated time
# amalgamated select
# amalgamated builtins
# amalgamated importlib
from cmd import Cmd
# amalgamated from threading import Thread
# amalgamated from collections import deque
# amalgamated xonsh.lazyjson
# amalgamated xonsh.lazyasd
# amalgamated xonsh.base_shell
# amalgamated xonsh.ansi_colors
# amalgamated xonsh.environ
# amalgamated xonsh.tools
# amalgamated xonsh.platform
pygments = LazyObject(lambda: importlib.import_module('pygments'),
                      globals(), 'pygments')
terminal256 = LazyObject(lambda: importlib.import_module(
                                    'pygments.formatters.terminal256'),
                      globals(), 'terminal')
pyghooks = LazyObject(lambda: importlib.import_module('xonsh.pyghooks'),
                      globals(), 'pyghooks')

readline = None
RL_COMPLETION_SUPPRESS_APPEND = RL_LIB = RL_STATE = None
RL_CAN_RESIZE = False
RL_DONE = None
RL_VARIABLE_VALUE = None
_RL_STATE_DONE = 0x1000000
_RL_STATE_ISEARCH = 0x0000080

_RL_PREV_CASE_SENSITIVE_COMPLETIONS = 'to-be-set'


def setup_readline():
    """Sets up the readline module and completion suppression, if available."""
    global RL_COMPLETION_SUPPRESS_APPEND, RL_LIB, RL_CAN_RESIZE, RL_STATE, readline
    if RL_COMPLETION_SUPPRESS_APPEND is not None:
        return
    for _rlmod_name in ('gnureadline', 'readline'):
        try:
            readline = importlib.import_module(_rlmod_name)
            sys.modules['readline'] = readline
        except ImportError:
            pass
        else:
            break
    if readline is None:
        print("No readline implementation available.  Skipping setup.")
        return
    import ctypes
    import ctypes.util
    uses_libedit = readline.__doc__ and 'libedit' in readline.__doc__
    readline.set_completer_delims(' \t\n')
    # Cygwin seems to hang indefinitely when querying the readline lib
    if (not ON_CYGWIN) and (not readline.__file__.endswith('.py')):
        RL_LIB = lib = ctypes.cdll.LoadLibrary(readline.__file__)
        try:
            RL_COMPLETION_SUPPRESS_APPEND = ctypes.c_int.in_dll(
                lib, 'rl_completion_suppress_append')
        except ValueError:
            # not all versions of readline have this symbol, ie Macs sometimes
            RL_COMPLETION_SUPPRESS_APPEND = None
        try:
            RL_STATE = ctypes.c_int.in_dll(lib, 'rl_readline_state')
        except:
            pass
        RL_CAN_RESIZE = hasattr(lib, 'rl_reset_screen_size')
    env = builtins.__xonsh_env__
    # reads in history
    readline.set_history_length(-1)
    ReadlineHistoryAdder()
    # sets up IPython-like history matching with up and down
    readline.parse_and_bind('"\e[B": history-search-forward')
    readline.parse_and_bind('"\e[A": history-search-backward')
    # Setup Shift-Tab to indent
    readline.parse_and_bind('"\e[Z": "{0}"'.format(env.get('INDENT')))

    # handle tab completion differences found in libedit readline compatibility
    # as discussed at http://stackoverflow.com/a/7116997
    if uses_libedit and ON_DARWIN:
        readline.parse_and_bind("bind ^I rl_complete")
        print('\n'.join(['', "*"*78,
            "libedit detected - readline will not be well behaved, including but not limited to:",
            "   * crashes on tab completion",
            "   * incorrect history navigation",
            "   * corrupting long-lines",
            "   * failure to wrap or indent lines properly",
            "",
            "It is highly recommended that you install gnureadline, which is installable with:",
            "     pip install gnureadline",
            "*"*78]), file=sys.stderr)
    else:
        readline.parse_and_bind("tab: complete")
    # try to load custom user settings
    inputrc_name = os.environ.get('INPUTRC')
    if inputrc_name is None:
        if uses_libedit:
            inputrc_name = '.editrc'
        else:
            inputrc_name = '.inputrc'
        inputrc_name = os.path.join(os.path.expanduser('~'), inputrc_name)
    if (not ON_WINDOWS) and (not os.path.isfile(inputrc_name)):
        inputrc_name = '/etc/inputrc'
    if os.path.isfile(inputrc_name):
        try:
            readline.read_init_file(inputrc_name)
        except Exception:
            # this seems to fail with libedit
            print_exception('xonsh: could not load readline default init file.')


def teardown_readline():
    """Tears down up the readline module, if available."""
    try:
        import readline
    except (ImportError, TypeError):
        return


def _rebind_case_sensitive_completions():
    # handle case sensitive, see Github issue #1342 for details
    global _RL_PREV_CASE_SENSITIVE_COMPLETIONS
    env = builtins.__xonsh_env__
    case_sensitive = env.get('CASE_SENSITIVE_COMPLETIONS')
    if case_sensitive is _RL_PREV_CASE_SENSITIVE_COMPLETIONS:
        return
    if case_sensitive:
        readline.parse_and_bind("set completion-ignore-case off")
    else:
        readline.parse_and_bind("set completion-ignore-case on")
    _RL_PREV_CASE_SENSITIVE_COMPLETIONS = case_sensitive


def fix_readline_state_after_ctrl_c():
    """
    Fix to allow Ctrl-C to exit reverse-i-search.

    Based on code from:
        http://bugs.python.org/file39467/raw_input__workaround_demo.py
    """
    if ON_WINDOWS:
        # hack to make pyreadline mimic the desired behavior
        try:
            _q = readline.rl.mode.process_keyevent_queue
            if len(_q) > 1:
                _q.pop()
        except:
            pass
    if RL_STATE is None:
        return
    if RL_STATE.value & _RL_STATE_ISEARCH:
        RL_STATE.value &= ~_RL_STATE_ISEARCH
    if not RL_STATE.value & _RL_STATE_DONE:
        RL_STATE.value |= _RL_STATE_DONE


def rl_completion_suppress_append(val=1):
    """Sets the rl_completion_suppress_append varaiable, if possible.
    A value of 1 (default) means to suppress, a value of 0 means to enable.
    """
    if RL_COMPLETION_SUPPRESS_APPEND is None:
        return
    RL_COMPLETION_SUPPRESS_APPEND.value = val


def rl_variable_dumper(readable=True):
    """Dumps the currently set readline variables. If readable is True, then this
    output may be used in an inputrc file.
    """
    RL_LIB.rl_variable_dumper(int(readable))


def rl_variable_value(variable):
    """Returns the currently set value for a readline configuration variable."""
    global RL_VARIABLE_VALUE
    if RL_VARIABLE_VALUE is None:
        import ctypes
        RL_VARIABLE_VALUE = RL_LIB.rl_variable_value
        RL_VARIABLE_VALUE.restype = ctypes.c_char_p
    env = builtins.__xonsh_env__
    enc, errors = env.get('XONSH_ENCODING'), env.get('XONSH_ENCODING_ERRORS')
    if isinstance(variable, str):
        variable = variable.encode(encoding=enc, errors=errors)
    rtn = RL_VARIABLE_VALUE(variable)
    return rtn.decode(encoding=enc, errors=errors)


def _insert_text_func(s, readline):
    """Creates a function to insert text via readline."""
    def inserter():
        readline.insert_text(s)
        readline.redisplay()
    return inserter


DEDENT_TOKENS = frozenset(['raise', 'return', 'pass', 'break', 'continue'])


class ReadlineShell(BaseShell, Cmd):
    """The readline based xonsh shell."""

    def __init__(self, completekey='tab', stdin=None, stdout=None, **kwargs):
        super().__init__(completekey=completekey,
                         stdin=stdin,
                         stdout=stdout,
                         **kwargs)
        setup_readline()
        self._current_indent = ''
        self._current_prompt = ''
        self._force_hide = None
        self.cmdqueue = deque()

    def __del__(self):
        teardown_readline()

    def singleline(self, store_in_history=True, **kwargs):
        """Reads a single line of input. The store_in_history kwarg
        flags whether the input should be stored in readline's in-memory
        history.
        """
        if not store_in_history:  # store current position to remove it later
            try:
                import readline
            except ImportError:
                store_in_history = True
            pos = readline.get_current_history_length() - 1
        rtn = input(self.prompt)
        if not store_in_history and pos >= 0:
            readline.remove_history_item(pos)
        return rtn

    def parseline(self, line):
        """Overridden to no-op."""
        return '', line, line

    def completedefault(self, text, line, begidx, endidx):
        """Implements tab-completion for text."""
        rl_completion_suppress_append()  # this needs to be called each time
        _rebind_case_sensitive_completions()

        mline = line.partition(' ')[2]
        offs = len(mline) - len(text)
        if self.completer is None:
            x = []
        else:
            x = [(i[offs:] if " " in i[:-1] else i)
                 for i in self.completer.complete(text, line,
                                                  begidx, endidx,
                                                  ctx=self.ctx)[0]]
        return x

    # tab complete on first index too
    completenames = completedefault

    def _load_remaining_input_into_queue(self):
        buf = b''
        while True:
            r, w, x = select.select([self.stdin], [], [], 1e-6)
            if len(r) == 0:
                break
            buf += os.read(self.stdin.fileno(), 1024)
        if len(buf) > 0:
            buf = buf.decode().replace('\r\n', '\n').replace('\r', '\n')
            self.cmdqueue.extend(buf.splitlines(keepends=True))

    def postcmd(self, stop, line):
        """Called just before execution of line. For readline, this handles the
        automatic indentation of code blocks.
        """
        try:
            import readline
        except ImportError:
            return stop
        if self.need_more_lines:
            if len(line.strip()) == 0:
                readline.set_pre_input_hook(None)
                self._current_indent = ''
            elif line.rstrip()[-1] == ':':
                ind = line[:len(line) - len(line.lstrip())]
                ind += builtins.__xonsh_env__.get('INDENT')
                readline.set_pre_input_hook(_insert_text_func(ind, readline))
                self._current_indent = ind
            elif line.split(maxsplit=1)[0] in DEDENT_TOKENS:
                env = builtins.__xonsh_env__
                ind = self._current_indent[:-len(env.get('INDENT'))]
                readline.set_pre_input_hook(_insert_text_func(ind, readline))
                self._current_indent = ind
            else:
                ind = line[:len(line) - len(line.lstrip())]
                if ind != self._current_indent:
                    insert_func = _insert_text_func(ind, readline)
                    readline.set_pre_input_hook(insert_func)
                    self._current_indent = ind
        else:
            readline.set_pre_input_hook(None)
        return stop

    def _cmdloop(self, intro=None):
        """Repeatedly issue a prompt, accept input, parse an initial prefix
        off the received input, and dispatch to action methods, passing them
        the remainder of the line as argument.

        This was forked from Lib/cmd.py from the Python standard library v3.4.3,
        (C) Python Software Foundation, 2015.
        """
        self.preloop()
        if self.use_rawinput and self.completekey:
            try:
                import readline
                self.old_completer = readline.get_completer()
                readline.set_completer(self.complete)
                readline.parse_and_bind(self.completekey + ": complete")
                have_readline = True
            except ImportError:
                have_readline = False
        try:
            if intro is not None:
                self.intro = intro
            if self.intro:
                self.stdout.write(str(self.intro)+"\n")
            stop = None
            while not stop:
                line = None
                exec_now = False
                if len(self.cmdqueue) > 0:
                    line = self.cmdqueue.popleft()
                    exec_now = line.endswith('\n')
                if self.use_rawinput and not exec_now:
                    inserter = None if line is None \
                                    else _insert_text_func(line, readline)
                    if inserter is not None:
                        readline.set_pre_input_hook(inserter)
                    try:
                        line = self.singleline()
                    except EOFError:
                        if builtins.__xonsh_env__.get("IGNOREEOF"):
                            self.stdout.write('Use "exit" to leave the shell.'
                                              '\n')
                            line = ''
                        else:
                            line = 'EOF'
                    if inserter is not None:
                        readline.set_pre_input_hook(None)
                else:
                    self.print_color(self.prompt, file=self.stdout)
                    if line is not None:
                        os.write(self.stdin.fileno(), line.encode())
                    if not exec_now:
                        line = self.stdin.readline()
                    if len(line) == 0:
                        line = 'EOF'
                    else:
                        line = line.rstrip('\r\n')
                    if have_readline and line != 'EOF':
                        readline.add_history(line)
                if not ON_WINDOWS:
                    # select() is not fully functional on windows
                    self._load_remaining_input_into_queue()
                line = self.precmd(line)
                stop = self.onecmd(line)
                stop = self.postcmd(stop, line)
            self.postloop()
        finally:
            if self.use_rawinput and self.completekey:
                try:
                    import readline
                    readline.set_completer(self.old_completer)
                except ImportError:
                    pass

    def cmdloop(self, intro=None):
        while not builtins.__xonsh_exit__:
            try:
                self._cmdloop(intro=intro)
            except KeyboardInterrupt:
                print()  # Gives a newline
                fix_readline_state_after_ctrl_c()
                self.reset_buffer()
                intro = None

    @property
    def prompt(self):
        """Obtains the current prompt string."""
        global RL_LIB, RL_CAN_RESIZE
        if RL_CAN_RESIZE:
            # This is needed to support some system where line-wrapping doesn't
            # work. This is a bug in upstream Python, or possibly readline.
            RL_LIB.rl_reset_screen_size()
        #return super().prompt
        if self.need_more_lines:
            if self.mlprompt is None:
                try:
                    self.mlprompt = multiline_prompt(curr=self._current_prompt)
                except Exception:  # pylint: disable=broad-except
                    print_exception()
                    self.mlprompt = '<multiline prompt error> '
            return self.mlprompt
        env = builtins.__xonsh_env__  # pylint: disable=no-member
        p = env.get('PROMPT')
        try:
            p = partial_format_prompt(p)
        except Exception:  # pylint: disable=broad-except
            print_exception()
        hide = True if self._force_hide is None else self._force_hide
        p = partial_color_format(p, style=env.get('XONSH_COLOR_STYLE'),
                                 hide=hide)
        self._current_prompt = p
        self.settitle()
        return p

    def format_color(self, string, hide=False, **kwargs):
        """Readline implementation of color formatting. This usesg ANSI color
        codes.
        """
        hide = hide if self._force_hide is None else self._force_hide
        return partial_color_format(string, hide=hide,
                    style=builtins.__xonsh_env__.get('XONSH_COLOR_STYLE'))

    def print_color(self, string, hide=False, **kwargs):
        if isinstance(string, str):
            s = self.format_color(string, hide=hide)
        else:
            # assume this is a list of (Token, str) tuples and format it
            env = builtins.__xonsh_env__
            self.styler.style_name = env.get('XONSH_COLOR_STYLE')
            style_proxy = pyghooks.xonsh_style_proxy(self.styler)
            formatter = terminal256.Terminal256Formatter(style=style_proxy)
            s = pygments.format(string, formatter).rstrip()
        print(s, **kwargs)

    def color_style_names(self):
        """Returns an iterable of all available style names."""
        return color_style_names()

    def color_style(self):
        """Returns the current color map."""
        style = style=builtins.__xonsh_env__.get('XONSH_COLOR_STYLE')
        return color_style(style=style)


class ReadlineHistoryAdder(Thread):

    def __init__(self, wait_for_gc=True, *args, **kwargs):
        """Thread responsible for adding inputs from history to the current readline
        instance. May wait for the history garbage collector to finish.
        """
        super(ReadlineHistoryAdder, self).__init__(*args, **kwargs)
        self.daemon = True
        self.wait_for_gc = wait_for_gc
        self.start()

    def run(self):
        try:
            import readline
        except ImportError:
            return
        hist = builtins.__xonsh_history__
        while self.wait_for_gc and hist.gc.is_alive():
            time.sleep(0.011)  # gc sleeps for 0.01 secs, sleep a beat longer
        files = hist.gc.files()
        i = 1
        for _, _, f in files:
            try:
                lj = LazyJSON(f, reopen=False)
                for cmd in lj['cmds']:
                    inp = cmd['inp'].splitlines()
                    for line in inp:
                        if line == 'EOF':
                            continue
                        readline.add_history(line)
                        if RL_LIB is not None:
                            RL_LIB.history_set_pos(i)
                        i += 1
                lj.close()
            except (IOError, OSError, ValueError):
                continue

#
# built_ins
#
# -*- coding: utf-8 -*-
"""The xonsh built-ins.

Note that this module is named 'built_ins' so as not to be confused with the
special Python builtins module.
"""
atexit = _LazyModule.load('atexit', 'atexit')
# amalgamated builtins
# amalgamated from collections import Sequence
# amalgamated from contextlib import contextmanager
# amalgamated inspect
# amalgamated os
# amalgamated re
# amalgamated shlex
# amalgamated signal
# amalgamated from subprocess import Popen, PIPE, STDOUT, CalledProcessError
# amalgamated sys
# amalgamated tempfile
# amalgamated time
# amalgamated xonsh.lazyasd
# amalgamated xonsh.history
# amalgamated xonsh.inspectors
# amalgamated xonsh.aliases
# amalgamated xonsh.environ
# amalgamated xonsh.foreign_shells
# amalgamated xonsh.jobs
# amalgamated xonsh.platform
# amalgamated xonsh.proc
# amalgamated xonsh.tools
# amalgamated xonsh.commands_cache
BUILTINS_LOADED = False
INSPECTOR = LazyObject(Inspector, globals(), 'INSPECTOR')
AT_EXIT_SIGNALS = (signal.SIGABRT, signal.SIGFPE, signal.SIGILL, signal.SIGSEGV,
                   signal.SIGTERM)

SIGNAL_MESSAGES = {
    signal.SIGABRT: 'Aborted',
    signal.SIGFPE: 'Floating point exception',
    signal.SIGILL: 'Illegal instructions',
    signal.SIGTERM: 'Terminated',
    signal.SIGSEGV: 'Segmentation fault'
}

if ON_POSIX:
    AT_EXIT_SIGNALS += (signal.SIGTSTP, signal.SIGQUIT, signal.SIGHUP)
    SIGNAL_MESSAGES.update({
        signal.SIGQUIT: 'Quit',
        signal.SIGHUP: 'Hangup',
        signal.SIGKILL: 'Killed'
    })

def resetting_signal_handle(sig, f):
    """Sets a new signal handle that will automatically restore the old value
    once the new handle is finished.
    """
    oldh = signal.getsignal(sig)

    def newh(s=None, frame=None):
        f(s, frame)
        signal.signal(sig, oldh)
        if sig != 0:
            sys.exit(sig)
    signal.signal(sig, newh)


def helper(x, name=''):
    """Prints help about, and then returns that variable."""
    INSPECTOR.pinfo(x, oname=name, detail_level=0)
    return x


def superhelper(x, name=''):
    """Prints help about, and then returns that variable."""
    INSPECTOR.pinfo(x, oname=name, detail_level=1)
    return x


def expand_path(s):
    """Takes a string path and expands ~ to home and environment vars."""
    if builtins.__xonsh_env__.get('EXPAND_ENV_VARS'):
        s = expandvars(s)
    return os.path.expanduser(s)


def reglob(path, parts=None, i=None):
    """Regular expression-based globbing."""
    if parts is None:
        path = os.path.normpath(path)
        drive, tail = os.path.splitdrive(path)
        parts = tail.split(os.sep)
        d = os.sep if os.path.isabs(path) else '.'
        d = os.path.join(drive, d)
        return reglob(d, parts, i=0)
    base = subdir = path
    if i == 0:
        if not os.path.isabs(base):
            base = ''
        elif len(parts) > 1:
            i += 1
    regex = os.path.join(base, parts[i])
    if ON_WINDOWS:
        # currently unable to access regex backslash sequences
        # on Windows due to paths using \.
        regex = regex.replace('\\', '\\\\')
    regex = re.compile(regex)
    files = os.listdir(subdir)
    files.sort()
    paths = []
    i1 = i + 1
    if i1 == len(parts):
        for f in files:
            p = os.path.join(base, f)
            if regex.fullmatch(p) is not None:
                paths.append(p)
    else:
        for f in files:
            p = os.path.join(base, f)
            if regex.fullmatch(p) is None or not os.path.isdir(p):
                continue
            paths += reglob(p, parts=parts, i=i1)
    return paths


def regexsearch(s):
    s = expand_path(s)
    return reglob(s)


def globsearch(s):
    csc = builtins.__xonsh_env__.get('CASE_SENSITIVE_COMPLETIONS')
    glob_sorted = builtins.__xonsh_env__.get('GLOB_SORTED')
    return globpath(s, ignore_case=(not csc), return_empty=True,
                    sort_result=glob_sorted)


def pathsearch(func, s, pymode=False):
    """
    Takes a string and returns a list of file paths that match (regex, glob,
    or arbitrary search function).
    """
    if (not callable(func) or
            len(inspect.signature(func).parameters) != 1):
        error = "%r is not a known path search function"
        raise XonshError(error % searchfunc)
    o = func(s)
    no_match = [] if pymode else [s]
    return o if len(o) != 0 else no_match

RE_SHEBANG = re.compile(r'#![ \t]*(.+?)$')


def _is_binary(fname, limit=80):
    with open(fname, 'rb') as f:
        for i in range(limit):
            char = f.read(1)
            if char == b'\0':
                return True
            if char == b'\n':
                return False
            if char == b'':
                return False
    return False


def _un_shebang(x):
    if x == '/usr/bin/env':
        return []
    elif any(x.startswith(i) for i in ['/usr/bin', '/usr/local/bin', '/bin']):
        x = os.path.basename(x)
    elif x.endswith('python') or x.endswith('python.exe'):
        x = 'python'
    if x == 'xonsh':
        return ['python', '-m', 'xonsh.main']
    return [x]


def get_script_subproc_command(fname, args):
    """
    Given the name of a script outside the path, returns a list representing
    an appropriate subprocess command to execute the script.  Raises
    PermissionError if the script is not executable.
    """
    # make sure file is executable
    if not os.access(fname, os.X_OK):
        raise PermissionError

    if ON_POSIX and not os.access(fname, os.R_OK):
        # on some systems, some importnat programs (e.g. sudo) will have
        # execute permissions but not read/write permisions. This enables
        # things with the SUID set to be run. Needs to come before _is_binary()
        # is called, because that function tries to read the file.
        return [fname] + args
    elif _is_binary(fname):
        # if the file is a binary, we should call it directly
        return [fname] + args

    if ON_WINDOWS:
        # Windows can execute various filetypes directly
        # as given in PATHEXT
        _, ext = os.path.splitext(fname)
        if ext.upper() in builtins.__xonsh_env__.get('PATHEXT'):
            return [fname] + args

    # find interpreter
    with open(fname, 'rb') as f:
        first_line = f.readline().decode().strip()
    m = RE_SHEBANG.match(first_line)

    # xonsh is the default interpreter
    if m is None:
        interp = ['xonsh']
    else:
        interp = m.group(1).strip()
        if len(interp) > 0:
            interp = shlex.split(interp)
        else:
            interp = ['xonsh']

    if ON_WINDOWS:
        o = []
        for i in interp:
            o.extend(_un_shebang(i))
        interp = o

    return interp + [fname] + args


_REDIR_NAME = "(o(?:ut)?|e(?:rr)?|a(?:ll)?|&?\d?)"
_REDIR_REGEX = re.compile("{r}(>?>|<){r}$".format(r=_REDIR_NAME))
_MODES = {'>>': 'a', '>': 'w', '<': 'r'}
_WRITE_MODES = frozenset({'w', 'a'})
_REDIR_ALL = frozenset({'&', 'a', 'all'})
_REDIR_ERR = frozenset({'2', 'e', 'err'})
_REDIR_OUT = frozenset({'', '1', 'o', 'out'})
_E2O_MAP = frozenset({'{}>{}'.format(e, o)
                      for e in _REDIR_ERR
                      for o in _REDIR_OUT
                      if o != ''})


def _is_redirect(x):
    return isinstance(x, str) and _REDIR_REGEX.match(x)


def _open(fname, mode):
    # file descriptors
    if isinstance(fname, int):
        return fname
    try:
        return open(fname, mode)
    except PermissionError:
        raise XonshError('xonsh: {0}: permission denied'.format(fname))
    except FileNotFoundError:
        raise XonshError('xonsh: {0}: no such file or directory'.format(fname))
    except Exception:
        raise XonshError('xonsh: {0}: unable to open file'.format(fname))


def _redirect_io(streams, r, loc=None):
    # special case of redirecting stderr to stdout
    if r.replace('&', '') in _E2O_MAP:
        if 'stderr' in streams:
            raise XonshError('Multiple redirects for stderr')
        streams['stderr'] = ('<stdout>', 'a', STDOUT)
        return

    orig, mode, dest = _REDIR_REGEX.match(r).groups()

    # redirect to fd
    if dest.startswith('&'):
        try:
            dest = int(dest[1:])
            if loc is None:
                loc, dest = dest, ''
            else:
                e = 'Unrecognized redirection command: {}'.format(r)
                raise XonshError(e)
        except (ValueError, XonshError):
            raise
        except Exception:
            pass

    mode = _MODES.get(mode, None)

    if mode == 'r':
        if len(orig) > 0 or len(dest) > 0:
            raise XonshError('Unrecognized redirection command: {}'.format(r))
        elif 'stdin' in streams:
            raise XonshError('Multiple inputs for stdin')
        else:
            streams['stdin'] = (loc, 'r', _open(loc, mode))
    elif mode in _WRITE_MODES:
        if orig in _REDIR_ALL:
            if 'stderr' in streams:
                raise XonshError('Multiple redirects for stderr')
            elif 'stdout' in streams:
                raise XonshError('Multiple redirects for stdout')
            elif len(dest) > 0:
                e = 'Unrecognized redirection command: {}'.format(r)
                raise XonshError(e)
            targets = ['stdout', 'stderr']
        elif orig in _REDIR_ERR:
            if 'stderr' in streams:
                raise XonshError('Multiple redirects for stderr')
            elif len(dest) > 0:
                e = 'Unrecognized redirection command: {}'.format(r)
                raise XonshError(e)
            targets = ['stderr']
        elif orig in _REDIR_OUT:
            if 'stdout' in streams:
                raise XonshError('Multiple redirects for stdout')
            elif len(dest) > 0:
                e = 'Unrecognized redirection command: {}'.format(r)
                raise XonshError(e)
            targets = ['stdout']
        else:
            raise XonshError('Unrecognized redirection command: {}'.format(r))

        f = _open(loc, mode)
        for t in targets:
            streams[t] = (loc, mode, f)

    else:
        raise XonshError('Unrecognized redirection command: {}'.format(r))


def run_subproc(cmds, captured=False):
    """Runs a subprocess, in its many forms. This takes a list of 'commands,'
    which may be a list of command line arguments or a string, representing
    a special connecting character.  For example::

        $ ls | grep wakka

    is represented by the following cmds::

        [['ls'], '|', ['grep', 'wakka']]

    Lastly, the captured argument affects only the last real command.
    """
    env = builtins.__xonsh_env__
    background = False
    procinfo = {}
    if cmds[-1] == '&':
        background = True
        cmds = cmds[:-1]
    _pipeline_group = None
    write_target = None
    last_cmd = len(cmds) - 1
    procs = []
    prev_proc = None
    _capture_streams = captured in {'stdout', 'object'}
    for ix, cmd in enumerate(cmds):
        starttime = time.time()
        procinfo['args'] = list(cmd)
        stdin = None
        stderr = None
        if isinstance(cmd, str):
            continue
        streams = {}
        while True:
            if len(cmd) >= 3 and _is_redirect(cmd[-2]):
                _redirect_io(streams, cmd[-2], cmd[-1])
                cmd = cmd[:-2]
            elif len(cmd) >= 2 and _is_redirect(cmd[-1]):
                _redirect_io(streams, cmd[-1])
                cmd = cmd[:-1]
            elif len(cmd) >= 3 and cmd[0] == '<':
                _redirect_io(streams, cmd[0], cmd[1])
                cmd = cmd[2:]
            else:
                break
        # set standard input
        if 'stdin' in streams:
            if prev_proc is not None:
                raise XonshError('Multiple inputs for stdin')
            stdin = streams['stdin'][-1]
            procinfo['stdin_redirect'] = streams['stdin'][:-1]
        elif prev_proc is not None:
            stdin = prev_proc.stdout
        # set standard output
        _stdout_name = None
        _stderr_name = None
        if 'stdout' in streams:
            if ix != last_cmd:
                raise XonshError('Multiple redirects for stdout')
            stdout = streams['stdout'][-1]
            procinfo['stdout_redirect'] = streams['stdout'][:-1]
        elif ix != last_cmd:
            stdout = PIPE
        elif _capture_streams:
            _nstdout = stdout = tempfile.NamedTemporaryFile(delete=False)
            _stdout_name = stdout.name
        elif builtins.__xonsh_stdout_uncaptured__ is not None:
            stdout = builtins.__xonsh_stdout_uncaptured__
        else:
            stdout = None
        # set standard error
        if 'stderr' in streams:
            stderr = streams['stderr'][-1]
            procinfo['stderr_redirect'] = streams['stderr'][:-1]
        elif captured == 'object' and ix == last_cmd:
            _nstderr = stderr = tempfile.NamedTemporaryFile(delete=False)
            _stderr_name = stderr.name
        elif builtins.__xonsh_stderr_uncaptured__ is not None:
            stderr = builtins.__xonsh_stderr_uncaptured__
        uninew = (ix == last_cmd) and (not _capture_streams)
        # find alias
        if callable(cmd[0]):
            alias = cmd[0]
        else:
            alias = builtins.aliases.get(cmd[0], None)
        procinfo['alias'] = alias
        # find binary location, if not callable
        if alias is None:
            binary_loc = locate_binary(cmd[0])
        elif not callable(alias):
            binary_loc = locate_binary(alias[0])
        # implement AUTO_CD
        if (alias is None and
                builtins.__xonsh_env__.get('AUTO_CD') and
                len(cmd) == 1 and
                os.path.isdir(cmd[0]) and
                binary_loc is None):
            cmd.insert(0, 'cd')
            alias = builtins.aliases.get('cd', None)

        if callable(alias):
            aliased_cmd = alias
        else:
            if alias is not None:
                aliased_cmd = alias + cmd[1:]
            else:
                aliased_cmd = cmd
            if binary_loc is not None:
                try:
                    aliased_cmd = get_script_subproc_command(binary_loc,
                                                             aliased_cmd[1:])
                except PermissionError:
                    e = 'xonsh: subprocess mode: permission denied: {0}'
                    raise XonshError(e.format(cmd[0]))
        _stdin_file = None
        if (stdin is not None and
                env.get('XONSH_STORE_STDIN') and
                captured == 'object' and
                __xonsh_commands_cache__.lazy_locate_binary('cat') and
                __xonsh_commands_cache__.lazy_locate_binary('tee')):
            _stdin_file = tempfile.NamedTemporaryFile()
            cproc = Popen(['cat'],
                          stdin=stdin,
                          stdout=PIPE)
            tproc = Popen(['tee', _stdin_file.name],
                          stdin=cproc.stdout,
                          stdout=PIPE)
            stdin = tproc.stdout
        if callable(aliased_cmd):
            prev_is_proxy = True
            bgable = getattr(aliased_cmd, '__xonsh_backgroundable__', True)
            numargs = len(inspect.signature(aliased_cmd).parameters)
            if numargs == 2:
                cls = SimpleProcProxy if bgable else SimpleForegroundProcProxy
            elif numargs == 4:
                cls = ProcProxy if bgable else ForegroundProcProxy
            else:
                e = 'Expected callable with 2 or 4 arguments, not {}'
                raise XonshError(e.format(numargs))
            proc = cls(aliased_cmd, cmd[1:],
                       stdin, stdout, stderr,
                       universal_newlines=uninew)
        else:
            prev_is_proxy = False
            usetee = ((stdout is None) and
                      (not background) and
                      env.get('XONSH_STORE_STDOUT', False))
            cls = TeePTYProc if usetee else Popen
            subproc_kwargs = {}
            if ON_POSIX and cls is Popen:
                def _subproc_pre():
                    if _pipeline_group is None:
                        os.setpgrp()
                    else:
                        os.setpgid(0, _pipeline_group)
                    signal.signal(signal.SIGTSTP, lambda n, f: signal.pause())
                subproc_kwargs['preexec_fn'] = _subproc_pre
            denv = env.detype()
            if ON_WINDOWS:
                # Over write prompt variable as xonsh's $PROMPT does
                # not make much sense for other subprocs
                denv['PROMPT'] = '$P$G'
            try:
                proc = cls(aliased_cmd,
                           universal_newlines=uninew,
                           env=denv,
                           stdin=stdin,
                           stdout=stdout,
                           stderr=stderr,
                           **subproc_kwargs)
            except PermissionError:
                e = 'xonsh: subprocess mode: permission denied: {0}'
                raise XonshError(e.format(aliased_cmd[0]))
            except FileNotFoundError:
                cmd = aliased_cmd[0]
                e = 'xonsh: subprocess mode: command not found: {0}'.format(cmd)
                sug = suggest_commands(cmd, env, builtins.aliases)
                if len(sug.strip()) > 0:
                    e += '\n' + suggest_commands(cmd, env, builtins.aliases)
                raise XonshError(e)
        procs.append(proc)
        prev_proc = proc
        if ON_POSIX and cls is Popen and _pipeline_group is None:
            _pipeline_group = prev_proc.pid
    if not prev_is_proxy:
        add_job({
            'cmds': cmds,
            'pids': [i.pid for i in procs],
            'obj': prev_proc,
            'bg': background
        })
    if (env.get('XONSH_INTERACTIVE') and
            not env.get('XONSH_STORE_STDOUT') and
            not _capture_streams):
        # set title here to get current command running
        try:
            builtins.__xonsh_shell__.settitle()
        except AttributeError:
            pass
    if background:
        return
    if prev_is_proxy:
        prev_proc.wait()
    wait_for_active_job()
    for proc in procs[:-1]:
        try:
            proc.stdout.close()
        except OSError:
            pass
    hist = builtins.__xonsh_history__
    hist.last_cmd_rtn = prev_proc.returncode
    # get output
    output = b''
    if write_target is None:
        if _stdout_name is not None:
            with open(_stdout_name, 'rb') as stdoutfile:
                output = stdoutfile.read()
            try:
                _nstdout.close()
            except:
                pass
            os.unlink(_stdout_name)
        elif prev_proc.stdout not in (None, sys.stdout):
            output = prev_proc.stdout.read()
        if _capture_streams:
            # to get proper encoding from Popen, we have to
            # use a byte stream and then implement universal_newlines here
            output = output.decode(encoding=env.get('XONSH_ENCODING'),
                                   errors=env.get('XONSH_ENCODING_ERRORS'))
            output = output.replace('\r\n', '\n')
        else:
            hist.last_cmd_out = output
        if captured == 'object': # get stderr as well
            named = _stderr_name is not None
            unnamed = prev_proc.stderr not in {None, sys.stderr}
            if named:
                with open(_stderr_name, 'rb') as stderrfile:
                    errout = stderrfile.read()
                try:
                    _nstderr.close()
                except:
                    pass
                os.unlink(_stderr_name)
            elif unnamed:
                errout = prev_proc.stderr.read()
            if named or unnamed:
                errout = errout.decode(encoding=env.get('XONSH_ENCODING'),
                                       errors=env.get('XONSH_ENCODING_ERRORS'))
                errout = errout.replace('\r\n', '\n')
                procinfo['stderr'] = errout

    if getattr(prev_proc, 'signal', None):
        sig, core = prev_proc.signal
        sig_str = SIGNAL_MESSAGES.get(sig)
        if sig_str:
            if core:
                sig_str += ' (core dumped)'
            print(sig_str, file=sys.stderr)
    if (not prev_is_proxy and
            hist.last_cmd_rtn is not None and
            hist.last_cmd_rtn > 0 and
            env.get('RAISE_SUBPROC_ERROR')):
        raise CalledProcessError(hist.last_cmd_rtn, aliased_cmd, output=output)
    if captured == 'stdout':
        return output
    elif captured is not False:
        procinfo['executed_cmd'] = aliased_cmd
        procinfo['pid'] = prev_proc.pid
        procinfo['returncode'] = prev_proc.returncode
        procinfo['timestamp'] = (starttime, time.time())
        if captured == 'object':
            procinfo['stdout'] = output
            if _stdin_file is not None:
                _stdin_file.seek(0)
                procinfo['stdin'] = _stdin_file.read().decode()
                _stdin_file.close()
            return CompletedCommand(**procinfo)
        else:
            return HiddenCompletedCommand(**procinfo)


def subproc_captured_stdout(*cmds):
    """Runs a subprocess, capturing the output. Returns the stdout
    that was produced as a str.
    """
    return run_subproc(cmds, captured='stdout')


def subproc_captured_inject(*cmds):
    """Runs a subprocess, capturing the output. Returns a list of
    whitespace-separated strings in the stdout that was produced."""
    return [i.strip() for i in run_subproc(cmds, captured='stdout').split()]


def subproc_captured_object(*cmds):
    """
    Runs a subprocess, capturing the output. Returns an instance of
    ``CompletedCommand`` representing the completed command.
    """
    return run_subproc(cmds, captured='object')


def subproc_captured_hiddenobject(*cmds):
    """
    Runs a subprocess, capturing the output. Returns an instance of
    ``HiddenCompletedCommand`` representing the completed command.
    """
    return run_subproc(cmds, captured='hiddenobject')


def subproc_uncaptured(*cmds):
    """Runs a subprocess, without capturing the output. Returns the stdout
    that was produced as a str.
    """
    return run_subproc(cmds, captured=False)


def ensure_list_of_strs(x):
    """Ensures that x is a list of strings."""
    if isinstance(x, str):
        rtn = [x]
    elif isinstance(x, Sequence):
        rtn = [i if isinstance(i, str) else str(i) for i in x]
    else:
        rtn = [str(x)]
    return rtn


def list_of_strs_or_callables(x):
    """Ensures that x is a list of strings or functions"""
    if isinstance(x, str) or callable(x):
        rtn = [x]
    elif isinstance(x, Sequence):
        rtn = [i if isinstance(i, str) or callable(i) else str(i) for i in x]
    else:
        rtn = [str(x)]
    return rtn


def load_builtins(execer=None, config=None, login=False, ctx=None):
    """Loads the xonsh builtins into the Python builtins. Sets the
    BUILTINS_LOADED variable to True.
    """
    global BUILTINS_LOADED
    # private built-ins
    builtins.__xonsh_config__ = {}
    builtins.__xonsh_env__ = env = Env(default_env(config=config, login=login))
    builtins.__xonsh_help__ = helper
    builtins.__xonsh_superhelp__ = superhelper
    builtins.__xonsh_pathsearch__ = pathsearch
    builtins.__xonsh_globsearch__ = globsearch
    builtins.__xonsh_regexsearch__ = regexsearch
    builtins.__xonsh_glob__ = globpath
    builtins.__xonsh_expand_path__ = expand_path
    builtins.__xonsh_exit__ = False
    builtins.__xonsh_stdout_uncaptured__ = None
    builtins.__xonsh_stderr_uncaptured__ = None
    if hasattr(builtins, 'exit'):
        builtins.__xonsh_pyexit__ = builtins.exit
        del builtins.exit
    if hasattr(builtins, 'quit'):
        builtins.__xonsh_pyquit__ = builtins.quit
        del builtins.quit
    builtins.__xonsh_subproc_captured_stdout__ = subproc_captured_stdout
    builtins.__xonsh_subproc_captured_inject__ = subproc_captured_inject
    builtins.__xonsh_subproc_captured_object__ = subproc_captured_object
    builtins.__xonsh_subproc_captured_hiddenobject__ = subproc_captured_hiddenobject
    builtins.__xonsh_subproc_uncaptured__ = subproc_uncaptured
    builtins.__xonsh_execer__ = execer
    builtins.__xonsh_commands_cache__ = CommandsCache()
    builtins.__xonsh_all_jobs__ = {}
    builtins.__xonsh_ensure_list_of_strs__ = ensure_list_of_strs
    builtins.__xonsh_list_of_strs_or_callables__ = list_of_strs_or_callables
    # public built-ins
    builtins.XonshError = XonshError
    builtins.XonshBlockError = XonshBlockError
    builtins.XonshCalledProcessError = XonshCalledProcessError
    builtins.evalx = None if execer is None else execer.eval
    builtins.execx = None if execer is None else execer.exec
    builtins.compilex = None if execer is None else execer.compile

    # sneak the path search functions into the aliases
    # Need this inline/lazy import here since we use locate_binary that relies on __xonsh_env__ in default aliases
    builtins.default_aliases = builtins.aliases = Aliases(make_default_aliases())
    if login:
        builtins.aliases.update(load_foreign_aliases(issue_warning=False))
    # history needs to be started after env and aliases
    # would be nice to actually include non-detyped versions.
    builtins.__xonsh_history__ = History(env=env.detype(),
                                         ts=[time.time(), None], locked=True)
    atexit.register(_lastflush)
    for sig in AT_EXIT_SIGNALS:
        resetting_signal_handle(sig, _lastflush)
    BUILTINS_LOADED = True


def _lastflush(s=None, f=None):
    if hasattr(builtins, '__xonsh_history__'):
        builtins.__xonsh_history__.flush(at_exit=True)


def unload_builtins():
    """Removes the xonsh builtins from the Python builtins, if the
    BUILTINS_LOADED is True, sets BUILTINS_LOADED to False, and returns.
    """
    global BUILTINS_LOADED
    env = getattr(builtins, '__xonsh_env__', None)
    if isinstance(env, Env):
        env.undo_replace_env()
    if hasattr(builtins, '__xonsh_pyexit__'):
        builtins.exit = builtins.__xonsh_pyexit__
    if hasattr(builtins, '__xonsh_pyquit__'):
        builtins.quit = builtins.__xonsh_pyquit__
    if not BUILTINS_LOADED:
        return
    names = ['__xonsh_config__',
             '__xonsh_env__',
             '__xonsh_ctx__',
             '__xonsh_help__',
             '__xonsh_superhelp__',
             '__xonsh_pathsearch__',
             '__xonsh_globsearch__',
             '__xonsh_regexsearch__',
             '__xonsh_glob__',
             '__xonsh_expand_path__',
             '__xonsh_exit__',
             '__xonsh_stdout_uncaptured__',
             '__xonsh_stderr_uncaptured__',
             '__xonsh_pyexit__',
             '__xonsh_pyquit__',
             '__xonsh_subproc_captured_stdout__',
             '__xonsh_subproc_captured_inject__',
             '__xonsh_subproc_captured_object__',
             '__xonsh_subproc_captured_hiddenobject__',
             '__xonsh_subproc_uncaptured__',
             '__xonsh_execer__',
             '__xonsh_commands_cache__',
             'XonshError',
             'XonshBlockError',
             'XonshCalledProcessError',
             'evalx',
             'execx',
             'compilex',
             'default_aliases',
             '__xonsh_all_jobs__',
             '__xonsh_ensure_list_of_strs__',
             '__xonsh_list_of_strs_or_callables__',
             '__xonsh_history__',
             ]
    for name in names:
        if hasattr(builtins, name):
            delattr(builtins, name)
    BUILTINS_LOADED = False


@contextmanager
def xonsh_builtins(execer=None):
    """A context manager for using the xonsh builtins only in a limited
    scope. Likely useful in testing.
    """
    load_builtins(execer=execer)
    yield
    unload_builtins()

#
# execer
#
# -*- coding: utf-8 -*-
"""Implements the xonsh executer."""
# amalgamated re
# amalgamated sys
# amalgamated types
# amalgamated inspect
# amalgamated builtins
# amalgamated warnings
# amalgamated from collections import Mapping
# amalgamated xonsh.ast
# amalgamated xonsh.parser
# amalgamated xonsh.tools
# amalgamated xonsh.built_ins
class Execer(object):
    """Executes xonsh code in a context."""

    def __init__(self, filename='<xonsh-code>', debug_level=0, parser_args=None,
                 unload=True, config=None, login=True, xonsh_ctx=None):
        """Parameters
        ----------
        filename : str, optional
            File we are to execute.
        debug_level : int, optional
            Debugging level to use in lexing and parsing.
        parser_args : dict, optional
            Arguments to pass down to the parser.
        unload : bool, optional
            Whether or not to unload xonsh builtins upon deletion.
        config : str, optional
            Path to configuration file.
        xonsh_ctx : dict or None, optional
            Xonsh xontext to load as builtins.__xonsh_ctx__
        """
        parser_args = parser_args or {}
        self.parser = Parser(**parser_args)
        self.filename = filename
        self.debug_level = debug_level
        self.unload = unload
        self.ctxtransformer = CtxAwareTransformer(self.parser)
        load_builtins(execer=self, config=config, login=login, ctx=xonsh_ctx)

    def __del__(self):
        if self.unload:
            unload_builtins()

    def parse(self, input, ctx, mode='exec', transform=True):
        """Parses xonsh code in a context-aware fashion. For context-free
        parsing, please use the Parser class directly or pass in
        transform=False.
        """
        if not transform:
            return self.parser.parse(input, filename=self.filename, mode=mode,
                                     debug_level=(self.debug_level > 1))

        # Parsing actually happens in a couple of phases. The first is a
        # shortcut for a context-free parser. Normally, all subprocess
        # lines should be wrapped in $(), to indicate that they are a
        # subproc. But that would be super annoying. Unfortnately, Python
        # mode - after indentation - is whitespace agnostic while, using
        # the Python token, subproc mode is whitespace aware. That is to say,
        # in Python mode "ls -l", "ls-l", and "ls - l" all parse to the
        # same AST because whitespace doesn't matter to the minus binary op.
        # However, these phases all have very different meaning in subproc
        # mode. The 'right' way to deal with this is to make the entire
        # grammar whitespace aware, and then ignore all of the whitespace
        # tokens for all of the Python rules. The lazy way implemented here
        # is to parse a line a second time with a $() wrapper if it fails
        # the first time. This is a context-free phase.
        tree, input = self._parse_ctx_free(input, mode=mode)
        if tree is None:
            return None

        # Now we need to perform context-aware AST transformation. This is
        # because the "ls -l" is valid Python. The only way that we know
        # it is not actually Python is by checking to see if the first token
        # (ls) is part of the execution context. If it isn't, then we will
        # assume that this line is supposed to be a subprocess line, assuming
        # it also is valid as a subprocess line.
        if ctx is None:
            ctx = set()
        elif isinstance(ctx, Mapping):
            ctx = set(ctx.keys())
        tree = self.ctxtransformer.ctxvisit(tree, input, ctx, mode=mode)
        return tree

    def compile(self, input, mode='exec', glbs=None, locs=None, stacklevel=2,
                filename=None, transform=True):
        """Compiles xonsh code into a Python code object, which may then
        be execed or evaled.
        """
        if filename is None:
            filename = self.filename
        if glbs is None or locs is None:
            frame = inspect.stack()[stacklevel][0]
            glbs = frame.f_globals if glbs is None else glbs
            locs = frame.f_locals if locs is None else locs
        ctx = set(dir(builtins)) | set(glbs.keys()) | set(locs.keys())
        tree = self.parse(input, ctx, mode=mode, transform=transform)
        if tree is None:
            return None  # handles comment only input
        if transform:
            with warnings.catch_warnings():
                # we do some funky things with blocks that cause warnings
                warnings.simplefilter('ignore', SyntaxWarning)
                code = compile(tree, filename, mode)
        else:
            code = compile(tree, filename, mode)
        return code

    def eval(self, input, glbs=None, locs=None, stacklevel=2,
                transform=True):
        """Evaluates (and returns) xonsh code."""
        if isinstance(input, types.CodeType):
            code = input
        else:
            code = self.compile(input=input,
                                glbs=glbs,
                                locs=locs,
                                mode='eval',
                                stacklevel=stacklevel,
                                transform=transform)
        if code is None:
            return None  # handles comment only input
        return eval(code, glbs, locs)

    def exec(self, input, mode='exec', glbs=None, locs=None, stacklevel=2,
                transform=True):
        """Execute xonsh code."""
        if isinstance(input, types.CodeType):
            code = input
        else:
            code = self.compile(input=input,
                                glbs=glbs,
                                locs=locs,
                                mode=mode,
                                stacklevel=stacklevel,
                                transform=transform)
        if code is None:
            return None  # handles comment only input
        return exec(code, glbs, locs)

    def _parse_ctx_free(self, input, mode='exec'):
        last_error_line = last_error_col = -1
        parsed = False
        original_error = None
        while not parsed:
            try:
                tree = self.parser.parse(input,
                                         filename=self.filename,
                                         mode=mode,
                                         debug_level=(self.debug_level > 1))
                parsed = True
            except IndentationError as e:
                if original_error is None:
                    raise e
                else:
                    raise original_error
            except SyntaxError as e:
                if original_error is None:
                    original_error = e
                if (e.loc is None) or (last_error_line == e.loc.lineno and
                                       last_error_col in (e.loc.column + 1,
                                                          e.loc.column)):
                    raise original_error
                last_error_col = e.loc.column
                last_error_line = e.loc.lineno
                idx = last_error_line - 1
                lines = input.splitlines()
                line = lines[idx]
                if input.endswith('\n'):
                    lines.append('')
                if len(line.strip()) == 0:
                    # whitespace only lines are not valid syntax in Python's
                    # interactive mode='single', who knew?! Just ignore them.
                    # this might cause actual sytax errors to have bad line
                    # numbers reported, but should only effect interactive mode
                    del lines[idx]
                    last_error_line = last_error_col = -1
                    input = '\n'.join(lines)
                    continue

                if last_error_line > 1 and lines[idx-1].rstrip()[-1:] == ':':
                    # catch non-indented blocks and raise error.
                    prev_indent = len(lines[idx-1]) - len(lines[idx-1].lstrip())
                    curr_indent = len(lines[idx]) - len(lines[idx].lstrip())
                    if prev_indent == curr_indent:
                        raise original_error
                lexer = self.parser.lexer
                maxcol = find_next_break(line, mincol=last_error_col,
                                         lexer=lexer)
                sbpline = subproc_toks(line, returnline=True,
                                       maxcol=maxcol, lexer=lexer)
                if sbpline is None:
                    # subprocess line had no valid tokens,
                    if len(line.partition('#')[0].strip()) == 0:
                        # likely because it only contained a comment.
                        del lines[idx]
                        last_error_line = last_error_col = -1
                        input = '\n'.join(lines)
                        continue
                    else:
                        # or for some other syntax error
                        raise original_error
                elif sbpline[last_error_col:].startswith('![![') or \
                     sbpline.lstrip().startswith('![!['):
                    # if we have already wrapped this in subproc tokens
                    # and it still doesn't work, adding more won't help
                    # anything
                    raise original_error
                else:
                    if self.debug_level:
                        msg = ('{0}:{1}:{2}{3} - {4}\n'
                               '{0}:{1}:{2}{3} + {5}')
                        mstr = '' if maxcol is None else ':' + str(maxcol)
                        msg = msg.format(self.filename, last_error_line,
                                         last_error_col, mstr, line, sbpline)
                        print(msg, file=sys.stderr)
                    lines[idx] = sbpline
                last_error_col += 3
                input = '\n'.join(lines)
        return tree, input

#
# imphooks
#
# -*- coding: utf-8 -*-
"""Import hooks for importing xonsh source files.

This module registers the hooks it defines when it is imported.
"""
# amalgamated builtins
from importlib.abc import MetaPathFinder, SourceLoader
from importlib.machinery import ModuleSpec
# amalgamated os
# amalgamated sys
# amalgamated xonsh.execer
# amalgamated xonsh.platform
class XonshImportHook(MetaPathFinder, SourceLoader):
    """Implements the import hook for xonsh source files."""

    def __init__(self, *args, **kwargs):
        super(XonshImportHook, self).__init__(*args, **kwargs)
        self._filenames = {}
        self._execer = None

    @property
    def execer(self):
        if hasattr(builtins, '__xonsh_execer__'):
            execer = builtins.__xonsh_execer__
            if self._execer is not None:
                self._execer = None
        elif self._execer is None:
            self._execer = execer = Execer(unload=False)
        else:
            execer = self._execer
        return execer

    #
    # MetaPathFinder methods
    #
    def find_spec(self, fullname, path, target=None):
        """Finds the spec for a xonsh module if it exists."""
        dot = '.'
        spec = None
        path = sys.path if path is None else path
        if dot not in fullname and dot not in path:
            path = [dot] + path
        name = fullname.rsplit(dot, 1)[-1]
        fname = name + '.xsh'
        for p in path:
            if not isinstance(p, str):
                continue
            if not os.path.isdir(p):
                continue
            if fname not in (x.name for x in scandir(p)):
                continue
            spec = ModuleSpec(fullname, self)
            self._filenames[fullname] = os.path.join(p, fname)
            break
        return spec

    #
    # SourceLoader methods
    #
    def get_filename(self, fullname):
        """Returns the filename for a module's fullname."""
        return self._filenames[fullname]

    def get_data(self, path):
        """Gets the bytes for a path."""
        raise NotImplementedError

    def get_code(self, fullname):
        """Gets the code object for a xonsh file."""
        filename = self._filenames.get(fullname, None)
        if filename is None:
            msg = "xonsh file {0!r} could not be found".format(fullname)
            raise ImportError(msg)
        with open(filename, 'r') as f:
            src = f.read()
        src = src if src.endswith('\n') else src + '\n'
        execer = self.execer
        execer.filename = filename
        ctx = {}  # dummy for modules
        code = execer.compile(src, glbs=ctx, locs=ctx)
        return code


sys.meta_path.append(XonshImportHook())

#
# shell
#
# -*- coding: utf-8 -*-
"""The xonsh shell"""
# amalgamated os
random = _LazyModule.load('random', 'random')
# amalgamated builtins
# amalgamated from warnings import warn
# amalgamated xonsh.xontribs
# amalgamated xonsh.environ
# amalgamated xonsh.execer
# amalgamated xonsh.platform
# amalgamated xonsh.tools
class Shell(object):
    """Main xonsh shell.

    Initializes execution environment and decides if prompt_toolkit or
    readline version of shell should be used.
    """

    def __init__(self, ctx=None, shell_type=None, config=None, rc=None,
                 **kwargs):
        """
        Parameters
        ----------
        ctx : Mapping, optional
            The execution context for the shell (e.g. the globals namespace).
            If none, this is computed by loading the rc files. If not None,
            this no additional context is computed and this is used
            directly.
        shell_type : str, optional
            The shell type to start, such as 'readline', 'prompt_toolkit',
            or 'random'.
        config : str, optional
            Path to configuration file.
        rc : list of str, optional
            Sequence of paths to run control files.
        """
        self.login = kwargs.get('login', True)
        self.stype = shell_type
        self._init_environ(ctx, config, rc,
                           kwargs.get('scriptcache', True),
                           kwargs.get('cacheall', False))
        env = builtins.__xonsh_env__
        # pick a valid shell -- if no shell is specified by the user,
        # shell type is pulled from env
        if shell_type is None:
            shell_type = env.get('SHELL_TYPE')
        if shell_type == 'best' or shell_type is None:
            shell_type = best_shell_type()
        elif shell_type == 'random':
            shell_type = random.choice(('readline', 'prompt_toolkit'))
        if shell_type == 'prompt_toolkit':
            if not has_prompt_toolkit():
                warn('prompt_toolkit is not available, using readline instead.')
                shell_type = 'readline'
            elif not ptk_version_is_supported():
                warn('prompt-toolkit version < v1.0.0 is not supported. '
                     'Please update prompt-toolkit. Using readline instead.')
                shell_type = 'readline'
        env['SHELL_TYPE'] = shell_type
        # actually make the shell
        if shell_type == 'none':
            from xonsh.base_shell import BaseShell as shell_class
        elif shell_type == 'prompt_toolkit':
            from xonsh.ptk.shell import PromptToolkitShell as shell_class
        elif shell_type == 'readline':
            from xonsh.readline_shell import ReadlineShell as shell_class
        else:
            raise XonshError('{} is not recognized as a shell type'.format(
                             shell_type))
        self.shell = shell_class(execer=self.execer,
                                 ctx=self.ctx, **kwargs)
        # allows history garbace colector to start running
        builtins.__xonsh_history__.gc.wait_for_shell = False

    def __getattr__(self, attr):
        """Delegates calls to appropriate shell instance."""
        return getattr(self.shell, attr)

    def _init_environ(self, ctx, config, rc, scriptcache, cacheall):
        self.ctx = {} if ctx is None else ctx
        debug = to_bool_or_int(os.getenv('XONSH_DEBUG', '0'))
        self.execer = Execer(config=config, login=self.login, xonsh_ctx=self.ctx,
                             debug_level=debug)
        self.execer.scriptcache = scriptcache
        self.execer.cacheall = cacheall
        if self.stype != 'none' or self.login:
            # load xontribs from config file
            names = builtins.__xonsh_config__.get('xontribs', ())
            for name in names:
                update_context(name, ctx=self.ctx)
            # load run control files
            env = builtins.__xonsh_env__
            rc = env.get('XONSHRC') if rc is None else rc
            self.ctx.update(xonshrc_context(rcfiles=rc, execer=self.execer, initial=self.ctx))
        self.ctx['__name__'] = '__main__'

#
# main
#
# -*- coding: utf-8 -*-
"""The main xonsh script."""
# amalgamated os
# amalgamated sys
enum = _LazyModule.load('enum', 'enum')
# amalgamated builtins
# amalgamated importlib
# amalgamated from contextlib import contextmanager
# amalgamated argparse
from argparse import ArgumentTypeError
try:
    from setproctitle import setproctitle
except ImportError:
    setproctitle = None

from xonsh import __version__
# amalgamated xonsh.lazyasd
# amalgamated xonsh.environ
# amalgamated xonsh.shell
# amalgamated xonsh.pretty
# amalgamated xonsh.proc
# amalgamated xonsh.jobs
# amalgamated xonsh.tools
# amalgamated xonsh.platform
# amalgamated xonsh.codecache
# amalgamated xonsh.xonfig
pygments = LazyObject(lambda: importlib.import_module('pygments'),
                      globals(), 'pygments')
pyghooks = LazyObject(lambda: importlib.import_module('xonsh.pyghooks'),
                      globals(), 'pyghooks')


def path_argument(s):
    """Return a path only if the path is actually legal

    This is very similar to argparse.FileType, except that it doesn't return
    an open file handle, but rather simply validates the path."""

    s = os.path.abspath(os.path.expanduser(s))
    if not os.path.isfile(s):
        raise ArgumentTypeError('"%s" must be a valid path to a file' % s)
    return s


parser = ArgumentParser(description='xonsh', add_help=False)
parser.add_argument('-h', '--help',
                    dest='help',
                    action='store_true',
                    default=False,
                    help='show help and exit')
parser.add_argument('-V', '--version',
                    dest='version',
                    action='store_true',
                    default=False,
                    help='show version information and exit')
parser.add_argument('-c',
                    help="Run a single command and exit",
                    dest='command',
                    required=False,
                    default=None)
parser.add_argument('-i', '--interactive',
                    help='force running in interactive mode',
                    dest='force_interactive',
                    action='store_true',
                    default=False)
parser.add_argument('-l', '--login',
                    help='run as a login shell',
                    dest='login',
                    action='store_true',
                    default=False)
parser.add_argument('--config-path',
                    help='specify a custom static configuration file',
                    dest='config_path',
                    default=None,
                    type=path_argument)
parser.add_argument('--no-rc',
                    help="Do not load the .xonshrc files",
                    dest='norc',
                    action='store_true',
                    default=False)
parser.add_argument('--no-script-cache',
                    help="Do not cache scripts as they are run",
                    dest='scriptcache',
                    action='store_false',
                    default=True)
parser.add_argument('--cache-everything',
                    help="Use a cache, even for interactive commands",
                    dest='cacheall',
                    action='store_true',
                    default=False)
parser.add_argument('-D',
                    dest='defines',
                    help='define an environment variable, in the form of '
                         '-DNAME=VAL. May be used many times.',
                    metavar='ITEM',
                    action='append',
                    default=None)
parser.add_argument('--shell-type',
                    help='What kind of shell should be used. '
                         'Possible options: readline, prompt_toolkit, random. '
                         'Warning! If set this overrides $SHELL_TYPE variable.',
                    dest='shell_type',
                    choices=('readline', 'prompt_toolkit', 'best', 'random'),
                    default=None)
parser.add_argument('file',
                    metavar='script-file',
                    help='If present, execute the script in script-file'
                         ' and exit',
                    nargs='?',
                    default=None)
parser.add_argument('args',
                    metavar='args',
                    help='Additional arguments to the script specified '
                         'by script-file',
                    nargs=argparse.REMAINDER,
                    default=[])


def _pprint_displayhook(value):
    if value is None:
        return
    builtins._ = None  # Set '_' to None to avoid recursion
    if isinstance(value, HiddenCompletedCommand):
        builtins._ = value
        return
    env = builtins.__xonsh_env__
    if env.get('PRETTY_PRINT_RESULTS'):
        printed_val = pretty(value)
    else:
        printed_val = repr(value)
    if HAS_PYGMENTS and env.get('COLOR_RESULTS'):
        tokens = list(pygments.lex(printed_val, lexer=pyghooks.XonshLexer()))
        print_color(tokens)
    else:
        print(printed_val)  # black & white case
    builtins._ = value


class XonshMode(enum.Enum):
    single_command = 0
    script_from_file = 1
    script_from_stdin = 2
    interactive = 3


def premain(argv=None):
    """Setup for main xonsh entry point, returns parsed arguments."""
    if argv is None:
        argv = sys.argv[1:]
    if setproctitle is not None:
        setproctitle(' '.join(['xonsh'] + argv))
    builtins.__xonsh_ctx__ = {}
    args = parser.parse_args(argv)
    if args.help:
        parser.print_help()
        parser.exit()
    if args.version:
        version = '/'.join(('xonsh', __version__)),
        print(version)
        parser.exit()
    shell_kwargs = {'shell_type': args.shell_type,
                    'completer': False,
                    'login': False,
                    'scriptcache': args.scriptcache,
                    'cacheall': args.cacheall,
                    'ctx': builtins.__xonsh_ctx__}
    if args.login:
        shell_kwargs['login'] = True
    if args.config_path is not None:
        shell_kwargs['config'] = args.config_path
    if args.norc:
        shell_kwargs['rc'] = ()
    setattr(sys, 'displayhook', _pprint_displayhook)
    if args.command is not None:
        args.mode = XonshMode.single_command
        shell_kwargs['shell_type'] = 'none'
    elif args.file is not None:
        args.mode = XonshMode.script_from_file
        shell_kwargs['shell_type'] = 'none'
    elif not sys.stdin.isatty() and not args.force_interactive:
        args.mode = XonshMode.script_from_stdin
        shell_kwargs['shell_type'] = 'none'
    else:
        args.mode = XonshMode.interactive
        shell_kwargs['completer'] = True
        shell_kwargs['login'] = True
    from xonsh import imphooks
    shell = builtins.__xonsh_shell__ = Shell(**shell_kwargs)
    env = builtins.__xonsh_env__
    env['XONSH_LOGIN'] = shell_kwargs['login']
    if args.defines is not None:
        env.update([x.split('=', 1) for x in args.defines])
    env['XONSH_INTERACTIVE'] = args.force_interactive
    if ON_WINDOWS:
        setup_win_unicode_console(env.get('WIN_UNICODE_CONSOLE', True))
    return args


def main(argv=None):
    """Main entry point for xonsh cli."""
    if argv is None:
        argv = sys.argv[1:]
    args = premain(argv)
    env = builtins.__xonsh_env__
    shell = builtins.__xonsh_shell__
    if args.mode == XonshMode.interactive:
        # enter the shell
        env['XONSH_INTERACTIVE'] = True
        ignore_sigtstp()
        if (env['XONSH_INTERACTIVE'] and
                not env['LOADED_CONFIG'] and
                not any(os.path.isfile(i) for i in env['XONSHRC'])):
            print('Could not find xonsh configuration or run control files.',
                  file=sys.stderr)
            xonfig_main(['wizard', '--confirm'])
        shell.shell.cmdloop()
    elif args.mode == XonshMode.single_command:
        # run a single command and exit
        run_code_with_cache(args.command.lstrip(), shell.execer, mode='single')
    elif args.mode == XonshMode.script_from_file:
        # run a script contained in a file
        path = os.path.abspath(os.path.expanduser(args.file))
        if os.path.isfile(path):
            sys.argv = args.args
            env['ARGS'] = [args.file] + args.args
            env['XONSH_SOURCE'] = path
            run_script_with_cache(args.file, shell.execer, glb=shell.ctx,
                                  loc=None, mode='exec')
        else:
            print('xonsh: {0}: No such file or directory.'.format(args.file))
    elif args.mode == XonshMode.script_from_stdin:
        # run a script given on stdin
        code = sys.stdin.read()
        run_code_with_cache(code, shell.execer, glb=shell.ctx, loc=None,
                            mode='exec')
    postmain(args)


def postmain(args=None):
    """Teardown for main xonsh entry point, accepts parsed arguments."""
    if ON_WINDOWS:
        setup_win_unicode_console(enable=False)
    if hasattr(builtins, '__xonsh_shell__'):
        del builtins.__xonsh_shell__


@contextmanager
def main_context(argv=None):
    """Generator that runs pre- and post-main() functions. This has two iterations.
    The first yields the shell. The second returns None but cleans
    up the shell.
    """
    args = premain(argv)
    yield builtins.__xonsh_shell__
    postmain(args)


if __name__ == '__main__':
    main()

