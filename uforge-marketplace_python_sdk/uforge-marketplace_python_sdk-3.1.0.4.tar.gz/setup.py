from setuptools import setup,find_packages

setup (

  # Declare your packages' dependencies here, for eg:
  install_requires=['lxml==3.3.5'],

  name = 'uforge-marketplace_python_sdk',
version = '3.1.0.4',
  packages = find_packages(),

  description='UForge Marketplace Python SDK',
  long_description='',
  author = 'Joris Bremond',
  author_email = 'joris.bremond@usharesoft.com',
  license="Apache License 2.0",
  url = 'http://www.usharesoft.com',
  classifiers=(
        'Development Status :: 4 - Beta',
        'Topic :: Software Development :: Libraries',
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
  
)
