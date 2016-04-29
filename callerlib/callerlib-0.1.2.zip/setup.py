import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='callerlib',
    version_format='{tag}.{commitcount}',
    packages=find_packages(),
    package_data={
        'callerlib': ['template/*.py', 'template/logs/.keep']
    },
    license='BSD License',
    description='A sip caller robotframework library.',
    long_description=README,
    url='https://bitbucket.org/PekaTeam/callerlib',
    author='Pavel Fedorov',
    author_email='studentofsut@gmail.com',
    install_requires=[
        'robotremoteserver>=1.0.1',
    ],
    setup_requires=[
        'setuptools-git-version',
    ],
    entry_points={'console_scripts': [
        'callerlib-startproject = callerlib.management:startproject',
    ]},
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Telecommunications Industry',
        'License :: Freeware',
        'Natural Language :: Russian',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
    ],
)
