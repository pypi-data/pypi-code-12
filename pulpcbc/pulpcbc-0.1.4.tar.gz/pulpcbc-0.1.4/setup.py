from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext


ext_modules = [Extension('pulpcbc',
                         ['pulpcbc.pyx', 'CyEventHandler.cpp'],
                         libraries=['CbcSolver', 'Cbc', 'Cgl', 'Osi', 'OsiClp',
                                    'Clp', 'CoinUtils', 'rt', 'bz2', 'z',
                                    'blas', 'lapack'],
                         extra_compile_args=['-fpermissive'],
                         extra_link_args=['-Wl,--no-as-needed'],
                         language="c++",
                        )]


setup(
    name='pulpcbc',
    version='0.1.4',
    url='https://github.com/opensoft/pulpcbc',
    cmdclass={'build_ext': build_ext},
    ext_modules=ext_modules,
    requires=[
        'Cython',
        'PuLP',
    ],
)
