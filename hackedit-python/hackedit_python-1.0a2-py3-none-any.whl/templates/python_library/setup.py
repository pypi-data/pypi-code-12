from setuptools import setup, find_packages
import sys, os

setup(name='@project@',
    version='@version@',
    description="@description@",
    long_description="@description@",
    classifiers=[], 
    keywords='',
    author='@creator@',
    author_email='@email@',
    url='@url@',
    license='@license@',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    setup_requires=[],
    entry_points="""
    """,
    namespace_packages=[],
)
