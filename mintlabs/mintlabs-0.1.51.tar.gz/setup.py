from distutils.core import setup
from setuptools import find_packages

setup(
    name='mintlabs',
    version='0.1.51',
    url='https://github.com/mint-labs/mintlabs',
    license='MIT',
    author='Mint Labs',
    author_email='gabriel@mint-labs.com',
    description='This is a python API to interact with the Mint-Labs platform.',
    classifiers=['Development Status :: 3 - Alpha',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python :: 3.4'
                 ],
    packages=find_packages(exclude=['docs', 'test*']),
    install_requires=['requests']
)
