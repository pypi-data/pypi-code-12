from setuptools import setup,find_packages
import os
import sys

# Declare your packages' dependencies here, for eg:
requires=[
            'cmd2==0.6.7',
            'argparse',
            'progressbar==2.3',
            'termcolor==1.1.0',
            'hurry.filesize==0.9',
         ]

if os.name != "nt":
    if not "linux" in sys.platform:
        #mac os
        requires.append('readline')
else:   #On Windows
    requires.append('pyreadline==2.0')

                    
setup (
  install_requires=requires,
  
  name = 'ussclicore',
  version = '1.0.6',
  description='UShareSoft cli core module',
  #long_description='',
  packages = find_packages(),
  author = 'Joris Bremond',
  author_email = 'joris.bremond@usharesoft.com',
  license="Apache License 2.0",
  #url = '',
  classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
       
  
  #long_description= 'Long description of the package',
  
)
