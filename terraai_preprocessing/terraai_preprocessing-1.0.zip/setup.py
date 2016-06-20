from setuptools import setup

setup(name='terraai_preprocessing',
      version='1.0',
      description='TerraAI preprocessing module',
      url='',
      author='aamir',
      author_email='aamir@terra.ai',
      license='TerraAI',
      packages=['terraai_preprocessing','terraai_preprocessing.combinatorics','terraai_preprocessing.preprocessing'],
	  include_package_data=True,
      zip_safe=False)