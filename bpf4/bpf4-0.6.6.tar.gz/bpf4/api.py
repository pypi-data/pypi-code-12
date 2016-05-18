import os as _os

from . import (core, util)
from .util import (
    warped, _bpfconstr, minimum, maximum, 
    max_, min_, sum_, select, asbpf,
    loadbpf
    )
from .core import (
    blend, brentq
    # interp_linear, interp_halfcos, interp_halfcos2, 
    # interp_fib, interp_halfcosexpm, interp_halfcos2m, 
    # interp_expon, interp_exponm
)


def linear(*args):
    """
    Example: define an linear BPF with points = 0:0, 1:5, 2:20

    These all do the same thing:

    linear(0, 0, 1, 5, 2, 20)  # fast but rather unclear
    linear((0, 0), (1, 5), (2, 20))
    linear({0:0, 1:5, 2:20})
    """
    return _bpfconstr('linear', *args)


def expon(*args, **kws):
    """
    Example: define an exponential BPF with exp=2 and points = 0:0, 1:5, 2:20

    These all do the same thing:

    expon(2, 0, 0, 1, 5, 2, 20)  # fast but rather unclear
    expon(2, (0, 0), (1, 5), (2, 20))
    expon(2, {0:0, 1:5, 2:20})
    expon(0, 0, 1, 5, 2, 20, exp=2)
    expon((0,0), (1, 5), (2, 20), exp=2)
    expon({0:0, 1:5, 2:20}, exp=2)
    """
    return _bpfconstr('expon', *args, **kws)


def halfcos(*args, **kws):
    """
    halfcos(x0, y0, x1, y1, ..., xn, yn)
    halfcos((x0, y0), (x1, y1), ..., (xn, yn))
    halfcos({x0:y0, x1:y1, x2:y2})

    As a first parameter you can define an exp:

    halfcos(exp, x0, y0, x1, y1, ..., xn, yn)

    Or as a keyword argument at the end:
    halfcos(x0, y0, x1, y1, ..., xn, yn, exp=0.5)

    """
    return _bpfconstr('halfcos', *args, **kws)


def halfcosexp(*args, **kws):
    """
    Example: define an exponential halfcos BPF with exp=2 and points = 0:0, 1:5, 2:20

    These all do the same thing:

    halfcosexp(2, 0, 0, 1, 5, 2, 20)  # fast but rather unclear
    halfcosexp(2, (0, 0), (1, 5), (2, 20))
    halfcosexp(2, {0:0, 1:5, 2:20})
    halfcosexp(0, 0, 1, 5, 2, 20, exp=2)
    halfcosexp((0,0), (1, 5), (2, 20), exp=2)
    halfcosexp({0:0, 1:5, 2:20}, exp=2)
    """
    return _bpfconstr('halfcosexp', *args, **kws)


def halfcosm(*args, **kws):
    return _bpfconstr('halfcosexpm', *args, **kws)


def halfcos2(*args, **kws):
    return _bpfconstr('halfcos2', *args, **kws)


def halfcos2m(*args, **kws):
    return _bpfconstr('halfcos2m', *args, **kws)


def spline(*args):
    """
    Example: define a spline BPF with points = 0:0, 1:5, 2:20

    These all do the same thing:

    spline(0, 0, 1, 5, 2, 20)  # fast but rather unclear
    spline((0, 0), (1, 5), (2, 20))
    spline({0:0, 1:5, 2:20})
    """
    return _bpfconstr('spline', *args)


def uspline(*args):
    return _bpfconstr('uspline', *args)


def fib(*args):
    """
    Example: define a fib BPF with points = 0:0, 1:5, 2:20

    These all do the same thing:

    fib(0, 0, 1, 5, 2, 20)  # fast but rather unclear
    fib((0, 0), (1, 5), (2, 20))
    fib({0:0, 1:5, 2:20})
    """
    return _bpfconstr('fib', *args)


def nointerpol(*args):
    """
    Example: define an nointerpol BPF with points = 0:0, 1:5, 2:20

    These all do the same thing:

    nointerpol(0, 0, 1, 5, 2, 20)  # fast but rather unclear
    nointerpol((0, 0), (1, 5), (2, 20))
    nointerpol({0:0, 1:5, 2:20})

    nointerpol().fromseq(0, 0, 1, 5, 2, 20)
    nointerpol().fromxy([0, 1, 5], [0, 5, 20])
    """
    return _bpfconstr('nointerpol', *args)


def nearest(*args):
    """
    a BPF with nearest interpolation
    """
    return _bpfconstr('nearest', *args)


def multi(*args):
    """
    Example: define the following BPF  
    (0,0) --linear-- (1,10) --expon(3)-- (2,3) --expon(3)-- (10, -1) --halfcos-- (20,0)

    multi(
        0, 0, 
        1, 10, 'linear', 
        2, 3, 'expon(3)', 
        10, -1,       # assumes previus interpolation
        20, 0, 'halfcos')
    multi(
         0, 0, 
        (1, 10, 'linear'), 
        (2, 3, 'expon(3)), 
        (10, -1), 
        (20, 0, 'halfcos')
    )
    """
    xs, ys, interpolations = util._multi_parse_args(args)
    return core.Multi(xs, ys, interpolations)


def pchip(*args):
    """
    Monotonic Cubic Hermite Intepolation

    These all do the same thing:

    pchip(0, 0, 1, 5, 2, 20)  # fast but rather unclear
    pchip((0, 0), (1, 5), (2, 20))
    pchip({0:0, 1:5, 2:20})

    pchip().fromseq(0, 0, 1, 5, 2, 20)
    pchip().fromxy([0, 1, 5], [0, 5, 20])
    """
    import pyinterp
    args = util._parseargs(*args)
    if args:
        return pyinterp.Pchip(args.xs, args.ys)


def const(value):
    """
    a constant bpf

    >>> c5 = const(5)
    >>> c5(10) 
    5
    """
    return core.Const(value)


def slope(slope, offset=0, keepslope=True):
    """
    generate a straight line with the given slope and offset (the 
    same as linear(0, offset, 1, slope)
    """
    return core.Slope(slope, offset)
