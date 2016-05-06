import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

data_files = [
    (root, [os.path.join(root, f) for f in files]) for root, dirs, files in os.walk('examples')
]

setup(
    name='inteltime',
    version='1.0.4',
    description="Intel checkpoint and cycle calculator for Niantic Lab's Ingress(tm)",
    long_description=long_description,
    author='Paul Traina',
    author_email='bulk+pypi@pst.org',
    url="https://gitlab.com/pleasantone/intel-times",
    packages=find_packages(exclude=['examples', 'tests']),
    entry_points={
        'console_scripts': [
            'inteltime=inteltime.test:main',
            'inteltime-flask=inteltime.flask:main'
        ]
    },
    install_requires=[
        'python-dateutil',
        'timestring',
        'tzlocal'
    ],
    package_data={
        '': ['templates/*', 'examples/*', 'static/*']
    },
    data_files=data_files,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Database :: Front-Ends',
        'Topic :: Games/Entertainment',
    ],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
)
