from setuptools import setup, find_packages

setup(name='terrapin',
      version="0.0.3",
      packages=find_packages(),
      description='A very lightweight template language',
      url='https://github.com/DistilledLtd/terrapin',
      author='Distilled Ltd',
      author_email='randd@distilled.net',
      install_requires=['ply']
      )
