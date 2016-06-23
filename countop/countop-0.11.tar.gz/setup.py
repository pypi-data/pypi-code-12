from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='countop',
      version='0.11',
      description='Count basic operations in algorithm implementations.',
      long_description=readme(),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 2.7'
      ],
      keywords='algorithms, count operations',
      url='https://github.com/ankur-gupta/countop',
      author='Ankur Gupta',
      author_email='ankur@perfectlyrandom.org',
      license='MIT',
      packages=['countop'],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
