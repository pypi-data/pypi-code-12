from os.path import dirname, join as pjoin, exists as pexists
from pip.req import parse_requirements
from pip.download import PipSession
from setuptools import setup, find_packages, Extension

VERSION = "0.1.1.post8"

DEPENDENCIES = [
    "cython==0.23",
    "numpy", 
    "scipy", 
    "pandas", 
    "rpy2", 
    "patsy",
    "statsmodels", 
    "joblib", 
    "networkx", 
    "seaborn",
    "pyyaml",
    "scikit-learn",

    "dask",
    "blaze",
    "cloudpickle"
]

#requirements = pjoin(dirname(__file__), "requirements.txt")
#assert pexists(requirements)
#requirements = [str(r.req) for r in parse_requirements(requirements, session=PipSession())]

cmdclass = {}

###################
# Cython extensions
###################

extensions = [
        Extension("wrenlab.correlation",
            sources=["wrenlab/correlation.pyx"],
            extra_compile_args=['-fopenmp'],
            extra_link_args=['-fopenmp'],
            language="c++"),
        Extension("wrenlab.text.ahocorasick.types",
            sources=["wrenlab/text/ahocorasick/types.pyx"],
            language="c++"),
        Extension("wrenlab.text.ahocorasick.algorithm",
            sources=["wrenlab/text/ahocorasick/algorithm.pyx"],
            language="c++")
]

try:
    from Cython.Distutils import build_ext
    cmdclass["build_ext"] = build_ext
except ImportError:
    # FIXME
    pass

include_dirs = []
try:
    import numpy
    include_dirs.append(numpy.get_include())
except ImportError:
    pass

####################
# Package definition
####################

setup(
    name="wrenlab",
    version=VERSION,
    description="Wren Lab bioinformatics utilities",
    author="Cory Giles",
    author_email="mail@corygil.es",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.5",
        "Topic :: Scientific/Engineering :: Bio-Informatics"
    ],
    license="AGPLv3+",

    include_package_data=True,
    py_modules=["mmat", "acfsa"],
    packages=find_packages(),
    install_requires=DEPENDENCIES,
    ext_modules=extensions,
    include_dirs=include_dirs,
    cmdclass=cmdclass

    #py_modules=["mmat", "matrixdb"],
    #entry_points={
    #    "console_scripts": [
    #        "mmat = mmat:cli"
    #    ]
    #},
)
