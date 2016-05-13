from setuptools import setup

setup(name='lj_commons',
      version='0.4',
      description='The common parameters, methods and classes for Luojilab Pythonists',
      url='',
      author='Fu Jian',
      author_email='fujian_en@126.com',
      license='MIT',
      packages=['lj_commons'],
      install_requires=[
          'markdown',
      ],
      scripts=['bin/ljmail', 'bin/ljmail-generate-config'],
      zip_safe=False)
