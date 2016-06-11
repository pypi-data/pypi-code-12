from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name = 'HashTable',
    version = '0.1a',
    long_description = readme(),
    url = 'https://github.com/munendrasn/hash',
    author = 'S N Munendra',
    author_email = 'sn.munendra52@gmail.com',
    description = 'Simple HashTable implementation in Python',
    packages = ['hash'] ,
    license = 'MIT',
    zip_safe=False
)
