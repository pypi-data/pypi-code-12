from setuptools import setup
import sys

with open('README.rst') as f:
    long_description = f.read()

with open('pyorcy/version.py') as f:
    exec(f.read())

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

with open('requirements_test.txt') as f:
    tests_require = f.read().splitlines()

setup(
    name = "pyorcy",
    version = __version__,
    packages = ['pyorcy', 'pyorcy.tests'],
    entry_points = {
        'console_scripts' : [
            'pyorcy = pyorcy.cli:main',
        ]
    },
    author = "Marko Loparic, Francesc Alted",
    author_email = "marko.loparic@gmail.com, faltet@gmail.com",
    description = "Mix Python and Cython code in the same module.",
    long_description = long_description,
    license = "MIT",
    keywords = ('compression', 'applied information theory'),
    url = "https://github.com/blosc/bloscpack",
    install_requires = install_requires,
    extras_require = dict(tests=tests_require),
    tests_require = tests_require,
    classifiers = ['Development Status :: 3 - Alpha',
                   'Environment :: Console',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: Microsoft :: Windows',
                   'Operating System :: POSIX',
                   'Programming Language :: Python',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Utilities',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                  ],
)
