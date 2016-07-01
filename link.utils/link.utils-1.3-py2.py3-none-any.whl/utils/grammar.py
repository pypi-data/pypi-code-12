
from grako.parser import GrakoGrammarGenerator
from grako.codegen import pythoncg

from six import exec_
import imp
import sys


def codegenerator(modname, prefix, grammar):
    """
    Parse grammar model and generate Python code allowing to parse it.

    Example:

    .. code-block:: python

       with open('grammar.bnf') as f:
           module = codegenerator('mydsl', 'MyDSL', f.read())

       assert module.__name__ == 'mydsl'
       parser = module.MyDSLParser()

    :param modname: Name of the generated Python module
    :type modname: str

    :param prefix: Prefix used to name the parser
    :type prefix: str

    :param grammar: Grammar describing the language to parse
    :type grammar: str

    :returns: Generated Python module
    :rtype: module
    """

    parser = GrakoGrammarGenerator(prefix, filename=modname)
    model = parser.parse(grammar)
    code = pythoncg(model)

    module = imp.new_module(modname)
    exec_(code, module.__dict__)
    sys.modules[modname] = module

    return module
