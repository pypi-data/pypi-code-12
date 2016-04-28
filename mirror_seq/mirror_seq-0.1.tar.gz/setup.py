from setuptools import setup

INSTALL_REQUIRES = [
    'pandas==0.18.0',
    'numexpr==2.5.2',
    'pysam==0.9.0',
    'cutadapt==1.9.1',
    'tables==3.2.2',
]

setup(name='mirror_seq',
    version='0.1',
    description='The bioinformatics tool for Mirror-seq.',
    url='https://github.com/Zymo-Research/mirror-seq',
    author='Hunter Chung',
    author_email='b89603112@gmail.com',
    licence='Apache License 2.0',
    packages=['mirror_seq'],
    install_requires=INSTALL_REQUIRES)
