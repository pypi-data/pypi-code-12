from __future__ import (absolute_import as _absolute_import, 
                        division as _division, print_function)
import numpy as _np
import operator as _operator
import os as _os
from scipy.integrate import quad as _quad
from scipy.optimize import brentq as _brentq
import itertools as _itertools
from . import core
import sys as _sys

PYTHON3 = _sys.version_info.major == 3

_CSV_COLUMN_NAMES = ('x', 'y', 'interpolation', 'exponent')
_constructors = {
    'linear': core.Linear,
    'expon': core.Expon,
    'halfcos': core.Halfcos,
    'nointerpol': core.NoInterpol,
    'halfcosexp': core.HalfcosExp,
    'spline': core.Spline,
    'uspline': core.USpline,
    'fib': core.Fib,
    'slope': core.Slope,
    'halfcos2': core.Halfcos2,
    'nearest': core.Nearest,
    'halfcos2m': core.Halfcos2m,
    'halfcosexpm': core.HalfcosExpm,
    'halfcosm': core.HalfcosExpm
}


def _isiterable(obj):
    try:
        iter(obj)
        if isinstance(obj, basestring):
            return False
        return True
    except TypeError:
        return False


def _iflatten(s):
    """
    return an iterator to the flattened items of sequence s
    strings are not flattened
    """
    try:
        iter(s)
    except TypeError:
        yield s
    else:
        for elem in s:
            if isinstance(elem, basestring):
                yield elem
            else:
                for subelem in _iflatten(elem):
                    yield subelem


def csv_to_bpf(csvfile):
    from em import csvtools
    rows = csvtools.read(csvfile)
    interpolation = rows[0].interpolation
    if all(row.interpolation == interpolation for row in rows[:-1]):
        # all of the same type
        if interpolation in ('expon', 'halfcosexp', 'halfcos2'):
            exp = rows[0].exponent
            constructor = get_bpf_constructor("%s(%.3f)" % (interpolation, exp))
        else:
            constructor = get_bpf_constructor(interpolation)
        numrows = len(rows)
        xs = _np.empty((numrows,), dtype=float)
        ys = _np.empty((numrows,), dtype=float)
        for i in xrange(numrows):
            r = rows[i]
            xs[i] = r.x
            ys[i] = r.y
        return constructor(xs, ys)
    else:
        # multitype
        raise NotImplemented("BPFs with multiple types not implemented YET")


def bpf_to_csv(bpf, csvfile):
    import csv
    csvfile = _os.path.splitext(csvfile)[0] + '.csv'
    try:
        # it follows the 'segments' protocol, returning a seq of (x, y, interpoltype, exp)
        segments = bpf.segments()
        with open(csvfile, 'w') as f:
            w = csv.writer(f)
            w.writerow(_CSV_COLUMN_NAMES)
            w.writerows(segments)
    except AttributeError:
        raise TypeError("BPF must be rendered in order to be written as CSV")

        
def bpf_to_dict(bpf):
    try:
        segment_it = bpf.segments()
    except:
        raise TypeError("this kind of BPF cannot be translated. It must be rendered first.")
    d = {}
    segments = list(segment_it)
    interpolation = segments[0][2]
    # x y interpolation exp
    if all(segment[2] == interpolation for segment in segments[:-1]):
        d['interpolation'] = interpolation
        try:
            exp = bpf.exp
            if exp != 1:
                d['exponent'] = exp
        except:
            pass
        points = [(segment[0], segment[1]) for segment in segments]
        d['points'] = points
    else:
        raise NotImplemented("BPFs with multiple interpolation types are not implemented")
    return d

          
def bpf_to_json(bpf, outfile=None):
    """
    convert this bpf to json format. if outfile is not given, it returns a string, as in dumps
    
    kws are passed directly to json.dump
    """
    try:
        import ujson as json
    except ImportError:
        try:
            import simplejson as json
        except ImportError:
            import json
    d = bpf_to_dict(bpf)
    if outfile is None:
        return json.dumps(d)
    else:
        outfile = _os.path.splitext(outfile)[0] + '.json'
        with open(outfile, 'w') as f:
            json.dump(d, f)    


def _bpf_to_yaml_2(bpf, outfile=None):
    """
    convert this bpf to json format. if outfile is not given, it returns a string, as in dumps
    """
    from cStringIO import StringIO
    try:
        import yaml
    except ImportError:
        raise RuntimeError("PyYAML is needed for yaml support.")
    d = bpf_to_dict(bpf)
    if outfile is None:
        stream = StringIO()
    else:
        outfile = _os.path.splitext(outfile)[0] + '.yaml'
        stream = open(outfile, 'w')
    dumper = yaml.Dumper(stream)
    dumper.add_representer(tuple, lambda du, instance: du.represent_list(instance))
    dumper.add_representer(_np.float64, lambda du, instance: du.represent_float(instance))
    dumper.open()
    dumper.represent(d)
    dumper.close()
    if outfile is None:
        return stream.getvalue()


