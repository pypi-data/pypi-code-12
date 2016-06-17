from distutils.core import setup
from setuptools import setup, find_packages

setup(name='ipyviz',
      version='1.0',
      description='Visualisation package for IPython Notebooks',
      author='Martin Zellner',
      author_email='martin.zellner@gmail.com',
      packages=find_packages(),
      package_data={'': ['*.html', 'd3.v3.min.js']},
      requires=['numpy',
                'seaborn',
                'matplotlib',
                'networkx',
                'IPython',
                'folium',
                ])
