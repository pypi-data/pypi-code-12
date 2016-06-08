# -*- coding: utf-8 -*-
import glob
import os


modules = glob.glob(os.path.dirname(__file__) + "/*.py")
__all__ = [os.path.basename(f)[:-3] for f in modules
           if not os.path.basename(f).startswith('_') and
           not f.endswith('__init__.py') and os.path.isfile(f)]

__doc__ = """
malibu's database classes were mainly an experiment with ORM tech using
Python's introspection capabilities, closures, and properties.

The actual ORM class exists as malibu.database.dbmapper.DBMapper
and should be inherited to be used properly.

malibu.database.dbmapper.dbtypeconv is a stub module for installing
adapters into the sqlite3 module.

As of the 0.1.6 release, the DBMapper and dbtypeconv are both
deprecated in favour of external ORM projects with better compatibility.

.. automodule:: malibu.database.dbmapper
   :members:

.. automodule:: malibu.database.dbtypeconv
   :members:

"""
