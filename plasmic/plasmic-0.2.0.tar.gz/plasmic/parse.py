# Copyright (C) 2016 The Meme Factory, Inc.  http://www.meme.com/

# This file is part of Plasmic.
#
# Plasmic is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Plasmic is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Plasmic.  If not, see <http://www.gnu.org/licenses/>.

# Karl O. Pinc <kop@meme.com>

'''Support the writing of configuration files in Python syntax.

Allow a configuration file to be written in Python syntax, as a Python
dict containing literal values.  Each key/value pair gives a name, the
key, to a configuration value.  Values may themselves be dicts,
allowing for arbitrary levels of nested sections of configuration.

Using the configuration file consists of calling `parse_config()` on
it's content to produce a dict.  Then, typically, referencing the
dict's values by keyword.

'''

import ast

class PyConfError(Exception):
    def __init__(self, msg, node, conf_str):
        self.value = (
            'Error parsing config: line {}: column {}: {}\n{}\n{}'
            .format(node.lineno, node.col_offset, msg,
                    _get_line(conf_str, node.lineno),
                    _col_pointer(node.col_offset)))
    def __str__(self):
        return self.value

def _get_line(conf_str, lineno):
    '''Return the (1-based) line number from the conf string.'''
    return conf_str.split('\n')[lineno - 1]

def _col_pointer(col):
    '''Return a string pointing to the error location.'''
    return '{{:>{col}}}'.format(col=col + 1).format('^')

def _complex_value(conf_str, node):
    '''Node must be a tuple or a singleton literal.'''
    if isinstance(node, ast.Tuple):
        for fieldname, values in ast.iter_fields(node):
            if fieldname == 'elts':
                for child in values:
                    _complex_value(conf_str, child)
    else:
        _singleton(conf_str, node)

def _key_value(node):
    '''Is the node suitable as a dict key?'''
    return (isinstance(node, ast.Num)
            or isinstance(node, ast.Str))
        
def _singleton(conf_str, node):
    '''Node must be a literal that's not a container.'''
    if (not _key_value(node)
        and not isinstance(node, ast.NameConstant)):
        raise PyConfError('Not a literal', node, conf_str)

def _validate_config(conf_str, st):
    '''Allow only nested dicts, strings, numbers, and booleans in
    configs.'''
    if isinstance(st, ast.Dict):
        for fieldname, values in ast.iter_fields(st):
            if fieldname == 'keys':
                for node in values:
                    if not _key_value(node):
                        raise PyConfError(
                            'Not a valid key value', node, conf_str)
            else:
                for node in values:
                    _validate_config(conf_str, node)
    else:
        _complex_value(conf_str, st)
        

def parse_config(conf_str):
    '''Parse a config string, returning a python dict.

    The `conf_str` is a python expression, subject to the following
    restrictions:

     * It must evaluate to a single object, a dict, and be written
       as a literal.

     * Dict values must be written as literals.  They may be dicts,
       tuples, numbers, strings, or literal constants such a True,
       False, None, etc.

     * Dict keys must be written as literals.  They may be numbers or
       strings.

    Comments, indentation, etc., are allowed.  So is arbitrary levels
    of nesting.  What is not allowed is any sort of evaluation.

    Example::

      # Sample configuration file
      { # A configuration dict may contain:
       'alpha': 1,          # numeric literals
       'beta' : 'b',        # string literals
       'gamma': (1, 2, 3 ,  # tuple literals
                  (4, 5)    # tuples may be nested
                ),
       'omega': {           # nested dict literals
           1    : 'first'       # a numeric dict key
           'a'  : 'second'      # a string dict key
           }
      }

    '''
    st = ast.parse(conf_str)
    if not isinstance(st, ast.Module):
        raise PyConfError('not a Module', st, conf_str)

    mod_children = [node for node in ast.iter_child_nodes(st)]
    if len(mod_children) != 1:
        raise PyConfError('unknown Module content', st, conf_str)
    mod_child = mod_children[0]
    if not isinstance(mod_child, ast.Expr):
        raise PyConfError(
            'Module does not contain Expr', mod_child, conf_str)

    expr_children = [node for node in ast.iter_child_nodes(mod_child)]
    if len(expr_children) != 1:
        raise PyConfError('unknown Expr content', mod_child, conf_str)
    expr_child = expr_children[0]
    if not isinstance(expr_child, ast.Dict):
        raise PyConfError('Config is not a dict', expr_child, conf_str)

    _validate_config(conf_str, expr_child)

    return ast.literal_eval(expr_child)
