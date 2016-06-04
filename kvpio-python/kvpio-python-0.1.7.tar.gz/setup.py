from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='kvpio-python',
    version='0.1.7',
    author='William Palmer',
    author_email='will@steelhive.com',
    description='Official kvp.io python bindings and client',
    long_description=long_description,
    url='https://www.kvp.io',
    include_package_data=True,
    zip_safe=False,
    packages=find_packages(),
    install_requires=[
        'requests',
        'click'
    ],
    tests_require=[
        'pytest',
        'pytest-cov'
    ],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: BSD",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    entry_points={
        'console_scripts': [
            'kvpio = kvpio.cli:cli',
        ]
    }
)
