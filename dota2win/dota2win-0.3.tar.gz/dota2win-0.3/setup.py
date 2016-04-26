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

setup(name = 'dota2win',  
      version = get_version('dota2win/dota2win'),
      keywords = 'dota 2 hero',
      description = 'Win in Dota2', 
      long_description = 'Win in Dota2.',
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
      download_url = 'https://pypi.python.org/pypi/dota2win',
      packages = ['dota2win'],
      package_dir = {'dota2win': 'dota2win'},
      scripts = ['dota2win/dota2win'],
      package_data = {'dota2win': ['dota2.hero.name.txt']}
) 

