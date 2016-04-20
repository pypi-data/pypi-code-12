from setuptools import setup, find_packages
import os 
from pip.req import parse_requirements

# hack for working with pandocs
import codecs 
try: 
  codecs.lookup('mbcs') 
except LookupError: 
  utf8 = codecs.lookup('utf-8') 
  func = lambda name, enc=utf8: {True: enc}.get(name=='mbcs') 
  codecs.register(func) 

# install readme
# readme = os.path.join(os.path.dirname(__file__), 'README.md')

# setup
setup(
  name='transpose',
  version='0.4.1',
  description='detect jsonschema in data and transpose into other formats',
  long_description = '',
  classifiers=[
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    ],
  keywords='',
  author='Brian Abelson',
  author_email='brian.abelson@voxmedia.com',
  url='http://github.com/voxmedia/transpose',
  license='MIT',
  packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
  namespace_packages=[],
  include_package_data=False,
  zip_safe=False,
  install_requires=[
    'jsonschema', 'pyyaml', 
  ],
  entry_points={
    'console_scripts': [
      'transpose = transpose:cli'
    ]  
  },
  tests_require=['nose']
)