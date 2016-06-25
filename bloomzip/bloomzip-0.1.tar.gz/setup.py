from setuptools import setup

setup(
    name='bloomzip',
    version='0.1',
    description='A module for creating compressed files with a precursory '
                'bloom filter',
    url='https://github.com/stiege/bloomzip',
    author='Alex Hodge',
    author_email='alex.hodge.nz@gmail.com',
    license='MIT',
    packages=['bloomzip'],
    zip_safe=False)