from setuptools import setup
from Cython.Build import cythonize

import numpy as np

setup(
    name='pypolyagamma-3',
    version='0.0.1',
    description='Cython wrappers for Polya gamma random number generation based on Jesse Windle\'s BayesLogit package: https://github.com/jwindle/BayesLogit. Forked from original pypolyagamma which is authored by Scott Linderman: https://github.com/slinderman/pypolyagamma.',
    author='Matt Burbidge',
    author_email='mburbidge@savvysherpa.com',
    url='http://www.github.com/Savvysherpa/pypolyagamma',
    license="MIT",
    packages=['pypolyagamma'],
    ext_modules=cythonize('**/*.pyx'),
    include_dirs=[np.get_include(),],
    install_requires=[
        'Cython >= 0.20.1',
        'numpy'
        ],
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Programming Language :: C++',
        ],
    keywords=['monte-carlo', 'polya', 'gamma'],
    platforms="ALL",
)
