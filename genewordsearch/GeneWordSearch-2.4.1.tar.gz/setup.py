# Basic Setup Script
# Requires Python3

# Written by Joseph Jeffers

import os
import glob
from setuptools import setup, find_packages
from setuptools.command.install import install

class SetupDBFolder(install):
    def run(self):
        os.makedirs(os.getenv('GWS_STORE', '~/.gws/'), exist_ok=True)
        install.run(self)

setup(name='GeneWordSearch',
version='2.4.1',
license='GPLv2',
description='Annotation finder for genes.',
author='Joe Jeffers',
author_email='jeffe174@umn.edu',
url='https://github.com/monprin/geneWordSearch/',
packages=find_packages(),
cmdclass={'install': SetupDBFolder},
data_files=[
(os.getenv('GWS_STORE', '~/.gws/')+'maize', list(glob.glob('genewordsearch/databases/maize/*.*'))),
(os.getenv('GWS_STORE', '~/.gws/')+'ath', list(glob.glob('genewordsearch/databases/ath/*.*')))
],
package_data={
'genewordsearch.databases':['*/totalWordCounts.*','*/geneNotes.*'],
'webapp':['templates/home.html','static/formProcess.js']},
long_description=open('README.rst').read(),
scripts=['bin/gws'],
install_requires=['flask','numpy','scipy'])
