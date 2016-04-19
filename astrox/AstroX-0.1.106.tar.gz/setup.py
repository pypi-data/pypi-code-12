from distutils.core import setup
from setuptools import setup
setup(
      name = 'AstroX',
      packages = ['astrox'],
      version = '0.1.106',
      description = 'AstroX Python Server',
      author = 'Alexander Simpson',
      author_email = 'as2388@cam.ac.uk',
      url = 'https://github.com/as2388/AstroX',
      #download_url = 'https://github.com/peterldowns/mypackage/tarball/0.1',
      install_requires=[
                        'autobahn',
                        'sense-hat',
                        'pillow',
                        'twisted'
                        ],
      keywords = ['AstroPi', 'Scratch', 'ScratchX'],
      classifiers = [],
      entry_points={
      'console_scripts': [
                          'astrox = astrox.__main__:main',
                          ]
      }
)