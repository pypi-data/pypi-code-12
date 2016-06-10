"""
Alpha, Beta, and Eta reduction and conversion baselines.
"""
from functools import partial


def redux(func, line, types, lambdas):
    """
    Reduces a line based on the mappings and base function
    :param func: Base function to use for reducing
    :param line: Line to reduce
    :param types: Allowed types to match in line's obj
    :param lambdas: mapping lambdas for each type available in types
    :return: A fully reduced line.
    """
    if func is not None:
        line, rep = func(line, types, lambdas)
        while rep:
            line, rep = func(line, types, lambdas)
    return line


def type_lambdas(obj, applier, types, lambdas):
    """
    Function base partial for redux
    :param obj: Line object to reduce
    :param applier: recursive lambda to allow applying done on any level
    :param types: Allowed type lambdas
    :param lambdas: Type to lambda applicator lambdas
    :return: A tuple of the possibly reduced object and if reduction happened
    """
    if (types is not None) and (lambdas is not None):
        for type_ in types:
            if isinstance(obj, types.get(type_))\
                    and lambdas.get(type_) is not None:
                return lambdas.get(type_)(obj, applier)
    return obj, False


def make_apply(types, lambdas):
    """
    Recursive applying function to itself to allow for full redux usage
    :param types: Allowed Type lambdas
    :param lambdas: Type to lambda applicator lambdas
    :return: The recursive type-mapping applicator
    """
    var = partial(type_lambdas, types=types, lambdas=lambdas)
    return partial(var, apply=var)
