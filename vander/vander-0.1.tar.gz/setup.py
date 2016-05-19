from setuptools import setup

setup(name='vander',
      version='0.1',
      description='Live graphs in your terminal',
      url='http://github.com/rubzo/vander',
      author='Stephen Kyle',
      author_email='stephenckyle@gmail.com',
      license='MIT',
      packages=['vander'],
      entry_points = {
          'console_scripts': ['vander=vander:main'],
      },
      install_requires=['urwid'],
      zip_safe=False)