def _bpf_to_yaml_3(bpf, outfile=None):
    """
    convert this bpf to json format. if outfile is not given, it returns a string, as in dumps
    """
    from io import StringIO
    try:
        import yaml
    except ImportError:
        raise RuntimeError("PyYAML is needed for yaml support.")
    d = bpf_to_dict(bpf)
    if outfile is None:
        stream = StringIO()
    else:
        outfile = _os.path.splitext(outfile)[0] + '.yaml'
        stream = open(outfile, 'w')
    dumper = yaml.Dumper(stream)
    dumper.add_representer(tuple, lambda du, instance: du.represent_list(instance))
    dumper.add_representer(_np.float64, lambda du, instance: du.represent_float(instance))
    dumper.open()
    dumper.represent(d)
    dumper.close()
    if outfile is None:
        return stream.getvalue()
    
if PYTHON3:
    bpf_to_yaml = _bpf_to_yaml_3
else:
    bpf_to_yaml = _bpf_to_yaml_2

    
def dict_to_bpf(d):
    """
    format:

    bpf = {
        'interpolation': 'expon(2)',
        10: 0.1,
        15: 1,
        25: -1
    }
    """
    exp = d.get('exponent')
    interpolation = d.get('interpolation', 'linear')
    if exp is None:
        constructor = get_bpf_constructor(interpolation)
    else:
        constructor = get_bpf_constructor(interpolation, exp)
    if 'points' in d:
        points = d['points']
    else:
        points = [(k, v) for k, v in d.iteritems() if isinstance(k, (int, float))]
    if not points:
        raise ValueError("Curve has no points!")
    points.sort()
    X, Y = zip(*points)
    return constructor.fromxy(X, Y)

    
def loadbpf(path, format='auto'):
    """
    load a bpf saved with dumpbpf

    Possible formats: auto, csv, yaml, json
    """
    if format == 'auto':
        format = _os.path.splitext(path)[-1].lower()[1:]
    assert format in ('csv', 'yaml', 'json')
    if format == 'yaml':
        import yaml
        d = yaml.load(open(path))
    elif format == 'json':
        import json
        d = json.load(path)
    elif format == 'csv':
        return csv_to_bpf(path)
    return dict_to_bpf(d)  

        
def asbpf(obj, bounds=(-_np.inf, _np.inf)):
    if isinstance(obj, core._BpfInterface):
        return obj
    elif callable(obj):
        return core._FunctionWrap(obj, bounds)
    elif hasattr(obj, '__float__'):
        return core.Const(float(obj))
    else:
        raise TypeError("can't wrap %s" % str(obj))

        
# def get_bpf_constructor2(descr):
#     """
#     given a descriptor of an interpolation function, return 
#     a constructor for a BPF with the given interpolation
    
#     Examples:
    
#     c = get_bpf_constructor('linear')
#     bpf = c((0, 1, 2, 3), (0, 10, 5, 30))
#     # this is the same as Linear((0, 1, 2, 3), (0, 10, 5, 30))
    
#     c = get_bpf_constructor('halfcosexp(2.5)')
#     bpf = c((0, 1, 2, 3), (0, 10, 5, 30))
#     # this is the same as HalfcosExp((0, 1, 2, 3), (0, 10, 5, 30), exp=2.5)
#     """
#     constructors = {
#         'linear': core.Linear,
#         'expon': core.Expon,
#         'halfcos': core.Halfcos,
#         'nointerpol': core.NoInterpol,
#         'halfcosexp': core.HalfcosExp,
#         'spline': core.Spline,
#         'uspline': core.USpline
#     }
#     if '(' in descr:
#         func, param = descr.split('(')
#         param = float(param[:-1])
#     elif ':' in descr:
#         func, param = descr.split(':')
#     else:
#         func = descr
#         param = None
#     constructor = constructors.get(func)

#     def f(construcotr, xs, ys, param=None):
#         if param:
#             return constructor(xs, ys, param)
#         return constructor(xs, ys)
#     if constructor:
#         return lambda xs, ys: f(constructor, xs, ys, param)


