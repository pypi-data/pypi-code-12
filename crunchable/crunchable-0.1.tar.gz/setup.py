from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='crunchable',
      version='0.1',
      description='Python SDK for Crunchable.IO',
      long_description=readme(),
      url='',
      author='Crunchable.IO',
      author_email='admin@crunchable.io',
      packages=['crunchable'],
      install_requires=[
        'requests',
        'bunch',
      ],
      include_package_data=True,
      zip_safe=False)

