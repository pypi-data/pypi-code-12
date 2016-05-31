from setuptools import setup, find_packages
import os

from os import path as op
CURRENT_DIR = op.dirname(__file__)

version = open(os.path.join(CURRENT_DIR, 'ubackup', 'VERSION.txt'), 'r').read().strip()

setup(
    name='ubackup',
    version=version,
    packages=find_packages(),

    install_requires=open(op.join(CURRENT_DIR, 'requirements.txt')).read().splitlines(),

    author='Thomas Kliszowski',
    author_email='contact@thomaskliszowski.fr',
    description='Minimalist backup tool',
    license='MIT',
    keywords='ubackup backup tool',
    url='https://github.com/ThomasKliszowski/ubackup',
    include_package_data=True,
    zip_safe=False,
    entry_points='''
        [console_scripts]
        ubackup=ubackup.cli:main
    '''
)
