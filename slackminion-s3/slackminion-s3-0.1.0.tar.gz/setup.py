from setuptools import setup, find_packages

from slackminion.plugins.state_s3 import version

setup(
        name='slackminion-s3',
        version=version,
        packages=find_packages(exclude=['test_plugins']),
        url='https://github.com/arcticfoxnv/slackminion-s3',
        license='MIT',
        author='Nick King',
        author_email='',
        description='Provides a s3 state handler for slackminion',
        install_requires=[
            'boto',
            'slackminion',
        ],
        classifiers=[
            "Programming Language :: Python",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Development Status :: 2 - Pre-Alpha",
            "Topic :: Communications :: Chat",
        ]
)