def _parseargs(*args, **kws):
    """
    convert the args and kws to the canonical form:
    xs, ys, kws
    """
    L = len(args)
    if L == 0:
        return None
    elif L == 1:
        assert isinstance(args, dict)
        items = args[0].items()
        items.sort()
        xs, ys = zip(*items)
    elif L == 2:
        if all(_isiterable(arg) for arg in args):
            if len(args[0]) > 2:   # <--  (xs, ys)
                xs, ys = args
            else:                  # <--  ((x0, y0), (x1, y1))
                xs, ys = zip(*args)
        else:
            return None
    elif L > 2 and not any(map(_isiterable, args)):
        # (x0, y0, x1, y1, ...)
        if L % 2 == 0:  # even
            xs = args[::2]
            ys = args[1::2]
        else:
            assert not kws
            kws = {'exp': args[0]}
            xs = args[1::2]
            ys = args[2::2]
    elif L > 2 and all(map(_isiterable, args)):   # <-- ((x0, y0), (x1, y1), ...)
        xs, ys = zip(*args)
    else:
        raise ValueError("could not parse arguments")
    return (xs, ys, kws)
        

def makebpf(descr, X, Y):
    """
    - descr: a string descriptor of the interpolation
        * linear
        * expon(x)
        * etc.
    - X: the array of xs
    - Y: the array of ys
    """
    return _bpfconstr(descr).fromxy(X, Y)


def _bpfconstr(descr, *args, **kws):
    """
    given a descriptor of an interpolation function, return 
    a constructor for a BPF with the given interpolation

    Examples:

    different ways of defining a bpf with points (0, 0), (1, 100), (2, 20)
    
    bpf('linear', (x0, x1, x2, x3), (y0, y1, y2, y3))

    bpf('linear')
    bpf('linear', 0, 0, 1, 100, 2, 20)
    bpf('linear', {0:0, 1:100, 2:20})
    bpf('linear', (0, 0), (1, 100), (2, 20))
    bpf('linear')(0, 0, 1, 100, 2, 20)
    bpf('linear').fromxy([0, 1, 2], [0, 100, 20])
    bpf('expon', 2)(0, 0, 1, 100, 2, 20)
    bpf('expon', 2, {0:0, 1:100, 2:20})
    bpf('expon(2)', 0, 0, 1, 100, 2, 20)
    bpf('expon:2', 0, 0, 1, 100, 2, 20)
    bpf('expon', 2, 0, 0, 1, 100, 2, 20)
    bpf('expon', 0,0, 1,100, 2,20, exp=2)
    
    Or using the methods defined for each interpolation type:
    
    bpf.linear(0, 0, 1, 100, 2, 20)
    bpf.linear({0:0, 1:100, 2:20})
    bpf.expon(0, 0, 1, 100, 2, 20, exp=2)
    bpf.expon(2, 0, 0, 1, 100, 2, 20)
    bpf.expon(2, (0, 0), (1, 100), (2, 20))
    bpf.halfcos({0:0, 1:100, 2:20}, exp=2)  # if you want a halfcosexp with exp=2
    bpf.halfcos(2, {0:0, 1:100, 2:20})      # if you want a halfcosexp with exp=2
    bpf.halfcos(0, 0, 1, 100, 2, 20)        # a normal halfcos (ie. exp=1)
    
    etc.
    
    """
    param = None
    if '(' in descr:
        descr, param = descr.split('(')
        param = float(param[:-1])    
    elif ':' in descr:
        descr, param = descr.split(':')
    else:
        if kws:
            exp = kws.get('exp')
            if exp is not None:
                param = exp
            if isinstance(args[0], dict):
                args = args[0].items()
                args.sort()
        else:
            l = len(args)
            if l == 1:
                p = args[0]
                if isinstance(p, dict):
                    param = None
                    args = p.items()
                    args.sort()
                elif descr == 'linear':
                    return core.Slope(args[0])
                else:
                    param = p
                    args = ()
            elif l > 1:
                if l == 2 and all(_isiterable(arg) for arg in args) and all(len(arg) > 2 for arg in args):
                    # (x0, x1, x2, ..., xn), (y0, y1, y2, ..., yn)
                    constructor = _constructors.get(descr)
                    return _BpfConstructor(constructor, param).fromxy(*args)
                elif any(_isiterable(arg) for arg in args):
                    if not _isiterable(args[0]):  # exp, (x0, y0), (x1, y1)
                        param = args[0]
                        args = args[1:]
                    elif not _isiterable(args[-1]):  # (x0, y0), (x1, y1), exp
                        param = args[-1]
                        args = args[:-1]
                    else:
                        param = None
                else:
                    if l % 2:  # exp, x0, y0, x1, y1
                        param = args[0]
                        args = args[1:]
                    else:
                        param = None
    constructor = _constructors.get(descr)
    if not constructor:
        raise ValueError("no bpf of type %s" % descr)
    if not args:
        return _BpfConstructor(constructor, param)
    else:
        if isinstance(args[0], dict):
            return _BpfConstructor(constructor, param).fromdict(args[0])
        return _BpfConstructor(constructor, param).fromseq(*args)
        
