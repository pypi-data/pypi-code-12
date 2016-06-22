from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='ivencloud',
      version='0.1.3',
      url='https://github.com/BerkOzdilek/PythonSDK',
      author='Berk Ozdilek',
      author_email='biozdilek@gmail.com',
      packages=['ivencloud'],
      install_requires=[
          'requests'],
      description='connect your device to iven cloud',
      keywords='iven iot',
      long_description=readme(),
      classifiers=[
          'Programming Language :: Python :: 2.7',
          'Development Status :: 3 - Alpha'],
      test_suite='nose.collector',
      tests_require=['nose']
      )

