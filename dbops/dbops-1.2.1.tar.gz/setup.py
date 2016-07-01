from distutils.core import setup

setup(name='dbops',
      version='1.2.1',
      description='Database Operations Tools',
      author='Ryan Birmingham',
      author_email='birm@rbirm.us',
      url='http://rbirm.us',
      classifiers=['Development Status :: 3 - Alpha', 'Topic :: Database',
                   'Intended Audience :: Information Technology'],
      long_description=open('readme.rst', 'r').read(),
      packages=['dbops'],
      )
