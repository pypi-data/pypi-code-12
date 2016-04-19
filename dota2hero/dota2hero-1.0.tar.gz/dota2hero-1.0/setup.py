from distutils.core import setup
from setuptools import setup, find_packages

setup(name = 'dota2hero',  
      version = '1.0',
      keywords = 'dota 2 hero',
      description = 'strategy of selecting hero in Dota2', 
      long_description = 'strategy of selecting hero in Dota2.',
      license = 'GPLv3',
      classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'Topic :: Software Development :: Build Tools',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Programming Language :: Python :: 2.7',
      ],
      author = 'Yingxiang Li',  
      author_email = 'xlccalyx@gmail.com', 
      maintainer = 'Yingxiang Li',
      url = 'www.calyx.biz',
      download_url = 'http://www.calyx.biz/downloading--1997936733.html',
      packages = ['dota2hero'],
      package_dir = {'dota2hero': 'dota2hero'},
      scripts = ['dota2hero/dota2hero'],
      package_data = {'dota2hero': ['example.input.tab']}
) 

