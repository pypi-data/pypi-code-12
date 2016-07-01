from setuptools import setup

setup(
  name='gradlepy',
  version='0.1.0',
  description='Wrapper for calling Gradle from Python',
  url='http://github.com/Gohla/gradlepy',
  author='Gabriel Konat',
  author_email='gabrielkonat@gmail.com',
  license='Apache 2.0',
  packages=['gradlepy'],
  test_suite='nose.collector',
  tests_require=['nose']
)
