import os
from setuptools import find_packages, setup


# directory = os.path.abspath(os.path.dirname(__file__))
"""
with open(os.path.join(directory, 'README.rst')) as f:
    long_description = f.read()
"""

setup(
    name="vexstorage",
    version='0.0.1',
    description='Database storage for vexbot',
    # long_description=long_description,
    url='https://github.com/benhoff/vexstorage',
    license='GPL3',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities',
        'Operating System :: OS Independent'],
    keywords='vexbot',
    author='Ben Hoff',
    author_email='beohoff@gmail.com',
    packages= find_packages(), # exclude=['docs', 'tests']
    entry_points={'vexbot.plugins': ['vexstorage = vexstorage.__main__'],},
    install_requires=[
        'pyzmq',
        'sqlalchemy',
        'pyyaml'
        ],

    extras_require={
        'dev': ['flake8']
        },
)
