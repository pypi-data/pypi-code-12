
version = '0.2.0'
version_info = (0,2,0)

#Provided for backwards compatibility with old code. In the old code, add to the top:
#import builtins
#builtins.__dero__version__ = '0.1.0'
try: 
    __dero_version__
    if __dero_version__ == '0.1.0':
        from dero.core import *
        from dero.data import *
        from dero.decorators import *
        from dero.latex import *
        from dero.logging import *
        from dero.matplotlib import *
        from dero.multiprocessing import *
        from dero.pandas import *
        from dero.pdf import *
        from dero.selenium import *
        from dero.sympy import *
        from dero.time import *
    else: #stuctured this way so that we can support future structuring changes, can add additional if statements
        __dero_version__ = 'current'
except NameError:
    __dero_version__ = 'current'

if __dero_version__ == 'current':
    import dero.core
    import dero.data
    import dero.decorators
    import dero.latex
    import dero.logging
    import dero.matplotlib
    import dero.multiprocessing
    import dero.pandas
    import dero.pdf
    import dero.selenium
    import dero.sympy
    import dero.time
