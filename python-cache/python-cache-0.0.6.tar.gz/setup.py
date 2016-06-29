from setuptools import setup

import os

# def readPackages():
#     d = os.path.join(os.path.dirname(__file__), "pycache")
#     return [o for o in os.listdir(d) if os.path.isdir(os.path.join(d,o))] + ["pycache"]

def readme():
    return open(os.path.join(os.path.dirname(__file__), 'README.md'), "r").read()

setup(
    name='python-cache',
    packages=['pycache'],
    version='0.0.6',
    description='Pythonic way of Caching',
    long_description=readme(),
    author='python-cache',
    author_email='kevin830222@gmail.com, alan4chen@kimo.com',
    url='https://github.com/python-cache/python-cache',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Intended Audience :: Developers'
    ],
    install_requires=[],
    include_package_data=True,
    license='MIT License',
)

