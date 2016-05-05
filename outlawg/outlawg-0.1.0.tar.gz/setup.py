import os

from outlawg import __version__, outlawg 
from setuptools import setup, find_packages


here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()

extra_options = {
    'packages': find_packages(),
}


setup(name='outlawg',
      version=__version__,
      description='Not your grandmother\'s logging tool',
      long_description=README,
      classifiers=['Topic :: Software Development :: Quality Assurance',
                   'Topic :: Software Development :: Testing',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 3.4'
                   ],
      keywords='[logging, test]',
      author='Richard Pappalardo',
      author_email='rpappalax@gmail.com',
      license='MPL2',
      include_package_data=True,
      **extra_options
      )
