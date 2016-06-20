from setuptools import setup
from setuptools.extension import Extension
from Cython.Build import cythonize
import numpy
import cython_gsl

extensions = [
    Extension('slda._topic_models', ['slda/_topic_models.pyx'],
              libraries=cython_gsl.get_libraries(),
              library_dirs=[cython_gsl.get_library_dir()],
              include_dirs=[numpy.get_include(), cython_gsl.get_include()],),
]

setup(
    name='slda',
    version='0.1.4',
    description='''Cython implementations of Gibbs sampling for latent
    Dirichlet allocation and its supervised variants''',
    url='https://github.com/Savvysherpa/slda',
    author='Berton Earnshaw, Mimi Felicilda',
    author_email='bearnshaw@savvysherpa.com, lfelicilda@savvysherpa.com',
    packages=[
        'slda',
    ],
    setup_requires=['Cython >= 0.20.1', 'cythongsl'],
    install_requires=[
        'numpy',
        'pypolyagamma-3',
        'pytest',
        'scikit-learn',
        'scipy',
    ],
    ext_modules=cythonize(extensions),
    keywords=['lda', 'slda', 'supervised', 'latent', 'Dirichlet', 'allocation'],
)
