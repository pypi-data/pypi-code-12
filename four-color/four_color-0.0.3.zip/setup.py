from setuptools import setup

version = '0.0.3'
name = 'four_color'
short_description = '`four_color` is a package for Four Color Problem.'
long_description = """\
`four_color` is a package for Four Color Problem.
::

python -m four_color

Requirements
------------
* Python 3, PIL, pulp

Features
--------
* nothing

Setup
-----
::

   $ pip install four_color

History
-------
0.0.1 (2016-6-13)
~~~~~~~~~~~~~~~~~~
* first release

"""

classifiers = [
   "Development Status :: 1 - Planning",
   "License :: OSI Approved :: Python Software Foundation License",
   "Programming Language :: Python",
   "Topic :: Software Development",
   "Topic :: Scientific/Engineering",
]

setup(
    name=name,
    version=version,
    description=short_description,
    long_description=long_description,
    classifiers=classifiers,
    py_modules=['four_color'],
    keywords=['four_color',],
    author='Saito Tsutomu',
    author_email='tsutomu@kke.co.jp',
    url='https://pypi.python.org/pypi/four_color',
    license='PSFL',
    install_requires=['pulp', ],
)