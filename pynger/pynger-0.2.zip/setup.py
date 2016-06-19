# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='pynger',
    version='0.2',
    packages=['pynger'],
    url='http://www.haikson.com/myprojects/pynger/',
    license='Apache 2',
    author='Kamo Petrosyan',
    author_email='kamo@haikson.com',
    install_requires=['requests'],
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
    ],
    description='According to the search engines to change the file saytmap.xml'
)
