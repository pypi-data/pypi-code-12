__author__ = 'ashwin'
"""A Test Lodge based pylodge module.

"""

from setuptools import setup
from codecs import open
from os import path

projectpath = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(projectpath, 'README.rst')) as f:
    long_description = f.read()

setup(
    name='pylodge',
    version='0.3.2',
    description='Test Automation framework for TestLodge',
    long_description=long_description,
    url='https://github.com/gettalent/pylodge',
    author='Ashwin Kondapalli',
    author_email='ashwin@gettalent.com',
    license='MIT',
    classifiers=[

        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Quality Assurance',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',

    ],
    keywords='TestLodge, test automation, pylodge',
    packages=['pylodge'],
    install_requires=['requests']

)
