# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


# adapted from https://stackoverflow.com/questions/2467590/dynamically-evaluating-simple-boolean-logic-in-python

def create_token_lst(s, str_to_token):
    """create token list:
    'True or False' -> [True, lambda..., False]"""
    s = s.replace('(', ' ( ')
    s = s.replace(')', ' ) ')
    out = []
    for it in s.split():
        if it in ['not', 'and', 'or']:
            out.append(it)
        else:
            out.append(str_to_token[it])
    return out


def find(lst, what, start=0):
    return [i for i,it in enumerate(lst) if it == what and i >= start]


def parens(token_lst):
    """returns:
        (bool)parens_exist, left_paren_pos, right_paren_pos
    """
    left_lst = find(token_lst, '(')

    if not left_lst:
        return False, -1, -1

    left = left_lst[-1]

    #can not occur earlier, hence there are args and op.
    right = find(token_lst, ')', left + 3)[0]

    return True, left, right


def binary_eval(op, left, right):
    """token_lst has length 3 and format: [left_arg, operator, right_arg]
    operator(left_arg, right_arg) is returned"""
    return op(left, right)

def unary_eval(op, right):
    """token_lst has length 3 and format: [left_arg, operator, right_arg]
    operator(left_arg, right_arg) is returned"""
    return op(right)

def generic_eval(tokens, op_dict):
    if len(tokens) == 0:
        return True
    elif len(tokens) == 1:
        return tokens[0]
    elif len(tokens) == 2:
        return op_dict[tokens[0]](tokens[1]) # unary_eval
    elif len(tokens) == 3:
        try:
            return op_dict[tokens[1]](tokens[0], tokens[2]) # binary_eval
        except:
            print(tokens)
            raise
    elif len(tokens) > 3:
        if len(tokens) % 2 != (1 + tokens.count('not')) % 2:
            raise ValueError('Parsing failed, wrong lenght {} for {} with {} "not"'.format(
                len(tokens), tokens, tokens.count('not')))
        for key in ['not', 'and', 'or']:
            res = find(tokens, key)
            if res:
                k = res[0]
                if key == 'not':
                    mask = slice(k, k+2)
                else:
                    mask = slice(k-1, k+2)
                tokens[mask] = [generic_eval(tokens[mask], op_dict)]
                break
        else:
            raise ValueError("None of 'not', 'and', 'or' found in {}".format(tokens))
        return generic_eval(tokens, op_dict)

def formatted_bool_eval(token_lst, op_dict):
    """eval a formatted (i.e. of the form 'ToFa(ToF)') string"""
    if not token_lst:
        return None

    if len(token_lst) == 1:
        return token_lst[0]

    has_parens, l_paren, r_paren = parens(token_lst)

    if not has_parens:
        return generic_eval(token_lst, op_dict)

    token_lst[l_paren:r_paren+1] = [generic_eval(token_lst[l_paren+1:r_paren], op_dict)]

    return formatted_bool_eval(token_lst, op_dict)


class LogicParser(object):
    def __init__(self, tokens={}):
        self.default_tokens = {'True': True,
                            'False': False,
                            'and': lambda left, right: left and right,
                            'or': lambda left, right: left or right,
                            'not': lambda right: not right,
                            '(':'(',
                            ')':')'}
        self.tokens = tokens

    def __call__(self, expr):
        """The actual 'eval' routine,
        if 'expr' is empty, 'True' is returned,
        otherwise 'expr' is evaluated according to parentheses nesting.
        The format assumed:
            [1] 'LEFT OPERATOR RIGHT',
            where LEFT and RIGHT are either:
                    True or False or '(' [1] ')' (subexpression in parentheses)
        """

        tokens = dict(self.default_tokens)
        tokens.update(self.tokens)

        token_lst = create_token_lst(expr, str_to_token=tokens)
        return formatted_bool_eval(token_lst, op_dict=self.default_tokens)

