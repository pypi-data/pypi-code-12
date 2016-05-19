from setuptools import setup

setup(name='capitals',
      version='0.1.0',
      url='http://git.km3net.de/jreubelt/capitals.git',
      description='Capitals quiz',
      author='Jonas Reubelt',
      packages=['capitals'],
      include_package_data=True,
      platforms='any',
      install_requires=[
          'urwid',
          ],
      entry_points={
          'console_scripts': [
              'capitals=capitals.app:main',
          ],
      },
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
      ],
)

__author__ = 'Jonas Reubelt'
