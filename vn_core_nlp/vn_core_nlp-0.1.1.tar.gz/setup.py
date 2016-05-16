from setuptools import setup, find_packages
#from distutils.core import setup

packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"])
setup(name='vn_core_nlp',
      version='0.1.1',
      description='The python package for vietnamese text processing',
      author='Hoang Pham',
      author_email='phamthaihoang.hn@gmail.com',
      #packages=['vn_core_nlp','vn_core_nlp.preprocessing',''],
      packages=packages,
      include_package_data=True,
      zip_safe=False)
