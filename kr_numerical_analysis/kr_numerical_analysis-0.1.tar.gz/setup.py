from setuptools import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
    
setup(name='kr_numerical_analysis',
      version='0.1',
      description='The methods for numerical analysis is based on the book of J.D. Faires and R.L. Burden: "Numerical Analysis".',
      long_description=long_description,
      url='https://github.com/kingraijun/numerical_analysis.git',
      author='Ruben A. Idoy, Jr.',
      author_email='king.raijun@gmail.com',
      #license='',
      keywords='numerical analysis',
      packages=find_packages(exclude=['tests','dist'])
      #install_requires=[],
    )