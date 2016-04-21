from distutils.core import setup
from setuptools import setup, find_packages
import ast

def get_version(fname):
    with open(fname) as f:
        source = f.read()
    module = ast.parse(source)
    for e in module.body:
        if isinstance(e, ast.Assign) and \
                len(e.targets) == 1 and \
                e.targets[0].id == '__version__' and \
                isinstance(e.value, ast.Str):
            return e.value.s
    raise RuntimeError('__version__ not found')

setup(name = 'dota2hero',  
      version = get_version('dota2hero/dota2hero'),
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
      author = 'Yamol',  
      author_email = 'xlccalyx@qq.com', 
      maintainer = 'Yamol',
      url = 'www.calyx.biz',
      download_url = 'http://www.calyx.biz/downloading--1997936733.html',
      packages = ['dota2hero'],
      package_dir = {'dota2hero': 'dota2hero'},
      scripts = ['dota2hero/dota2hero'],
      package_data = {'dota2hero': ['dota2hero.infor.txt']}
) 