get_bpf_constructor = _bpfconstr

    
class _BpfConstructor:
    def __init__(self, constructor, exp=None):
        # do minor error checking
        t = constructor.__name__.lower()
        if t in ('halfcos', 'halfcosm'):
            if exp is not None:
                constructor = core.HalfcosExp
            else:
                assert exp is None
        elif t in ('halfcos2', 'halfcos2m', 'halfcosexpm'):
            if exp is None:
                exp = 1
        elif t in ('linear', 'nointerpol', 'nearest', 'spline', 'fib', 'slope', 'uspline'):
            assert exp is None
        else:
            assert exp is not None
        self.constructor = constructor
        self.exp = exp

    def fromseq(self, *seq, **kws):
        k = {'exp':self.exp} if self.exp is not None else {}
        k.update(kws)
        return self.constructor.fromseq(*seq, **k)

    def fromdict(self, d, **kws):
        k = {'exp':self.exp} if self.exp is not None else {}
        k.update(kws)
        return self.constructor.fromdict(d, **k)

    def fromxy(self, xs, ys, **kws):
        k = {'exp':self.exp} if self.exp is not None else {}
        k.update(kws)
        return self.constructor.fromxy(xs, ys, **k)
    __call__ = fromseq

    
# class _Bpf:
#     def __call__(self, descr, *args):
#         """
#         given a descriptor of an interpolation function, return 
#         a constructor for a BPF with the given interpolation

#         Examples:

#         different ways of defining a bpf with points (0, 0), (1, 100), (2, 20)

#         bpf('linear')
#         bpf('linear', 0, 0, 1, 100, 2, 20)
#         bpf('linear', {0:0, 1:100, 2:20})
#         bpf('linear', (0, 0), (1, 100), (2, 20))
#         bpf('linear')(0, 0, 1, 100, 2, 20)
#         bpf('linear').fromxy([0, 1, 2], [0, 100, 20])
#         bpf('expon', 2)(0, 0, 1, 100, 2, 20)
#         bpf('expon', 2, {0:0, 1:100, 2:20})
#         bpf('expon(2)', 0, 0, 1, 100, 2, 20)
#         bpf('expon', 2, 0, 0, 1, 100, 2, 20)
    
#         """
#         return _bpfconstr(descr, *args)

#     @staticmethod
#     def linear(*args):
#         """
#         Example: define an linear BPF with points = 0:0, 1:5, 2:20
        
#         These all do the same thing:
        
#         linear(0, 0, 1, 5, 2, 20)
#         linear((0, 0), (1, 5), (2, 20))
#         linear({0:0, 1:5, 2:20})
        
#         linear().fromseq(0, 0, 1, 5, 2, 20)
#         linear().fromxy([0, 1, 5], [0, 5, 20])
#         """
#         return _bpfconstr('linear', *args)

#     @staticmethod
#     def expon(*args, **kws):
#         """
#         Example: define an exponential BPF with exp=2 and points = 0:0, 1:5, 2:20
        
#         These all do the same thing:
        
#         expon(2, 0, 0, 1, 5, 2, 20)
#         expon(2, (0, 0), (1, 5), (2, 20))
#         expon(2, {0:0, 1:5, 2:20})
#         expon(0, 0, 1, 5, 2, 20, exp=2)
#         expon((0,0), (1, 5), (2, 20), exp=2)
#         expon({0:0, 1:5, 2:20}, exp=2)
#         """
#         return _bpfconstr('expon', *args, **kws)

#     @staticmethod
#     def halfcos(*args, **kws):
#         """
#         halfcos(x0, y0, x1, y1, ..., xn, yn)
#         halfcos((x0, y0), (x1, y1), ..., (xn, yn))
#         halfcos({x0:y0, x1:y1, x2:y2})
        
#         As a first parameter you can define an exp:
        
#         halfcos(exp, x0, y0, x1, y1, ..., xn, yn)
        
#         Or as a keyword argument at the end:
#         halfcos(x0, y0, x1, y1, ..., xn, yn, exp=0.5)
        
#         """
#         return _bpfconstr('halfcos', *args, **kws)

