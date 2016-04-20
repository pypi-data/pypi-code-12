import os
from os import path
 
from distutils.core import setup
 
def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == "":
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)
 
package_dir = "./"
 
packages = []
for dirpath, dirnames, filenames in os.walk(package_dir):
    for i, dirname in enumerate(dirnames):
        if dirname.startswith("."):
            del dirnames[i]
    if "__init__.py" in filenames:
        packages.append(".".join(fullsplit(dirpath)))

LONG_DESCRIPTION = open(path.join(path.dirname(__file__), 'README')).read()

REQUIREMENTS = [
'pyserial'
]
       
setup(
	name = 'megapi',
	version = '0.1.4',
	license = 'MIT',    
	author = 'ander',                       
	author_email = 'ander@makeblock.cc',
	url = 'http://www.makeblock.com',
	description = 'python for megapi',
	long_description=LONG_DESCRIPTION,
	packages=packages
)
