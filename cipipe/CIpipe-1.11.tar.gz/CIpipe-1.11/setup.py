import ast
from distutils.core import setup
from setuptools import setup, find_packages

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

setup(name = 'CIpipe',  
      version = get_version('CIpipe/CIpipe'),
      keywords = 'CRISPR Indel pipe',
      description = 'CRISPR Indel pipe', 
      long_description = 'A piep for analyzing indel at target region sequence from CRISPR experiment.',
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
      packages = ['CIpipe'],
      package_dir = {'CIpipe': 'CIpipe'},
      scripts = ['CIpipe/CIpipe'],
      package_data = {'CIpipe': ['VarScan.v2.3.9.jar', 'example.input.tab']}
) 

