from distutils.core import setup
from distutils.extension import Extension
import Cython
import Cython.Distutils
from Cython.Distutils import build_ext
import os
import numpy
import wget
import zipfile

gco_directory = "gco_src"

files = ['GCoptimization.cpp', 'graph.cpp', 'LinkedBlockList.cpp',
         'maxflow.cpp']

files = [os.path.join(gco_directory, f) for f in files]
files.insert(0, "gco_python.pyx")

# download src files
# wget.download("http://vision.csd.uwo.ca/code/gco-v3.0.zip")
wget.download("http://147.228.240.61/queetech/install/gco-v3.0.zip")
if not os.path.exists(gco_directory):
        os.makedirs(gco_directory)
with zipfile.ZipFile('gco-v3.0.zip') as zf:
    zf.extractall(gco_directory)


setup(
        
    name='pygco',
    description='Graph Cut for python',
    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # http://packaging.python.org/en/latest/tutorial.html#version
    version='0.0.7',
    url='https://github.com/mjirik/gco_python',
    author='',
    author_email='',
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Bio-Informatics',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: BSD License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
    ],
    cmdclass={'build_ext': build_ext},
    ext_modules=[Extension("pygco", files, language="c++",
                            include_dirs=[gco_directory, numpy.get_include()],
                            library_dirs=[gco_directory],
                            extra_compile_args=["-fpermissive"])],
    package_data = {'': ['pygco.so']},
    install_requires=['cython', 'wget'],
)
