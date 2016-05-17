from setuptools import setup, find_packages
from parse_requirements_not_suckily import __version__

setup(
    name='parse-requirements-not-suckily',
    version=__version__,
    description=('Wrapper for parse_requirements to make less painful'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='setup.py lazymode parse_requirements',
    author='Jon Robison',
    author_email='narfman0@gmail.com',
    url='https://github.com/narfman0/parse-requirements-not-suckily',
    license='LICENSE',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
)
