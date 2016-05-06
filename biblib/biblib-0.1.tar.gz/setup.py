import sys
import os
from setuptools import setup
from biblib import __version__
from setuptools.command.test import test as TestCommand

class Tox(TestCommand):
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]
    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        errno = tox.cmdline(args=args)
        sys.exit(errno)

# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'biblib',
    version = __version__,
    author = 'Frank Roemer',
    author_email = 'froemer76@googlemail.com',
    description = ("A library to handle BibTeX bibliographic data."),
    license = "MIT",
    keywords = "BibTeX ISBN DOI citation",
    url = "http://pythonhosted.org/biblib",
    packages=['biblib',
              'biblib/dev'
              ],
    package_data={'': ['README', 'LICENSE', 'requirements.txt']},
    include_package_data=True,
    long_description=read('README'),
    install_requires=read('requirements.txt').splitlines(),
    tests_require=['tox'],
    cmdclass = {'tests': Tox},
    classifiers=[
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: General',
        'Topic :: Text Processing :: Markup :: LaTeX',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ]
)
