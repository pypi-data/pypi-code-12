from distutils.core import setup

import os


def version():
    setupDir = os.path.dirname(os.path.realpath(__file__))
    versionFile = open(os.path.join(setupDir, 'genometk', 'VERSION'))
    return versionFile.read().strip()

setup(
    name='GenomeTk',
    version=version(),
    author='Donovan Parks',
    author_email='donovan.parks@gmail.com',
    packages=['genometk'],
    scripts=['bin/genometk'],
    package_data={'genometk' : ['VERSION', 'data_files/hmms/*']},
    url='http://pypi.python.org/pypi/genometk/',
    license='GPL3',
    description='A toolbox for working with genomes.',
    long_description=open('README.md').read(),
    install_requires=[
        "numpy >= 1.8.0",
        "biolib >= 0.0.11"],
)
