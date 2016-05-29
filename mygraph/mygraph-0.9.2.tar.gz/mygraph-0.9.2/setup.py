from distutils.core import setup
from distutils.extension import Extension
import os
import sys
print 'This module requires libboost-python-dev, libpython-dev, libpqxx-4.0, libhdf5-dev'
if sys.platform =='darwin':
    print 'sudo port install boost, hdf5, python27, libpqxx'
elif sys.platform =='linux':
    print 'sudo apt-get install libboost-python-dev, libpython-dev, libpqxx-4.0, libhdf5-dev'
srcs = ['./src/' + i for i in os.listdir('./src') if i.endswith('cpp')]
headers = ['./header/' + i for i in os.listdir('./header')]
inc = ['./header']
if 'C_INCLUDE_PATH' in os.environ.keys():
    c_inc = os.environ.get('C_INCLUDE_PATH').split(':')
    print 'Appending C_LIBRARY_PATH'
    if '' in c_inc:
        c_inc.remove('')
    inc += c_inc

if 'CPLUS_INCLUDE_PATH' in os.environ.keys():
    cplus_inc = os.environ.get('CPLUS_INCLUDE_PATH').split(':')
    print 'Appending CPLUS_LIBRARY_PATH'
    if '' in cplus_inc:
        cplus_inc.remove('')
    inc += cplus_inc


lib = ['opt/local/lib', '/usr/local/lib'] if sys.platform=='darwin' else\
    ['/usr/local/lib','/usr/lib']

if 'LD_LIBRARY_PATH' in os.environ.keys():
    print 'Appending LD_LIBRARY_PATH'
    lib += os.environ.get('LD_LIBRARY_PATH').split(':')

LIB_BOOST_PYTHON='boost_python-mt' if sys.platform == 'darwin' else\
    'boost_python'

setup(name='mygraph',
      version='0.9.2',
      description='Python hyperpath algorithm implementation',
      author='Tonny Ma',
      author_email='tonny.achilles@gmail.com',
      url='http://fukudalab.hypernav.mobi',
      data_files=[('header', headers)],
      ext_modules=[
          Extension("mygraph",
                    define_macros=[('MAJOR_VERSION', '0'), ('MINOR_VERSION', '9')],
                    include_dirs=inc,
                    library_dirs=lib,
                    libraries=[LIB_BOOST_PYTHON, 'python2.7', 'pqxx', 'hdf5', 'hdf5_hl'],
                    extra_compile_args=['-std=c++0x'],
                    sources=srcs)
      ])
