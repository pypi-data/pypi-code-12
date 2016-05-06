from setuptools import setup, find_packages
from codecs import open
from os import path

with open(path.join(path.abspath(path.dirname(__file__)), 'README.rst'), encoding='utf-8') as f:
    readme = f.read()

setup(
    name='pypirc3',
    version='1.0.0',
    description='command line tool to show and create .pypirc with Python 3',
    long_description=readme,
    url='https://github.com/shirakiya/pypirc3',
    author='shirakiya',
    author_email='shirakiya.pv@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='pypi pypirc cli setup',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[],
    extras_require={
        'dev': [],
        'test': [],
    },
    data_files=[],
    entry_points={
        'console_scripts': [
            'pypirc3=pypirc3.client:main',
        ],
    },
)
