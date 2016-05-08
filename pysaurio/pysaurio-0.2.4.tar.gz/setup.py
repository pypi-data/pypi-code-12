from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pysaurio',
    version='0.2.4',
    description='A tool for searching & extracting information from multiple text files.',
    long_description=long_description,
    url='https://pypi.python.org/pypi/pysaurio',
    author='Antonio Suárez Jiménez',
    author_email='pherkad13@gmail.com',
    license='GNU GPLv3',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Utilities',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='pysaurio search extract text csv collect data merge join pyraptor',
    packages=['pysaurio'],
    package_dir = {'pysaurio':'pysaurio'},
)
