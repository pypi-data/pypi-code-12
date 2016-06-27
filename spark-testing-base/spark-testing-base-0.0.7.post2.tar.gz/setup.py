from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='spark-testing-base',
    version='0.0.7-2',
    author='Holden Karau',
    author_email='holden@pigscanfly.ca',
    packages=['sparktestingbase', 'sparktestingbase.test'],
    url='https://github.com/Stibbons/python-spark-testing-base',
    # Fork of 'https://github.com/holdenk/spark-testing-base',
    license='LICENSE.txt',
    long_description=readme(),
    description='Spark testing for python',
    install_requires=[
        'unittest2',
        'findspark',
        'pytest',
        'hypothesis'
    ],
    test_requires=[
        'nose',
        'coverage',
        'unittest2'
    ],
)
