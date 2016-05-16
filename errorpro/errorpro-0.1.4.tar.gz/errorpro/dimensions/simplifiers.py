# -*- coding: utf-8 -*-

"""

This is a modifed copy of sympy/physics/unitsystems/simplifiers.py and can be
replaced as soon as the changes are released officially by sympy.

Several methods to simplify expressions involving unit objects.
"""

from __future__ import division

from sympy import Add, Mul, Pow, Symbol, Function
from sympy.core.compatibility import reduce
from errorpro.dimensions.dimensions import Dimension


def dim_simplify(expr):
    """
    Simplify expression by recursively evaluating the dimension arguments.

    This function proceeds to a very rough dimensional analysis. It tries to
    simplify expression with dimensions, and it deletes all what multiplies a
    dimension without being a dimension. This is necessary to avoid strange
    behavior when Add(L, L) be transformed into Mul(2, L).
    """

    if isinstance(expr, Dimension):
        return expr

    if isinstance(expr, Symbol):
        return None

    args = []
    for arg in expr.args:
        if isinstance(arg, (Mul, Pow, Add, Symbol, Function)):
            arg = dim_simplify(arg)
        args.append(arg)

    if all([arg!=None and (arg.is_number or (isinstance(arg, Dimension) and arg.is_dimensionless)) for arg in args]):
        return Dimension({})

    if isinstance(expr, Function):
        raise ValueError("Arguments of this function cannot have a dimension: %s" % expr)
    elif isinstance(expr, Pow):
        if isinstance(args[0], Dimension):
            return args[0].pow(args[1])
        else:
            return None
    elif isinstance(expr, Add):
        dimargs = [arg for arg in args if isinstance(arg, Dimension)]
        if (all(isinstance(arg, Dimension) or arg==None for arg in args) or
            all(arg.is_dimensionless for arg in dimargs)):
            if len(dimargs)>0:
                return reduce(lambda x, y: x.add(y), dimargs)
            else:
                return Dimension({})
        else:
            raise ValueError("Dimensions cannot be added: %s" % expr)
    elif isinstance(expr, Mul):
        result = Dimension({})
        for arg in args:
            if isinstance(arg, Dimension):
                result = result.mul(arg)
            elif arg == None:
                return None
        return result

    return None
