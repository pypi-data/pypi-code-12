'''graphstack
'''

from distutils.core import setup
from setuptools import find_packages

CLASSIFIERS = [
'Development Status :: 3 - Alpha',
'Intended Audience :: Developers',
'License :: OSI Approved :: MIT License',
'Programming Language :: Python',
'Programming Language :: Python :: 2.7',
'Programming Language :: Python :: 3.3',
'Programming Language :: Python :: 3.4',
'Programming Language :: Python :: 3.5',
'Operating System :: Microsoft :: Windows',
'Operating System :: POSIX',
'Operating System :: Unix',
'Operating System :: MacOS',
'Natural Language :: English',
]

with open('README.md') as fp:
    LONG_DESCRIPTION = ''.join(fp.readlines())

setup(
    name = 'graphstack',
    version = '0.1.0',
    packages = find_packages(),
    install_requires = ['pycallgraph',
                       ],
    author = 'Brendan Smithyman',
    author_email = 'brendan@3ptscience.com',
    description = 'graphstack',
    long_description = LONG_DESCRIPTION,
    license = 'MIT',
    keywords = 'dictionary class attribute',
    url = 'https://github.com/3ptscience/graphstack',
    download_url = 'https://github.com/3ptscience/graphstack',
    classifiers = CLASSIFIERS,
    platforms = ['Windows', 'Linux', 'Solaris', 'Mac OS-X', 'Unix'],
    use_2to3 = False,
)
