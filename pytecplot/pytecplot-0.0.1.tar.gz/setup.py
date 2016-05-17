from __future__ import print_function

import re
from codecs import open
from os import path

def long_description():
    here = path.abspath(path.dirname(__file__))
    with open(path.join(here,'README.rst'), encoding='utf-8') as f:
        return f.read()

def read_version():
    here = path.abspath(path.dirname(__file__))
    with open(path.join(here,'tecplot','__init__.py'), encoding='utf-8') as f:
        m = re.search(r"__version__ = '(.*?)'",f.read(),re.M)
        return m.group(1)

def setup_opts():
    opts = dict(
        name='pytecplot',
        version=read_version(),
        description='A python interface to the TecUtil layer of Tecplot 360 EX',
        long_description=long_description(),
        url='http://www.tecplot.com',
        author='Tecplot, Inc.',
        author_email='support@tecplot.com',
        classifiers=[
            # Development Status
            #   1 - Planning
            #   2 - Pre-Alpha
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 1 - Planning',
            'Intended Audience :: Developers',
            'Intended Audience :: Education',
            'Intended Audience :: End Users/Desktop',
            'Intended Audience :: Science/Research',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Topic :: Education',
            'Topic :: Multimedia :: Graphics :: 3D Rendering',
            'Topic :: Multimedia :: Graphics :: Presentation',
            'Topic :: Multimedia :: Graphics :: Viewers',
            'Topic :: Scientific/Engineering',
            'Topic :: Scientific/Engineering :: Information Analysis',
            'Topic :: Scientific/Engineering :: Mathematics',
            'Topic :: Scientific/Engineering :: Physics',
            'Topic :: Scientific/Engineering :: Visualization',
            'Topic :: Software Development :: Libraries',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
        ],
        keywords= [
            'tecplot',
            'cfd',
            'data analysis',
            'scientific',
            'scientific computing',
            'statistics',
            'visualization',
        ],
        packages=['tecplot'],
    )
    return opts

if __name__ == '__main__':
    from setuptools import setup
    setup(**setup_opts())
