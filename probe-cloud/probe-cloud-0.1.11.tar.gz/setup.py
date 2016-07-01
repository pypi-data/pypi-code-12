from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys, os

version = '0.1.11'

# pylint:disable=R0904

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

# are we on readthedocs server?
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
# put all install requirements into this list:
requires = [
    'cleo',
    'psutil',
    'dataset',
    'terminaltables',
    'fabric',
    'probe-log',
    'probe-params',
    'boltons',
]

if on_rtd:
    requires = []
else:
    requires = requires

setup(name='probe-cloud',
      version=version,
      scripts=['probe_cloud.py'],
      description="cloud utils for probe packages",
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
      package_data={'probe.cloud': ['cfg/cloud.cfg', 'fabfile.py', 'cfg/logging.yml']},
      cmdclass={'test': PyTest}
      )
