import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

data_files = [
    (root, [os.path.join(root, f) for f in files]) for root, dirs, files in os.walk('examples')
]

setup(
    name='intelurls',
    version='0.0.1',
    description="Parse Ingress Intel, Google Maps, and Apple Maps URLs",
    long_description=long_description,
    author='Paul Traina',
    author_email='bulk+pypi@pst.org',
    url="https://gitlab.com/pleasantone/intelurls",
    packages=find_packages(exclude=['examples', 'tests']),
    install_requires=[
        'requests',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Topic :: Games/Entertainment',
    ],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
)
