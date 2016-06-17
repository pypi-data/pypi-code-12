from distutils.core import setup

with open('README.md') as file:
    long_description = file.read()

setup(
    name='ghstreak',
    version='0.1.0',
    description='A Python library for fetching GitHub contribution streaks.',
    long_description=long_description,
    author='Christopher Su',
    author_email='chris+py@christopher.su',
    url='https://github.com/csu/gh-streak',
    packages=['ghstreak'],
    install_requires=[
        "requests==2.10.0"
    ]
)