# -*- coding: utf-8 -*-
from setuptools import setup

setup(name='izigraph',
      version='0.13.0',
      description='Package to create graphs',
      url='https://github.com/gnkz/izigraph',
      author='Gonzalo Sánchez',
      author_email='sanchezv.gonzalo@gmail.com',
      license='MIT',
      packages=[
            'izigraph',
            'izigraph.importers'
      ],
      install_requires=[],
      extras_require={
            ':python_version == "2.6"': [
                  'ordereddict',
            ],
      },
      zip_safe=False)
