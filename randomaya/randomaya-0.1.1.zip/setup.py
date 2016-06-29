from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='randomaya',
      version='0.1.1',
      description='Random aya generator',
      url='https://github.com/ansarb/randomaya',
      author='Ansar Bedharudeen',
      author_email='1ns1rb@gmail.com',
      license='MIT',
      packages=['randomaya'],
      include_package_data=True,
      zip_safe=False)