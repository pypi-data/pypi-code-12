from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='ivencloud',
      version='0.1',
      # url='github',
      author='Berk Ozdilek',
      author_email='biozdilek@gmail.com',
      packages=['ivencloud'],
      install_requires=[
          'requests'],
      description='connect your device to iven cloud',
      keywords='iven cloud iot',
      long_description=readme()
      )