#     @staticmethod
#     def halfcosexp(*args, **kws):
#         """
#         Example: define an exponential halfcos BPF with exp=2 and points = 0:0, 1:5, 2:20
    
#         These all do the same thing:
    
#         halfcosexp(2, 0, 0, 1, 5, 2, 20)
#         halfcosexp(2, (0, 0), (1, 5), (2, 20))
#         halfcosexp(2, {0:0, 1:5, 2:20})
#         halfcosexp(0, 0, 1, 5, 2, 20, exp=2)
#         halfcosexp((0,0), (1, 5), (2, 20), exp=2)
#         halfcosexp({0:0, 1:5, 2:20}, exp=2)
#         """
#         return _bpfconstr('halfcosexp', *args, **kws)

#     @staticmethod
#     def halfcos2(*args, **kws):
#         return _bpfconstr('halfcos2', *args, **kws)

#     @staticmethod
#     def spline(*args):
#         """
#         Example: define an spline BPF with points = 0:0, 1:5, 2:20
    
#         These all do the same thing:
    
#         spline(0, 0, 1, 5, 2, 20)
#         spline((0, 0), (1, 5), (2, 20))
#         spline({0:0, 1:5, 2:20})
    
#         spline().fromseq(0, 0, 1, 5, 2, 20)
#         spline().fromxy([0, 1, 5], [0, 5, 20])
#         """
#         return _bpfconstr('spline', *args)

#     @staticmethod
#     def fib(*args):
#         """
#         Example: define an fib BPF with points = 0:0, 1:5, 2:20

#         These all do the same thing:

#         fib(0, 0, 1, 5, 2, 20)
#         fib((0, 0), (1, 5), (2, 20))
#         fib({0:0, 1:5, 2:20})

#         fib().fromseq(0, 0, 1, 5, 2, 20)
#         fib().fromxy([0, 1, 5], [0, 5, 20])
#         """
#         return _bpfconstr('fib', *args)

#     @staticmethod
#     def nointerpol(*args):
#         """
#         Example: define an nointerpol BPF with points = 0:0, 1:5, 2:20

#         These all do the same thing:

#         nointerpol(0, 0, 1, 5, 2, 20)
#         nointerpol((0, 0), (1, 5), (2, 20))
#         nointerpol({0:0, 1:5, 2:20})

#         nointerpol().fromseq(0, 0, 1, 5, 2, 20)
#         nointerpol().fromxy([0, 1, 5], [0, 5, 20])
#         """
#         return _bpfconstr('nointerpol', *args)

#     @staticmethod
#     def nearest(*args):
#         """
#         a BPF with nearest interpolation
#         """
#         return _bpfconstr('nearest', *args)

#     @staticmethod
#     def multi(*args):
#         """
#         Example: define the following BPF  (0,0) --linear-- (1,10) --expon(3)-- (2,3) --expon(3)-- (10, -1) --halfcos-- (20,0)
        
#         multi(
#             0, 0, 
#             1, 10, 'linear', 
#             2, 3, 'expon(3)', 
#             10, -1,                 # it assumes the same interpolation as the last segment with a known interpolation
#             20, 0, 'halfcos')
#         multi(
#              0, 0, 
#             (1, 10, 'linear'), 
#             (2, 3, 'expon(3)), 
#             (10, -1), 
#             (20, 0, 'halfcos')
#         )
#         multi(
#             0, 0, 'linear', 
#             1, 10, 'expon(3)',
#             10, -1, 'expon(3)',
#             20, 0
#         )
#         """
#         xs, ys, interpolations = _multi_parse_args(args)
#         return core.Multi(xs, ys, interpolations)

#     @staticmethod
#     def const(value):
#         return core.Const(value)

#     @staticmethod
#     def slope(slope, offset=0):
#         return core.Slope(slope, offset)

#     @staticmethod
#     def load(path):
#         format = _os.path.splitext(path)[1][1:].lower()
#         return loadbpf(path, format)

#     @staticmethod
#     def asbpf(obj):
#         return asbpf(obj)


