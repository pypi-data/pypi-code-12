"""
This includes the Lexical Element classes for:
Lambda -- a lambda function
Var -- a single variable
Apply -- an Expression application of two Lambda's or Apply's
Alias -- a meta-variable containing a Lambda from it's alias
Helper methods are included as well.
"""
from __future__ import print_function


class Lambda(object):
    """
    A Lambda Function in lambda calculus
    """
    def __init__(self, arg, body):
        """
        Lambda C'tor
        :param arg: Variable that is supplied as the function name.
        :param body: Lexical Element to be given as the function's body
        """
        if arg is None or body is None:
            self.body = Var(u'x')
            self.arg = Var(u'x')
        else:
            self.body = body
            self.arg = arg

    def __str__(self):
        """
        Creates a string that can be used in python's eval to create a lambda
        :return: The string to make lambda from eval
        """
        return 'lambda ' + self.arg.__str__() + ': ' + self.body.__str__()


class Apply(object):
    """
    A Expression application in lambda calculus
    """
    def __init__(self, func, arg):
        """
        Apply C'tor
        :param func: The function forming the expression
        :param arg: The argument to be applied to the function
        """
        self.func = func
        self.arg = arg

    def __str__(self):
        """
        Creates a string that can be used in python's eval to create a function
        :return: The string to make function from eval
        """
        if isinstance(self.func, Lambda):
            return '(' + self.func.__str__() + ')(' + self.arg.__str__() + ')'
        return self.func.__str__() + '(' + self.arg.__str__() + ')'


class Var(object):
    """
    A Variable in lambda calculus
    """
    def __init__(self, name):
        """
        Var C'tor
        :param name: the name of the variable.
        """
        self.name = name

    def __str__(self):
        """
        Creates a string that can be used in python's eval to create a variable
        :return: The string to make variable from eval
        """
        return self.name


class Alias(object):
    """
    Meta-Variable containing a lambda caluclus function
    Used for function definition substitution in the repl
    """
    def __init__(self, name):
        """
        Alias C'tor
        :param name: The named alias
        """
        self.name = name


def recursive_none_filter(none_list):
    """
    filters None objects from a list and any inner-lists recursively
    :param none_list: the list to filter
    :return: if none_list is a list,
     then the filtered none_list
     else none_list itself
    """
    if isinstance(none_list, list):
        values = [recursive_none_filter(i)
                  for i in none_list if recursive_none_filter(i) is not None]
        if len(values) is not 0:
            return values
        return None
    return none_list


def replace_alias(obj, defs):
    """
    Recursively replaces aliases with their appropriate lambda functions
    :param obj: The main Lexical element to replace from
    :param defs: The dict of valid aliases and their values
    :return: the mapped lexical element.
    """
    if isinstance(obj, Lambda):
        body, rep = replace_alias(obj.body, defs)
        return Lambda(obj.arg, body), rep
    elif isinstance(obj, Apply):
        func, rep1 = replace_alias(obj.func, defs)
        arg, rep2 = replace_alias(obj.arg, defs)
        return Apply(func, arg), (rep1 or rep2)
    elif isinstance(obj, Alias):
        for definition in defs:
            if obj.name == definition[0]:
                return definition[1], True
    elif isinstance(obj, Var):
        return obj, False
