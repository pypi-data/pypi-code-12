from setuptools import setup

setup(
  name='buildorchestra',
  version='0.1.0',
  description='Build system orchestration tool',
  url='http://github.com/Gohla/buildorchestra',
  author='Gabriel Konat',
  author_email='g.d.p.konat@tudelft.nl',
  license='Apache 2.0',
  packages=['buildorchestra'],
  install_requires=['toposort'],
  test_suite='nose.collector',
  tests_require=['nose']
)
