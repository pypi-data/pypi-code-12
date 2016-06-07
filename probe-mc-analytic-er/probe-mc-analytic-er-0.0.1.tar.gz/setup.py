from setuptools import find_packages
from setuptools.command.test import test as TestCommand
import sys, os
from numpy.distutils.core import setup, Extension

version = '0.0.1'

def get_package_data(name, extlist):
    """Return data files for package *name* with extensions in *extlist*"""
    #modified slightly from taken from http://code.google.com/p/winpython/source/browse/setup.py 2013-11-7
    flist = []
    # Workaround to replace os.path.relpath (not available until Python 2.6):
    offset = len(name)+len(os.pathsep)
    for dirpath, _dirnames, filenames in os.walk(name):
        for fname in filenames:
            if not fname.startswith('.') and os.path.splitext(fname)[1] in extlist:
#                flist.append(osp.join(dirpath, fname[offset:]))
                flist.append(os.path.join(dirpath, fname))
    return flist

class PyTest(TestCommand):

    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        # pylint: disable=W0201
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

# put all install requirements into this list:
requires = [
    'h5py',
    'numpy',
    'scipy',
    'matplotlib',
]

ext_files = get_package_data('probe/mc', ['.f90', '.f95','.F90', '.F95'])
print 'KOKOT ext_files: {}'.format(ext_files)
ext_module_names = ['.'.join(os.path.splitext(v)[0].split(os.path.sep)) for v in ext_files]
print 'KOKOT ext_module_names: {}'.format(ext_module_names)
EXT_MODULES = [Extension(name=x,sources=[ext_files[1], ext_files[0]]) for x in ext_module_names]
print 'KOKOT EXT_MODULES: {}'.format(EXT_MODULES)

#EXT_MODULES = [
#    Extension(name='probe/mc/mc', sources=['probe/mc/ziggurat.f90', 'probe/mc/mc.f90'])
#]

setup(name='probe-mc-analytic-er',
      version=version,
      scripts=['scripts/mc.py'],
      description="Monte Carlo simulation of particle motion in analytic radial field",
      long_description="""\
""",
      classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Petr Zikan',
      author_email='zikan.p@gmail.com',
      url='',
      license='GPLv3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=requires,
      entry_points="""
      # -*- Entry points: -*-
      """,
      tests_require=['pytest'],
      namespace_packages=['probe'],
      cmdclass={'test': PyTest},
      ext_modules=EXT_MODULES,
      )
