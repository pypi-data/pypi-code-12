"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""


from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='eventbus',
    version='1.1.0',

    description='TCP client module for vertx TCP eventbus bridge',

    url='https://github.com/jaymine/TCP-eventbus-client-Python',

    author='Jayamine Alupotha',
    author_email='Jayamine.alupotha@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='vertx TCP eventbus clients',

    packages=find_packages(exclude=['samples','tests']),

)