def _multi_parse_args(args):
    flattened_args = list(_iflatten(args))
    if len(flattened_args) == len(args):
        # it is already a flat list
        args = flattened_args
        points = []
        interpolations = []
        point_open = False
        last_interpolation = 'linear'
        interpol_mode = None
        xs = [args[0]]
        ys = [args[1]]
        lasty = ys[0]
        for i, arg in enumerate(args[2:]):
            if not point_open:
                point_open = True
                interpolation = None
                point = []
                if interpol_mode == 'first':
                    if isinstance(arg, basestring):
                        interpolation = arg
                    else:
                        point.append(float(arg))
                        interpolation = last_interpolation
                elif interpol_mode == 'last':
                    point.append(float(arg))
                else:
                    if isinstance(arg, basestring):
                        interpol_mode = 'first'
                        interpolation = arg
                    else:
                        interpol_mode = 'last'
                        point.append(float(arg))
            else:
                L = len(point)
                if interpol_mode == 'first':
                    assert interpolation is not None
                    if L == 0:
                        point.append(float(arg))
                    elif L == 1:
                        point.append(float(arg) if arg is not None else lasty)
                        points.append((point, interpolation))  # <--- 
                        point_open = False
                        lasty = point[1]
                        last_interpolation = interpolation
                        
                    else:
                        raise ValueError
                elif interpol_mode == 'last':
                    if L == 0:
                        raise ValueError
                    elif L == 1:
                        point.append(float(arg) if arg is not None else lasty)
                    elif L == 2:
                        if not isinstance(arg, basestring):
                            interpolation = last_interpolation
                            points.append((point, interpolation))  # <---
                            lasty = point[1]
                            last_interpolation = interpolation
                            point_open = False
                        else:
                            assert interpolation is None
                            interpolation = arg
                            points.append((point, interpolation))  # <---
                            lasty = point[1]
                            last_interpolation = interpolation
                            point_open = False
        if point_open:
            points.append((point, last_interpolation))
        for point, interpolation in points:
            x, y = point
            xs.append(x)
            ys.append(y)
            interpolations.append(interpolation)
        return xs, ys, interpolations
    else:
        # it is of the type (x0, y0), (x1, y1, interpolation), ...
        last_interpolation = 'linear'
        x0, y0 = args[0]
        xs = [x0]
        ys = [y0]
        lasty = y0
        interpolations = []
        for point in args[1:]:  # we skip the first point
            if len(point) == 2:
                interpolation = last_interpolation
                x, y = point
            else:
                x, y = (j for j in point if not isinstance(j, basestring))
                interpolation = (j for j in point if isinstance(j, basestring)).next()
            xs.append(x)
            y = y if y is not None else lasty
            lasty = y
            ys.append(y)
            interpolations.append(interpolation)
        return xs, ys, interpolations    
        
# Bpf = _Bpf()

        
def _bpf_from_pairs(interpolation, pairs):
    xs, ys = zip(*pairs)
    return get_bpf_constructor(interpolation)(xs, ys)

    
def max_(*elements):
    bpfs = map(asbpf, elements)
    return core.Max(*bpfs)

    
def min_(*elements):
    bpfs = map(asbpf, elements)
    return core.Min(*bpfs)

    
def sum_(*elements):
    bpfs = map(asbpf, elements)
    return reduce(_operator.add, bpfs)


def select(which, bpfs):
    """
    which returns at any x, which bpf from bpfs should return the result
    
    >>> which = nointerpol(0, 0, 5, 1)
    >>> bpfs = [linear(0, 0, 10, 10), linear(0, 10, 10, 0)]
    >>> s = select(which, bpfs)
    >>> s(1)     # at time=1, the first bpf will be selected
    0
    """
    return core._BpfSelect(asbpf(which), map(asbpf, bpfs))

    
def dumpbpf(bpf, format='yaml', outfile=None):
    """
    Dump the data of this bpf as human readable text to a file 
    or to a string (if no outfile is given)
    
    If outfile is given, its extension will be used to determine
    the format.

    The bpf can then be reconstructed via `loadbpf`

    Formats supported: csv, yaml, json
    """
    if format == 'csv':
        if outfile is None:
            raise ValueError("need an outfile to dump to CSV")
        return bpf_to_csv(bpf, outfile)
    elif format == 'json':
        return bpf_to_json(bpf, outfile)
    elif format == 'yaml':
        return bpf_to_yaml(bpf, outfile)
    else:
        # we interpret it as a filename, the format should be the extention
        base, ext = _os.path.splitext(format)
        if ext in ('.csv', '.json', '.yaml'):
            outfile = format
            format = ext[1:]
            return dumpbpf(bpf, format, outfile)
        else:
            raise ValueError("format not understood or not supported.")

            
def concat_bpfs(bpfs, fadetime=0, fadeshape='expon(3)'):
    """
    glue these bpfs together, one after the other
    """
    if fadetime != 0:
        raise ValueError("fade not implemented")
    bpfs2 = [bpfs[0]]
    x0, x1 = bpfs[0].bounds()
    xs = [x0]
    for bpf in bpfs[1:]:
        bpf2 = bpf.fit_between(x1, x1 + (bpf._x1 - bpf._x0))
        bpfs2.append(bpf2)
        xs.append(bpf2._x0)
        x0, x1 = bpf2.bounds()
    return core._BpfConcat(xs, bpfs2)

    
