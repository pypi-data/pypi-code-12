"""Setuptools configuration for engine."""

from setuptools import setup
from setuptools import find_packages


with open('README.rst', 'r') as readmefile:

    README = readmefile.read()

setup(
    name='asyncdef.engine',
    version='0.1.1',
    url='https://github.com/asyncdef/engine',
    description='Core event loop implementation.',
    author="Kevin Conway",
    author_email="kevinjacobconway@gmail.com",
    long_description=README,
    license='Apache 2.0',
    packages=[
        'asyncdef',
        'asyncdef.engine',
        'asyncdef.engine.processors',
    ],
    install_requires=[
        'iface<2.0.0',
        'asyncdef.interfaces<2.0.0',
    ],
    extras_require={
        'testing': [
            'pep257',
            'pep8',
            'pyenchant',
            'pyflakes',
            'pylint',
            'pytest',
            'pytest-cov',
        ],
    },
    entry_points={
        'console_scripts': [

        ],
    },
    include_package_data=True,
    zip_safe=False,
)
