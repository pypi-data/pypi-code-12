from setuptools import setup

from controlhost import version

setup(name='controlhost',
      version=version,
      url='https://github.com/tamasgal/controlhost/',
      description='A set of classes and tools wich uses the ControlHost protocol.',
      author='Tamas Gal',
      author_email='himself@tamasgal.com',
      packages=['controlhost'],
      include_package_data=True,
      platforms='any',
      install_requires=[
      ],
      entry_points={
          'console_scripts': [
              #'controlhost=controlhost.app:main',
          ],
      },
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
      ],
)

__author__ = 'Tamas Gal'
