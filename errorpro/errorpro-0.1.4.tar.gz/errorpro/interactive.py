import errorpro.core
from errorpro import interpreter
from errorpro.parsing.parsing import parse, parse_file

from IPython import get_ipython
from IPython.core.magic import register_line_cell_magic

from sympy import functions as funcs
import sympy

__all__ = ['init', 'load_file', 'save_to_csv', 'calculation']

ns = None

def init(namespace, register_only = False):
    """ function to initialize namespace.
    Args:
     namespace: dictionary representing the namespace to work in
     register_only: bool. If True, namespace will be saved without modifying.
                    If False, IPython will be configured, mathematical functions and
                    constants and ErrorPro functions will be added.
    """

    # save in global variable
    global ns
    ns = namespace

    if not register_only:
        # make matplotlib show plots inline in IPython
        ipython = get_ipython()
        ipython.magic("matplotlib inline")

        # add sympy functions and constants
        ns.update(vars(funcs))
        ns.update({"pi":sympy.pi,
                   "Pi":sympy.pi})
        # TODO: more constants...?

        # add basic errorpro functions
        ns.update(vars(errorpro.core))
        ns.update({"load_file":load_file,
                   "save_to_csv":save_to_csv})

def load_file(filename):
    """
    imports assignments and calculations from file
    """
    global ns

    # parse
    syntax_tree = parse_file(filename)

    # execute
    ns = interpreter.interpret(syntax_tree, ns)

def save_to_csv():
    pass

def calculation(calc):
    """ parses and executes calculation

    Args:
        calc: string of calculation(s) like in data file
    """

    global ns

    # parse
    syntax_tree = parse(calc)

    # execute
    ns = interpreter.interpret(syntax_tree, ns)

@register_line_cell_magic
def eq(line, cell=None):
    if cell is None:
        calculation(line)
    else:
        calculation(cell)
