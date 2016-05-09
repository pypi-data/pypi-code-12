import setuptools
from distutils.core import setup

setup(name='ActivityStream',
      version='0.2.2',
      url='http://sf.net/p/activitystream',
      packages=['activitystream', 'activitystream.storage'],
      install_requires=['pymongo'],
      license='Apache License, http://www.apache.org/licenses/LICENSE-2.0',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 2.7',
          'License :: OSI Approved :: Apache Software License',
          ],
      )
