from __future__ import print_function
import os
import sys
import re
import shutil
from setuptools import setup, find_packages


def get_version(package):
    """Return package version as listed in `__version__` in `init.py`."""
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


version = get_version('mezzanine_client')


if sys.argv[-1] == 'publish':
    if os.system("pip freeze | grep wheel"):
        print("wheel not installed.\nUse `pip install wheel`.\nExiting.")
        sys.exit()
    if os.system("pip freeze | grep twine"):
        print("twine not installed.\nUse `pip install twine`.\nExiting.")
        sys.exit()
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine upload dist/*")
    print("You probably want to also tag the version now:")
    print("  git tag -a {0} -m 'version {0}'".format(version))
    print("  git push --tags")
    shutil.rmtree('dist')
    shutil.rmtree('build')
    shutil.rmtree('mezzanine_client.egg-info')
    sys.exit()


setup(
    name='mezzanine-client',
    version=version,
    author='George Cushen',
    author_email='mezzanine-users@googlegroups.com',   
    url='http://gcushen.github.io/mezzanine-api/client/',
    description='A remote CLI and Python client SDK for Mezzanine REST API.',
    keywords='mezzanine cms api client sdk library rest restful',
    include_package_data=True,
    license='ISC',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'requests>=2.9.1',
        'requests-oauthlib>=0.6.1',
        'click',
        'future',
        'markdown2'
    ],
    entry_points="""
        [console_scripts]
        mezzanine-cli=mezzanine_client.cli:client
    """,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
