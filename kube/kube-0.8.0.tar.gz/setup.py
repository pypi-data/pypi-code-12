"""Python setuptools build script."""

import sys

import setuptools


__version__ = '0.8.0'


INSTALL_REQUIRES = [
    'requests',
    'http-parser',
    'pyrsistent',
]
if sys.version_info < (3, 4):
    INSTALL_REQUIRES.append('enum34')


CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
    'Topic :: Software Development :: Libraries',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
]


setuptools.setup(
    name='kube',
    version=__version__,
    author='Floris Bruynooghe',
    author_email='flub@cobe.io',
    license='LGPLv3',
    url='http://bitbucket.org/cobeio/kube',
    description='Opinionated interface for the Kubernetes API',
    packages=setuptools.find_packages(),
    install_requires=INSTALL_REQUIRES,
    classifiers=CLASSIFIERS,
    keywords='kubernetes k8s watch',
)
