import os
from distutils.core import setup


def get_packages(root_dir):
    packages = []
    for root, dirs, files in os.walk(root_dir):
        if "__init__.py" in files:
            packages.append(root.replace('/', '.'))
    return packages


setup(
    name='repeat-cli',
    version='1.0.0',
    author='Joel Johnson',
    author_email='joelj@joelj.com',
    packages=['repeat_cli'],
    scripts=['repeat'],
    data_files=['README.md'],
    url='https://github.com/leftstache/repeat',
    license='Apache 2.0',
    description='Repeats a command',
    long_description=open('README.md').read(),
    install_requires=[]
)