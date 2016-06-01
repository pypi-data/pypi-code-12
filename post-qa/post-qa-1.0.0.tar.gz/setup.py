from setuptools import setup, find_packages
import os
from io import open


packagename = 'post-qa'
description = 'Upload QA metrics for LSST Data Management.'
author = 'Jonathan Sick'
author_email = 'jsick@lsst.org'
license = 'MIT'
url = 'https://github.com/lsst-sqre/post-qa'
version = '1.0.0'


def read(filename):
    full_filename = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        filename)
    return open(full_filename, mode='r', encoding='utf-8').read()

long_description = read('README.rst')


setup(
    name=packagename,
    version=version,
    description=description,
    long_description=long_description,
    url=url,
    author=author,
    author_email=author_email,
    license=license,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='lsst',
    packages=find_packages(exclude=['docs', 'tests*', 'data']),
    install_requires=['future', 'requests', 'GitPython', 'pytz'],
    tests_require=['pytest', 'pytest-cov', 'pytest-flake8',
                   'pytest-mock', 'responses', 'numpy'],
    # package_data={},
    entry_points={
        'console_scripts': [
            'post-qa = postqa.cli:run_post_qa',
        ]
    }
)
