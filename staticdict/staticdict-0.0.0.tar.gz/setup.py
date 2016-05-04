from distutils.core import setup
from Cython.Build import cythonize

setup(
  name = 'staticdict',
  ext_modules = cythonize("staticdict/hashdict_pyx.pyx"),
  packages = ['staticdict'],
  package_dir = {'staticdict':'staticdict'}
)
