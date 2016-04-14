from setuptools import setup
from setuptools.command.test import test as TestCommand

with open('README.rst', 'r') as f:
  readme = f.read()

# We can't just import the module and pull out __version__, because the module's
# dependencies might not be installed yet when this file is being run.
with open('handwritingio/version.py', 'r') as f:
  for line in f:
    line = line.strip()
    if line.startswith('__version__ = '):
      version = line.lstrip('__version__ = ').strip("'").strip('"')
      break
  else:
    raise RuntimeError('Unable to find version string')


setup(
  name='handwritingio',
  version=version,
  description='Handwriting.io API client.',
  long_description=readme,
  author='Handwriting.io',
  author_email='support@handwriting.io',
  url='https://github.com/handwritingio/python-client',
  classifiers=(
    'Intended Audience :: Developers',
    'Natural Language :: English',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
  ),
  packages=['handwritingio'],
  license='MIT License',
  install_requires=[
    'pyRFC3339>=1,<2',
    'requests>=2,<3',
    'six>=1.1,<2',
  ],
  setup_requires=['pytest-runner'],
  tests_require=['pytest'],
)
