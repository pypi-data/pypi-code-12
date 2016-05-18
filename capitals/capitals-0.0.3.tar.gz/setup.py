from setuptools import setup

setup(name='capitals',
      version='0.0.3',
      url='http://git.km3net.de/jreubelt/capitals.git',
      description='Capitals quiz',
      author='Jonas Reubelt',
      packages=['capitals'],
      include_package_data=True,
      platforms='any',
      install_requires=[
          'pandas',
          'urwid',
          'random',
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