def integrate(bpf, bounds=None):
    """
    integrate the given bpf between the given bounds (or use the bpf bounds if not given)
    
    It uses the quad algorithm in scipy.integrate
    """
    if bounds is None:
        x0, x1 = bpf.bounds()
    else:
        x0, x1 = bounds
    return _quad(bpf, x0, x1)[0]


def warped(bpf, dx=None, numpoints=1000):
    """
    bpf represents the curvature of a linear space. the result is a 
    warped bpf so that:
    
    position_bpf | warped_bpf = corresponding position after warping
    
    dx: the accuracy of the measurement
    numpoints: if dx is not given, the bpf is sampled `numpoints` times
               across its bounds
    
    Example:
    find the theoretical position of a given point according to a probability distribution
    
    distribution = bpf.halfcos(0,0, 0.5,1, 1, 0)
    w = warped(distribution)
    original_points = (0, 0.25, 0.33, 0.5)
    warped_points = w.map(original_points)
    """
    x0, x1 = bpf.bounds()
    if dx is None:
        dx = (x1 - x0) / numpoints
    integrated = bpf.integrated()[::dx]
    integrated_at_x1 = integrated(bpf.x1)
    # N = int((x1 + dx - x0) / dx + 0.5)
    xs = _np.arange(x0, x1+dx, dx)    
    ys = _np.ones_like(xs) * _np.nan
    for i in xrange(len(xs)):
        try:
            ys[i] = _brentq(integrated - xs[i]*integrated_at_x1, x0, x1)
        except:
            pass
    return core.Sampled(ys, dx=dx, x0=x0)

        
def _minimize(bpf, N, func=min, debug=False):
    x0, x1 = bpf.bounds()
    xs = _np.linspace(x0, x1, N)
    from scipy.optimize import brent
    mins = [brent(bpf, brack=(xs[i], xs[-i])) for i in xrange(int(len(xs) * 0.5 + 0.5))]
    mins2 = [(bpf(m), m) for m in mins]  # if x0 <= m <= x1]
    if debug:
        print(mins2)
    if mins2:
        return float(func(mins2)[1])
    return None

    
def minimum(bpf, N=10):
    """
    return the x where bpf(x) is the minimum of bpf
    
    N: number of estimates
    """
    return _minimize(bpf, N, min)


def maximum(bpf, N=10):
    """
    return the x where bpf(x) is the maximum of bpf
    """
    return _minimize(-bpf, N, min)
    

def rms(bpf, rmstime=0.1):
    bpf2 = bpf**2
    from math import sqrt

    def func(x):
        return sqrt(bpf2.integrate_between(x, x+rmstime) / rmstime)
    return asbpf(func).set_bounds(bpf.x0, bpf.x1)
 

def binarymask(mask, durs=[1], offset=0, cycledurs=True):
    """
    Creates a binary mask

    mask: a sequence of states. A state is either 0 or 1
          and can be represented also by 'x'(1) or 'o', '-'(0)
    durs: a sequence of durations

    Example
    =======

    mask = create_mask("x--x-x---")


    """
    if cycledurs:
        durs = _itertools.cycle(durs)
    else:
        assert len(durs) == len(mask)

    def binvalue(x):
        d = {'x':1, 'o':0, '-':0, 1:1, 0:0, '1':1, '0':0}
        return d.get(x)

    mask = [binvalue(x) for x in mask]
    mask.append(mask[-1])
    assert all(x is not None for x in mask)
    t = offset
    times = []
    for i, dur in zip(range(len(mask)), durs):
        times.append(t)
        t += dur
    return core.NoInterpol(times, mask)


def create_mask(*args, **kws):
    warnigns.warn("Deprecated! Use binarymask")
    return binarymask(*args, **kws)


def _pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = _itertools.tee(iterable)
    try:
        b.next()
    except StopIteration:
        pass
    return _itertools.izip(a, b)

    
