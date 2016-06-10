from setuptools import setup

setup(name='jsreport',
      version='0.2.1',
      description='Simple tool to pull basic reporting data out of JustServe (https://www.justserve.org/).',
      url='https://github.com/abadstubner/JustServe_Reports',
      author='abadstubner',
      author_email='andrew+pypi@badstubner.com',
      license='MIT',
      packages=['jsreport'],
      install_requires=[
          'selenium',
      ],
      zip_safe=False)
