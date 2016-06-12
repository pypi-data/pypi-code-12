"""
setup.py for xml_preferences

https://github.com/barry-scott/xml-preferences.git

"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
import codecs
import os.path

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with codecs.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

with open('./version.txt') as f:
    version_text = f.read()

def getDevStatusFromVersion():
    if 'a' in version_text:
        return 'Development Status :: 3 - Alpha'

    elif 'b' in version_text:
        return 'Development Status :: 4 - Beta'

    else:
        return 'Development Status :: 5 - Production/Stable'

setup(
    name='xml-preferences',

    version=version_text,

    description='xml-preferences reads and writes preferences infomation from XML files',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/barry-scott/xml-preferences',

    # Author details
    author='Barry Scott',
    author_email='barry@barrys-emacs.org',

    # Choose your license
    license='Apache 2.0',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        getDevStatusFromVersion(),

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
    ],

    # What does your project relate to?
    keywords='development',

    packages=find_packages('Source'),
    package_dir={'':'Source'},
)
