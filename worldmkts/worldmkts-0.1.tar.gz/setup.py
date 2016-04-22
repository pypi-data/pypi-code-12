from setuptools import setup

setup(name='worldmkts',
      version='0.1',
      description='Display World Markets data from Google Finance',
      author='David Elden',
      packages=['world_mkts_data'],
      install_requires=[
          'lxml',
          'requests',
          'numpy',
          'tabulate'
      ]
    )