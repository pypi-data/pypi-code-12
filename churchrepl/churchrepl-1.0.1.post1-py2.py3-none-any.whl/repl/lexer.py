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

    def replace_alias(self, definitions):
        """
        Replaces all instances of an alias recursively.
        Does not replace new aliases inserted
        :param definitions: ALias dictionary
        :return: the object and whether or not any replacements were made
        """
        self.body, rep = self.body.replace_alias(definitions)
        return self, rep

    def contains_lambda(self, search):
        """
        Returns the number of lambda expressions with the matching Arg
        :param search: arg's name to match
        :return: number of matching sub lambdas
        """
        return (1 if search == self.arg.name else 0) \
            + self.body.contains_lambda(search)

    def alpha(self, parents=None):
        """
        Alpha converts an object.
        :param parents: Parent lambdas to consider in alpha conversion
        :return: alpha conversion equivalent self replaced inplace
        """
        parents = parents or []
        count = self.body.contains_lambda(self.arg.name)
        if count is not 0:
            self.body = self.body.alpha(parents + [self])
            self.arg.name = (
                self.arg.name + str(count)
                if len(self.arg.name) < 2 else
                self.arg.name[0] + str(int(self.arg.name[1:]) + count)
            )
            return self
        if len(parents) is not 0:
            self.body = self.body.alpha(parents + [self])
            return self
        return self


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

    def replace_alias(self, definitions):
        """
        Replaces all instances of an alias recursively.
        Does not replace new aliases inserted
        :param definitions: ALias dictionary
        :return: the object and whether or not any replacements were made
        """
        self.func, rep_func = self.func.replace_alias(definitions)
        self.arg, rep_arg = self.arg.replace_alias(definitions)
        return self, (rep_func or rep_arg)

    def contains_lambda(self, search):
        """
        Returns the number of lambda expressions with the matching Arg
        :param search: arg's name to match
        :return: number of matching sub lambdas
        """
        return self.func.contains_lambda(search) \
            + self.arg.contains_lambda(search)

    def alpha(self, parents=None):
        """
        Alpha converts an object.
        :param parents: Parent lambdas to consider in alpha conversion
        :return: alpha conversion equivalent self replaced inplace
        """
        self.func = self.func.alpha(parents)
        self.arg = self.arg.alpha(parents)
        return self


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

    def replace_alias(self, _):
        """
        Replaces all instances of an alias recursively.
        Does not replace new aliases inserted
        :param _: unused
        :return: the object and whether or not any replacements were made
        """
        return self, False

    @staticmethod
    def contains_lambda(_):
        """
        Returns the number of lambda expressions with the matching Arg
        :param _:  unused
        :return: number of matching sub lambdas
        """
        return 0

    def alpha(self, parents=None):
        """
        Alpha converts an object.
        :param parents: Parent lambdas to consider in alpha conversion
        :return: alpha conversion equivalent self replaced inplace
        """
        parents = parents or []
        for parent in reversed(parents):
            if self.name == parent.arg.name:
                count = parent.body.contains_lambda(self.name)
                if count is not 0:
                    self.name += str(count)
                return self
        return self


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

    def replace_alias(self, definitions):
        """
        Replaces all instances of an alias recursively.
        Does not replace new aliases inserted
        :param definitions: ALias dictionary
        :return: the object and whether or not any replacements were made
        """
        for definition in definitions:
            if self.name == definition[0]:
                return definition[1], True
        raise ValueError('Invalid Alias')


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
