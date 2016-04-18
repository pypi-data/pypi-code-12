from distutils.core import setup
from setuptools import find_packages

setup(
    name='ws-amqp',
    version='0.5.1',
    packages=find_packages(exclude=['tests', 'example']),
    url='https://github.com/websuslik/ws-amqp',
    license='MIT',
    author='Yuri Voronkov',
    author_email='websuslik@gmail.com',
    description='',
    test_suite="nose.collector",
    install_requires=['amqp']
)
