"""
Alpha, Eta, Beta reduction of lambda functions.
"""
from .lexer import Lambda, Var, Apply


def free_vars(expr):
    """
    Returns set of free variables in an expression
    :param expr: the expression to check
    :return: the set of frees
    """
    ret = []
    if isinstance(expr, Var):
        ret = [expr.name]
    elif isinstance(expr, Apply):
        ret = list(free_vars(expr.func)) + list(free_vars(expr.arg))
    elif isinstance(expr, Lambda):
        ret = list(free_vars(expr.body))
    return set(ret)


def alpha(line, outer=None, level=0):
    """
    Alpha conversion of a line in an expression
    :param line: the line to convert
    :param outer: Outer line of object being processed or None
    :param level: Level of process depth
    :return: An alpha converted equivalency to the line.
    """
    outer = outer or line
    if isinstance(line, Var):
        if outer is None or line.name not in free_vars(outer):
            return line
        name = line.name + (str(level-1) if level > 1 else "")
        return Var(name)
    if isinstance(line, Apply):
        return Apply(alpha(line.func, outer, level + 1),
                     alpha(line.arg, outer, level + 1))
    if isinstance(line, Lambda):
        return Lambda(alpha(line.arg, outer, level + 1),
                      alpha(line.body, outer, level + 1))
    return line
