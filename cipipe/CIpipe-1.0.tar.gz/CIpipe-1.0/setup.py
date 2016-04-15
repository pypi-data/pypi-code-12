from distutils.core import setup
from setuptools import setup, find_packages

setup(name = 'CIpipe',  
      version = '1.0',
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

