#
# STIRPLATE, INC. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2016 STIRPLATE, INC., All Rights Reserved.
#
# NOTICE:  All information contained herein is, and remains
# the property of COMPANY. The intellectual and technical
# concepts contained herein are proprietary to COMPANY and
# may be covered by U.S. and Foreign Patents, patents in
# process, and are protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this
# material is strictly forbidden unless prior written permission
# is obtained from COMPANY.  Access to the source code contained
# herein is hereby forbidden to anyone except current COMPANY
# employees, managers or contractors who have executed
# Confidentiality and Non-disclosure agreements explicitly
# covering such access.
#
# The copyright notice above does not evidence any actual or
# intended publication or disclosure  of  this source code, which
# includes information that is confidential and/or proprietary,
# and is a trade secret, of  COMPANY.
#
# ANY REPRODUCTION, MODIFICATION, DISTRIBUTION, PUBLIC  PERFORMANCE,
# OR PUBLIC DISPLAY OF OR THROUGH USE  OF THIS  SOURCE CODE  WITHOUT
# THE EXPRESS WRITTEN CONSENT OF COMPANY IS STRICTLY PROHIBITED,
# AND IN VIOLATION OF APPLICABLE LAWS AND INTERNATIONAL TREATIES.
# THE RECEIPT OR POSSESSION OF  THIS SOURCE CODE AND/OR RELATED
# INFORMATION DOES NOT CONVEY OR IMPLY ANY RIGHTS TO REPRODUCE,
# DISCLOSE OR DISTRIBUTE ITS CONTENTS, OR TO MANUFACTURE, USE,
# OR SELL ANYTHING THAT IT  MAY DESCRIBE, IN WHOLE OR IN PART.
#
import os

from setuptools import setup, find_packages
from codecs import open

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='stirplate',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='1.2.0',

    description='Stirplate Data Uploader',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/stirplate/upload',

    # Author details
    author='The Stirplate, Inc. Team',
    author_email='brett@stirplate.io',

    # Choose your license
    license='MIT',

    packages=find_packages(),
    package_dir={"stirplate": "stirplate"},

    # Add the species data
    package_data={
        'stirplate': [
            os.path.join('species', 'rna.json'),
            os.path.join('species', 'gbs.json')
        ],
    },

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # Development status
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here.
        'Programming Language :: Python',
    ],

    # What does your project relate to?
    keywords='stirplate bioinformatics upload biology genetics genomics proteomics rna dna gbs',

    # List run-time dependencies here.  These will be installed by pip.
    install_requires=['requests', 'mando', 'boto3'],

    # Create an executable script: 'stirplate'
    entry_points={
        'console_scripts': [
            'stirplate=stirplate.stirplate:main',
        ],
    },
)