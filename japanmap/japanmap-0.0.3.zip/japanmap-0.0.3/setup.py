from setuptools import setup

version = '0.0.3'
name = 'japanmap'
short_description = '`japanmap` is a package for Japanese map.'
long_description = """\
`japanmap` is a package for Japanese map.
::
   import matplotlib.pyplot as plt
   from japanmap import japanmap
   plt.imshow(japanmap({1:'blue'}))

Requirements
------------
* Python 3, OpenCV3, Pillow

Features
--------
* nothing

Setup
-----
::

   $ pip install japanmap

History
-------
0.0.1 (2016-6-7)
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
    py_modules=['japanmap'],
    keywords=['japanmap',],
    author='Saito Tsutomu',
    author_email='tsutomu@kke.co.jp',
    url='https://pypi.python.org/pypi/japanmap',
    license='PSFL',
    install_requires=['pillow'],
)