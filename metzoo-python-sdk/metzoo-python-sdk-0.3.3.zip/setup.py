# -*- coding: utf-8 -*-

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='metzoo-python-sdk',
      version='0.3.3',
      description='Python SDK for Metzoo',
      long_description=readme(),
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
      ],
      keywords='metzoo monitoring metric',
      url='https://bitbucket.org/edrans/metzoo-python-sdk',
      author='Edrans',
      author_email='info@edrans.com',
      license='MIT',
      packages=['metzoo'],
      install_requires=['requests'],
      zip_safe=False)
