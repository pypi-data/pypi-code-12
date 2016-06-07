from setuptools import setup
from cloak import __version__, __author__

setup(
    name='cloak',
    author=__author__,
    author_email="rpcope1@gmail.com",
    url="https://bitbucket.org/rpcope1/cloak",
    version=__version__,
    description="A library of container data structures",
    packages=['cloak'],
    install_requires=[],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: BSD License'
    ]
)
