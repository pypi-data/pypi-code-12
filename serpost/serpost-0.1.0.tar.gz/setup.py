import os
from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='serpost',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='CLI tool for search tracking number in SERPOST page',
    url='https://github.com/erickgnavar/serpost/',
    author='Erick Navarro',
    author_email='erick@navarro.io',
    keywords='tracking serpost',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities',
    ],
    install_requires=[
        'beautifulsoup4',
        'lxml'
    ],
    entry_points={
        'console_scripts': [
            'serpost-cli=serpost.cli:main'
        ]
    }
)
