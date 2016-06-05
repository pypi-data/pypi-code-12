from setuptools import setup, find_packages

setup(
    name='mdpy',
    version='0.0.3',
    description='utilities for converting markdown files to ipython notebooks',
    url='https://github.com/frnsys/mdpy',
    author='Francis Tseng (@frnsys)',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'click'
    ],
    entry_points='''
        [console_scripts]
        mdpy=mdpy:cli
    ''',
)