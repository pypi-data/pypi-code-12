from setuptools import setup, find_packages

import os,sys

# Need numpy to be installed already,
# b/c pip install doesn't work well
# with those packages:

try:
  import numpy,pandas
except ImportError:
  print("You need to install numpy and pandas separately, or use Anaconda")
  sys.exit

sys.path.append(os.path.join(os.getcwd(), 'src'))

test_requirements = []

setup_requirements = []

setup(
    name = "survey_utils",
    version = "0.0.4",
    packages = find_packages('src', include='survey_utils.math_utils'),
    package_dir = {'':'src'},

    # Dependencies on other packages:
    setup_requires   = setup_requirements,
    tests_require    = test_requirements,
    install_requires = test_requirements + setup_requirements,

    # Unit tests; they are initiated via 'python setup_math_utils.py test'
    test_suite       = 'survey_utils.math_utils',

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
     #   '': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'hello' package, too:
     #   'hello': ['*.msg'],
    },

    # metadata for upload to PyPI
    author = "Andreas Paepcke",
    author_email = "paepcke@cs.stanford.edu",
    description = "Utilities for matrix-related computations on survey results.",
    license = "BSD",
    keywords = "surveys, survey analytics",
    url = "https://github.com/paepcke/survey_utils",   # project home page, if any
)
