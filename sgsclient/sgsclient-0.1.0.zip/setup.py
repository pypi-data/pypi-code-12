from setuptools import setup, find_packages

import sgsclient


def readme():
      with open('README.rst') as f:
            return f.read()

setup(name='sgsclient',
      version=sgsclient.version,
      description='The python client library for the Stratum Game Server.',
      long_description=readme(),
      keywords=['sgsclient'],
      url='https://github.com/stratumgs/stratumgs-python-client',
      author='David Korhumel',
      author_email='dpk2442@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[],
      include_package_data=True,
      zip_safe=False)
