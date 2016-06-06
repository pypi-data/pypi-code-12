import os

from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open

README_FILENAME = "README.md"
REQ_FILENAME = "requirements.txt"
README = 'Python library for the pentaho BA REST API'
requirements = []

if os.path.isfile(README_FILENAME):
    with open(README_FILENAME) as readme:
        README = readme.read()

if os.path.isfile(REQ_FILENAME):
    with open(REQ_FILENAME) as f:
        requirements = f.read().splitlines()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
        name='pentaho-rest-api',

        version='1.0.19',

        include_package_data=True,

        package_data={
            # If any package contains *.txt or *.rst files, include them:
            '': ['*.txt', '*.md'],
        },

        description='Python library for the pentaho BA REST API',
        long_description='Python library for the pentaho BA REST API',

        # The project's main homepage.
        url='https://github.com/AlayaCare/pentaho-rest-api',

        # Author details
        author='Saqib Khalil Yawar',
        author_email='saqib.yawar@alayacare.com',

        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Build Tools',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'License :: OSI Approved :: GNU General Public License (GPL)'
        ],

        # What does your project relate to?
        keywords='pentaho rest api development',

        packages=find_packages(exclude=['contrib', 'docs', 'tests']),

        # packages=['penapi'],

        install_requires=requirements,

        entry_points={
            'console_scripts': [
                'Pentaho=pentaho:Pentaho',
            ],
        },

        extras_require={
            'dev': requirements,
            'test': requirements,
        },

)
