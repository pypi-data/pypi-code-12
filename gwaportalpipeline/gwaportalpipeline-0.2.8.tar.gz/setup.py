from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='gwaportalpipeline',
    version='0.2.8',
    description='Analysis-pipeline for GWA-Portal',
    long_description=long_description,
    url='https://github.com/timeu/gwaportal-analysis-pipeline',
    author='Uemit Seren',
    author_email='uemit.seren@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
	'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='GWAS',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=[
        "celery >= 3.0.19",
        "requests >=1.1.0",
        "numpy >=1.6.1",
        "h5py >=2.1.3",
        "PyGWAS >= 1.0.2"
        ]
)

