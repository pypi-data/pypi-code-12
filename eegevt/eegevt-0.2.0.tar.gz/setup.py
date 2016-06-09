from setuptools import setup

with open('README.md') as rfile:
    long_description = rfile.read()

setup(name='eegevt',
      version='0.2.0',
      description='Module for working with various EEG event file formats',
      long_description=long_description,
      url='https://github.com/gjcooper/eegevt',
      author='Gavin Cooper',
      author_email='gjcooper@gmail.com',
      license='GPL v2.0',
      packages=['eegevt'],
      keywords=['EEG', 'event'])
