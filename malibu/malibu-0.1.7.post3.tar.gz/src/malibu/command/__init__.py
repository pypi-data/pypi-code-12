# -*- coding: utf-8 -*-
import glob
import os
from importlib import import_module
from malibu.util.decorators import function_kw_reg

modules = glob.glob(os.path.dirname(__file__) + "/*.py")
__all__ = [os.path.basename(f)[:-3] for f in modules
           if not os.path.basename(f).startswith('_') and
           not f.endswith('__init__.py') and os.path.isfile(f)]


__doc__ = """
Module for processing commands in a CLI fashion.

.. autofunction:: get_command_modules
.. py:function:: command_module(func, *args, **kw)

   A decorator function that is used to register command modules in the
   :py:data:`~__command_modules` dictionary.

   :param function func: Function being decorator
   :param *args: positional arguments
   :param **kw: keyword arguments
   :type *args: list
   :type **kw: dict
   :return: none
   :rtype: None

.. automodule:: malibu.command.module
"""

__command_modules = {}
command_module = function_kw_reg(__command_modules, ["name", "depends"])


def get_command_modules(package=None):
    """ Reads a package and returns a dictionary of modules decorated with
        the :py:func:`command_module` decorator.

        :param str package: Package to search for command modules
        :return: dictionary of command modules
        :rtype: dict
        :raises AttributeError: if package has no __all__ attribute
    """

    package = __package__ if not package else package
    package_all = import_module(package)
    if not hasattr(package_all, "__all__"):
        raise AttributeError("Package %s has no __all__ attribute" % (package))

    package_all = package_all.__all__

    modules = {}
    deps = set()

    for module in package_all:
        module = import_module("{}.{}".format(package, module))
        # Just importing the code should take care of registration with the
        # decorator.

    for module, kws in __command_modules.items():
        module.depend_modules = kws["depends"]
        for depmod in kws["depends"]:
            deps.add(depmod)
        if kws["name"] in modules:
            # Module is already in map, don't clobber
            continue
        module.BASE_NAME = kws["name"]
        modules.update({kws["name"]: module})

    for module, kws in __command_modules.items():
        for depmod in kws["depends"]:
            if depmod not in modules:
                modules.pop(kws["name"])

    return modules
