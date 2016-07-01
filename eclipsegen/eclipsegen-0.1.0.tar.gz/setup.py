from setuptools import setup

setup(
  name='eclipsegen',
  version='0.1.0',
  description='Generate Eclipse instances in Python',
  url='http://github.com/Gohla/eclipsegen',
  author='Gabriel Konat',
  author_email='gabrielkonat@gmail.com',
  license='Apache 2.0',
  packages=['eclipsegen'],
  install_requires=['requests'],
  test_suite='nose.collector',
  tests_require=['nose']
)