def jagged_band(xs, upperbpf, lowerbpf=0, curve='linear'):
    """
    create a jagged bpf between lowerbpf and upperbpf at the x
    values given by xs
    
    At each x in xs the, the value is equal to lowerbpf, sweeping
    with curvature 'curve' to upperbpf just before the next x
    """
    constructor = get_bpf_constructor(curve)
    upperbpf = asbpf(upperbpf)
    lowerbpf = asbpf(lowerbpf)
    EPSILON = 1e-12
    fragments = []
    if xs[0] > upperbpf.x0 and upperbpf.x0 > float('-inf'):
        xs = [upperbpf.x0] + xs
    if xs[-1] < upperbpf.x1 and upperbpf.x1 < float('inf'):
        xs.append(upperbpf.x1)
    for x0, x1 in _pairwise(xs[:-1]):
        x1 = x1 - EPSILON
        fragment = constructor(x0, lowerbpf(x0), x1, upperbpf(x1))[x0:x1].outbound(0, 0)
        fragments.append(fragment)
    x0 = xs[-2]
    x1 = xs[-1]
    fragments.append(constructor(x0, lowerbpf(x0), x1, upperbpf(x1))[x0:x1].outbound(0, 0))
    return sum_(*fragments)
    

def randombw(randombw, center=1):
    """
    Create a random bpf
    
    randombw: a (time-varying) bandwidth
    center  : the center of the random distribution
    
    if randombw is 0.1 and center is 1, the bpf will render values 
    between 0.95 and 1.05

    NB: this bpf will always be different, since the random numbers
    are calculated as needed. Sample it to freeze it to a known state.

    Example
    =======

    >>> l = bpf.linear(0, 0, 1, 1)
    >>> r = bpf.util.randombw(0.1)
    >>> l2 = (l*r)[::0.01]
    """
    randombw = asbpf(randombw)
    return (randombw.rand() + (center - randombw*0.5))[randombw.x0:randombw.x1]
    

def blendwithfloor(b, mix=0.5):
    return core.blend(b, asbpf(b(maximum(b))), mix)[b.x0:b.x1]
    # return b.blendwith(asbpf(b(minimum(b))), mix)[b.x0:b.x1]

    
def blendwithceil(b, mix=0.5):
    return core.blend(b, asbpf(b(maximum(b))), mix)[b.x0:b.x1]
    # return b.blendwith(asbpf(b(maximum(b))), mix)[b.x0:b.x1]
    
# def blendwithvariance(b, mix=0.5):
#     if b.x0 < minimum(b) < b.x1:
#         return blendwithceil(b, mix)
#     return blendwithfloor(b, mix)


# def smooth(b, window):
#     bi = b.integrated()
#     # bi = b
#     halfwin = window*0.5
#     bsmooth = ((bi << halfwin) - (bi >> halfwin)) * (1./window)  # NB: bi << 2 is the same as bi(x + 2)
#     bsmooth2 = bsmooth[bi.x0 + halfwin:bi.x1 - halfwin][bi.x0:bi.x1]
#     return bsmooth2


def smooth2(b, window, n=7):
    """
    window: length (in the x coord) of the smoothing window
    n: (int) amount of projections to use. Should be an uneven value
    """
    alpha = window / float(n)
    projs_left = [b << (alpha*i) for i in range(int(n / 2))]
    projs_right = [b >> (alpha*i) for i in range(int(n / 2))]
    bsmooth = (sum(projs_left) + sum(projs_right) + b) / (len(projs_left) + len(projs_right) + 1)
    return bsmooth


def smooth(b, window, N=1000):
    """
    b      : a bpf
    window : the width (in x coords) of the smoothing window
    N      : number of points to resample the bpf
    """
    dx = min((b.x1 - b.x0) / N, window/7)
    nwin = int(window / dx)
    box = _np.ones(nwin)/nwin
    Y = b[::dx].ys
    Y2 = _np.convolve(Y, box, mode="same")
    X = _np.linspace(b.x0, b.x1, len(Y2))
    return core.Linear.fromxy(X, Y2)


def linearslice(linearbpf, x0, x1):
    """
    Slice the given bpf, returning a new Linear bpf with endpoints
    x0 and x1.
    """
    assert isinstance(linearbpf, core.Linear)
    X, Y = linearbpf.points()
    insert_head = x0 > X[0]
    if insert_head:
        i = _np.searchsorted(X, x0)
        X = X[i-1:]
        Y = Y[i-1:]
    insert_tail = x1 < X[-1]
    if insert_tail: 
        i = _np.searchsorted(X, x1)
        X = X[:i+1]
        Y = Y[:i+1]
    if insert_head or insert_tail:
        # we copy when we know exactly how much to copy
        X = X.copy()
        Y = Y.copy()
    if insert_head:
        X[0] = x0
        Y[0] = linearbpf(x0)
    if insert_tail:
        X[i] = x1
        Y[i] = linearbpf(x1)    
    return core.Linear(X, Y)

