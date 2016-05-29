from distutils.core import setup
from distutils.extension import Extension
import os
import sys
print 'This module requires libboost-python-dev, libpython-dev, libpqxx-4.0, libhdf6-dev'
srcs = ['./src/' + i for i in os.listdir('./src') if i.endswith('cpp')]
headers = ['./header/' + i for i in os.listdir('./header')]
inc = ['./header']
if 'C_INCLUDE_PATH' in os.environ.keys():
    c_inc = os.environ.get('C_INCLUDE_PATH').split(':')
    if '' in c_inc:
        c_inc.remove('')
    inc.append(c_inc)

if 'CPLUS_INCLUDE_PATH' in os.environ.keys():
    cplus_inc = os.environ.get('CPLUS_INCLUDE_PATH').split(':')
    if '' in cplus_inc:
        cplus_inc.remove('')
    inc.append(cplus_inc)

lib = ['opt/local/lib']
LIB_BOOST_PYTHON='boost_python'
if sys.platform == 'darwin':
    lib.append(os.environ.get('LD_LIBRARY_PATH').split(':'))
    LIB_BOOST_PYTHON = 'boost_python-mt'
elif sys.platform.startswith('linux'):
    lib.append(os.environ.get('LD_LIBRARY_PATH').split(':'))

setup(name='mygraph',
      version='0.8',
      description='Python hyperpath algorithm implementation',
      author='Tonny Ma',
      author_email='tonny.achilles@gmail.com',
      url='http://fukudalab.hypernav.mobi',
      data_files=[('header', headers)],
      ext_modules=[
          Extension("mygraph",
                    define_macros=[('MAJOR_VERSION', '0'), ('MINOR_VERSION', '6')],
                    include_dirs=inc,
                    library_dirs=lib,
                    libraries=[LIB_BOOST_PYTHON, 'python2.7', 'pqxx', 'hdf5', 'hdf5_hl'],
                    extra_compile_args=['-std=c++0x'],
                    sources=srcs)
      ])
