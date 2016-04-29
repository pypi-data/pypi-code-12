from setuptools import setup

version = '0.1'

setup(name='hpx-bitly',
      version=version,
      description="An API for bit.ly. Forked from bitly-api-python which is not updating the project",
      packages=['bitly'],
      include_package_data=True,
      zip_safe=True,
      )
