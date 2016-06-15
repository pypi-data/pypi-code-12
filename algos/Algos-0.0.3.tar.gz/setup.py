from distutils.core import setup

modules = [
    #'algos.structures',
    'algos.operations.swap',
    'algos.sorting.insertion_sort'
]


setup(
    name         = 'Algos',
    version      = '0.0.3',
    py_modules   =  modules,
    author       = 'Chitrank Dixit',
    author_email = 'chitrankdixit@gmail.com',
    url          = 'http://chitrank-dixit.github.io',
    description  = 'A simple library that consists of all basic operations and complex algorithm present on the globe' 

)
