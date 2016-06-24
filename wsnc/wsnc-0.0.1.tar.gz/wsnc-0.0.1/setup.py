from distutils.core import setup
import sys

if not (sys.version_info[0] >= 3 and sys.version_info[1] >= 4):
    sys.exit('Requires Python >= 3.4')

setup(
    name='wsnc',
    version='0.0.1',
    license='ISC License',
    description='netcat over websockets',
    author='Blair Mason',
    author_email='robert.blair.mason@gmail.com',
    url='https://github.com/rbmj/wsnc',
    scripts=['wsnc/wsnc'],
    install_requires=['autobahn'])
