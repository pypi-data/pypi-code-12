from setuptools import setup

setup(name='generaltools',
      version=open("VERSION").read(),
      description='Collection of function snippets often used in our python environment',
      url='https://github.com/buchbend/generaltools.git',
      author='Christof Buchbender',
      author_email='buchbend@ph1.uni-koeln.de',
      license='MIT',
      packages=['generaltools'],
      install_requires=["MySQL-python"],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
