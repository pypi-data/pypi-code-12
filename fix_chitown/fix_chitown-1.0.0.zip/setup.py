"""Setup for fixing Chicago team errors in the 2014 lahman database."""

from setuptools import setup  # , find_packages

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='fix_chitown',
    version='1.0.0',
    packages=['fix_chitown'],
    description='Fix Chicago team errors in the 2014 lahman DB.',
    long_description=readme,
    author='Benjamin Field',
    author_email='benjamin.field@gmail.com',
    url='https://github.com/aitchslash',
    license=license,
    install_requires=['PyMySQL==0.6.7'],
    keywords=['lahman', 'baseball', 'Chicago'],
    # packages=find_packages(),
    entry_points={
        'console_scripts': [
            'fix_chitown= fix_chitown.__main__:main'
        ]
    },
)
