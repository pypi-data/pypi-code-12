"""
Alpha, Eta, Beta reduction of lambda functions.
"""
from .lexer import Lambda, Var, Apply


def contains_lambda(search, expr):
    """
    Check if an inner lambda has a name clash
    :param search: Name to find
    :param expr: inner lambda to search in
    :return: number of clashes
    """
    if isinstance(expr, Var):
        return 0
    if isinstance(expr, Apply):
        return contains_lambda(search, expr.func) \
               + contains_lambda(search, expr.arg)
    if isinstance(expr, Lambda):
        return (1 if search == expr.arg.name else 0)\
               + contains_lambda(search, expr.body)


def alpha(line, parents=None):
    """
    Alpha conversion of a line in an expression
    :param line: the line to convert
    :param parents: The parent lambdas to search in for conversion
    :return: An alpha converted equivalency to the line.
    """
    parents = parents or []
    if isinstance(line, Lambda):
        count = contains_lambda(line.arg.name, line.body)
        if count is not 0:
            _name = line.arg.name + str(count)
            return Lambda(Var(_name),
                          alpha(line.body, parents+[line])[0]), True
        if len(parents) is not 0:
            body, rep = alpha(line.body, parents + [line])
            return Lambda(line.arg, body), rep
    if isinstance(line, Apply):
        func, rep_func = alpha(line.func, parents)
        arg, rep_arg = alpha(line.arg, parents)
        return Apply(func, arg), (rep_func or rep_arg)
    if isinstance(line, Var):
        for parent in reversed(parents):
            if line.name == parent.arg.name:
                count = contains_lambda(line.name, parent.body)
                if count is not 0:
                    _name = line.name + str(count)
                    return Var(_name), True
                return line, False
    return line, False
