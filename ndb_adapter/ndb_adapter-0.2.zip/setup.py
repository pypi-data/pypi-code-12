from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ndb_adapter',
    version="0.2",
    author='Michal Mrozek',
    author_email='michau.mrozek@student.uj.edu.pl',
    url='https://github.com/Michsior14/ndb_adapter',
    description='Adapter for http://ndbserver.rutgers.edu/ created for biologists, bioinformatics etc.',
    long_description=long_description,
    packages=['ndb_adapter'],
    license='MIT',
    keywords=['ndbserver', 'ndb', 'nucleic acid database', 'adapter'],
    install_requires=['requests', 'xlrd'],
    classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: End Users/Desktop',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3 :: Only',
            'Programming Language :: Python :: 3.0',
            'Programming Language :: Python :: 3.1',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Operating System :: OS Independent',
            'Topic :: Database',
            'Topic :: Internet',
            'Topic :: Scientific/Engineering :: Bio-Informatics',
            'Topic :: Scientific/Engineering :: Chemistry',
            'Topic :: Software Development :: Libraries :: Python Modules',
            ],
    )