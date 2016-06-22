import os
from setuptools import setup, find_packages
from subprocess import Popen, PIPE
import sys


HERE = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(HERE, 'README.rst')).read()
CHANGELOG = open(os.path.join(HERE, 'CHANGES.rst')).read()


REQUIRES = [
    'repoze.who>=2.3'
]


TESTS_REQUIRE = [
    'pytest',
    'pytest-cov'
]

setup(
    name='who_dev',
    version='0.0.2',
    description='A developer-mode plugin for repoze.who',
    long_description='\n\n'.join([README, CHANGELOG]),
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
    ],
    keywords='web application server wsgi repoze repoze.who',
    url='https://github.com/m-martinez/who_dev',
    license='BSD-derived (http://www.repoze.org/LICENSE.txt)',
    include_package_data=True,
    packages=find_packages(),
    zip_safe=False,
    install_requires=REQUIRES,
    extras_require={'develop': TESTS_REQUIRE},
    tests_require=TESTS_REQUIRE,
)
