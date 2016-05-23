# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from tsuru_router_tailer import __version__

tests_require = [
    "coverage",
    "nose",
    "nose-focus",
    "flake8",
    "yanc",
    "preggy",
]

setup(
    name='tsuru-router-tailer',
    version=__version__,
    description="Send tsuru router log and send to logstash",
    long_description="Send tsuru router log and send to logstash",
    keywords='tsuru router log logstash',
    author='Guilherme Souza',
    author_email='guivideojob@gmail.com',
    license='MIT',
    url='https://github.com/guilhermef/tsuru-router-tailer',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5',
    ],
    packages=find_packages(),
    package_dir={"tsuru_router_tailer": "tsuru_router_tailer"},
    include_package_data=True,

    install_requires=[
        'redis',
    ],

    extras_require={
        'tests': tests_require,
    },

    entry_points={
        'console_scripts': [
            'tsuru-router-tailer=tsuru_router_tailer.main:main',
        ],
    },

)
