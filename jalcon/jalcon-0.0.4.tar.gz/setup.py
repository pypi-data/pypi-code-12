import os
from setuptools import setup
import sys
from distutils.sysconfig import get_python_lib
from setuptools import find_packages, setup


if 'install' in sys.argv:
    lib_paths = [get_python_lib()]
    if lib_paths[0].startswith('/usr/lib/'):
        # We have to try also with an explicit prefix of /usr/local in order to
        # catch Debian's custom user site-packages directory.
        lib_paths.append(get_python_lib(prefix='/usr/local'))
    for lib_path in lib_paths:
        existing_path = os.path.abspath(os.path.join(lib_path, 'jalcon'))
        if os.path.exists(existing_path):
            # We note the need for the warning here, but present it after the
            # command is run, so it's more likely to be seen.
            overlay_warning = True
            break

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'jalcon',
    version = '0.0.4',
    author = 'JA Arce',
    author_email = 'johnandrewarce@gmail.com',
    description = ('jalcon is a bootstrap framework for Falcon with MongoDB'),
    license = 'BSD',
    keywords = 'jalcon falcon framework jalcon-rest',
    url = 'https://github.com/jaarce/jalcon',
    packages=find_packages(),
    scripts=['jalcon-admin.py'],
    long_description='Why should it be long when there\'s a short description. Simply JAmazing!',
    zip_safe=False,
    classifiers=[
        'Topic :: Utilities',
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
    ],
)
