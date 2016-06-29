from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
from os import path
from codecs import open

# Get the long description from the README file
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# Get the version number from cva/version.py
with open(path.join(here, 'cva/_version.py'), encoding='utf-8') as f:
    tmp_version = f.read()
exec(tmp_version)

setup(
    name = 'cva',
    packages = ['cva', 'cva/examples', 'cva/test'],
    package_data = {
        'text_files' : ['*.rst', '*.txt'],
        'readme'     : ['README.rst'],
    },
    version = __version__,
    install_requires=['numpy>=1.11.0', 'matplotlib>=1.5.1'],
    description = 'Calculus of Variations Solver',
    long_description=long_description,
    license='LGPLv2',
    author = 'Robert Whitinger',
    author_email = 'cva_account@wmkt.com',
    url = "http://github.com/robertjw/",
    download_url = "http://github.com/robertjw/",
    keywords = ['calculus', 'variations', 'functional', 'analysis'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5', 
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
)
