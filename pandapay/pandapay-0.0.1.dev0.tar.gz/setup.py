import os
import sys
import warnings

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    from distutils.command.build_py import build_py

path, script = os.path.split(sys.argv[0])
os.chdir(os.path.abspath(path))

# Don't import panda module here, since deps may not be installed
sys.path.insert(0, (os.path.dirname(__file__)))
from version import VERSION

setup(
    name='pandapay',
    cmdclass={'build_py': build_py},
    version=VERSION,
    description='PandaPay python bindings',
    author='Panda',
    author_email='support@pandapay.io',
    url='https://github.com/ViralPhilanthropyInc/panda-python',
    packages=['pandaecs'],
    install_requires=['stripe'],
    use_2to3=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ])
