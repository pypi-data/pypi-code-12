from setuptools import setup
import os

# Try to load version from local version file
version_filename = 'VERSION'
setup_path = os.path.dirname(os.path.realpath(__file__))
version_path = os.path.join(setup_path, version_filename)
version_file = open(version_path)
version = version_file.read().strip()

# Configure the distribution
setup(name='pyquay',
      version=version,
      description='Quay python client',
      packages=['pyquay'],
      package_dir={'pyquay': 'pyquay'},
      scripts=['bin/quaycli.py'],
      url='https://www.socotra.com',
      maintainer='Chris Antenesse',
      maintainer_email='chris.antenesse@socotra.com',
      license='all rights reserved',
      long_description=open('README.md', 'rt').read())
