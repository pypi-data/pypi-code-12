import os
from setuptools import find_packages,setup
from subprocess import Popen, PIPE

def call_git_describe():
    try:
        p = Popen(
            ['git', 'describe', '--tags'],
            stdout=PIPE,
            stderr=PIPE
        )
        p.stderr.close()
        return p.stdout.readlines()[0].strip().replace('-','+')
    except:
        return None

def get_git_version():
    version = call_git_describe()

    if version is None:
        raise ValueError("Cannot find the version number!")
    return version

setup(
    description='Viking Makt Framework',
    include_package_data=True,
    install_requires=['tornado'],
    license='https://gitlab.com/vikingmakt/rask/raw/master/LICENSE',
    maintainer='Umgeher Torgersen',
    maintainer_email='me@umgeher.org',
    name='rask',
    package_data={'':['LICENSE','VERSION']},
    packages=find_packages(),
    url='https://gitlab.com/vikingmakt/rask',
    version=get_git_version()
)
