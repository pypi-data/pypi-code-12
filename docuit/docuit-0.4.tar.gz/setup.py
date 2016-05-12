#!/usr/bin/env python

from distutils.core import setup

from setuptools import find_packages

from docuit._version import __version__


try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

setup(
    name='docuit',
    version=__version__,
    author='Tobias Wilken',
    author_email='tooangel@tooangel.de',
    maintainer='Tobias Wilken',
    maintainer_email='tooangel@tooangel.de',
    url='https://github.com/TooAngel/docuit',
    description='Docuit is a tool which makes sure your README stays up to date and simplifies getting the needed parts out of the README.',  # noqa
    long_description=long_description,
    download_url='https://pypi.python.org/pypi/docuit',
    license='AGPL-3.0',
    platforms=['Any'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',  # noqa
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Software Development',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Documentation',
        'Topic :: Software Development :: Testing',
        'Topic :: System :: Boot',
        'Topic :: System :: Systems Administration',
        'Topic :: Text Processing :: Markup',
        'Topic :: Utilities'
    ],
    entry_points={
        'console_scripts': [
            'docuit = docuit.__main__:main'
        ]
    },
    packages=find_packages(),
    install_requires=['docopt>=0.6.2'],
)
