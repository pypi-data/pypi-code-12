from setuptools import setup

setup(
    name='DBcm',
    version='1.3',
    description='The Head First Python 2e Database Context Manager',
    author='Paul Barry',
    author_email='paul.james.barry@gmail.com',
    url='http://www.headfirstlabs.com',
    py_modules=['DBcm'],
    dependency_links=['http://dev.mysql.com/downloads/connector/python/'],
)
