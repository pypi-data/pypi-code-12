from setuptools import setup

long_description = """Magerestore is a tool to automate fetching backups from a remote server and unpacking them on a magento installation.

Database import and media folder unzipping is the ony currently supported operations.

Magerestore uses n98-magerun to handle some tasks, but are not required for all operations."""

setup(
    name='magerestore',
    version='0.1.1',
    description="Tool for restoring magento install from predefined backups",
    long_description=long_description,
    url="https://github.com/k4emic/magerestore",
    license="GPLv3",
    author="Mads Nielsen",
    packages=['magerestore'],
    install_requires=[
        'Click>=6', 'paramiko>=1.16'
    ],
    entry_points={
        'console_scripts': [
            'magerestore=magerestore.cli:main'
        ]
    },
)
