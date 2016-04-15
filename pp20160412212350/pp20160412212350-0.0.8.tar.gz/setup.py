# -*- coding: utf-8 -*-


from setuptools import setup


long_desc = """Programming Exercise for Python is a collection of sample code
for demostration of concept and usage of Python Language."""

setup(name='pp20160412212350',
      version='0.0.8',
      packages=['pp20160412212350', 'pp20160412212350.lib'],
      entry_points={'console_scripts': [
          'pp20160412212350 = pp20160412212350.__main__:main',
      ]},
      author='Jim Lin',
      author_email='jimlintw922@gmail.com',
      url='https://github.com/jinsenglin/pp20160412212350/',
      description='Programming Exercise for Python',
      long_description=long_desc,
      license="Apache 2.0",
      classifiers=[
          'Programming Language :: Python :: 2'
      ],
      install_requires=[]
      )
