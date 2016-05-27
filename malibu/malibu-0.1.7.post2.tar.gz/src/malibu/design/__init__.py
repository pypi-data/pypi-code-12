# -*- coding: utf-8 -*-
import glob
import os


modules = glob.glob(os.path.dirname(__file__) + "/*.py")
__all__ = [os.path.basename(f)[:-3] for f in modules
           if not os.path.basename(f).startswith('_') and
           not f.endswith('__init__.py') and os.path.isfile(f)]

__doc__ = """
The classes in this package are essentially small design experiments.
Both pieces have a little bit of history behind them and were/are
intended to replace either a design methodology or another part of
the library. You can read more about their "history" in the class
packages.

.. automodule:: malibu.design.borgish
   :members:

.. automodule:: malibu.design.brine
   :members:

"""
