from setuptools import setup, find_packages


def readme():
    with open('README.rst') as f:
        return f.read()


def requirements():
    with open('requirements.txt') as f:
        return [line.rstrip('\n') for line in f]


def version():
    with open('version.txt') as f:
        return f.read().rstrip('\n')

setup(name='psychic_disco',
      version=version(),
      description='Pythonic Microservices on AWS Lambda',
      long_description=readme(),
      url='http://github.com/robertdfrench/psychic-disco',
      author='Robert D. French',
      author_email='robert@robertdfrench.me',
      license='MIT',
      packages=find_packages(),
      zip_safe=False,
      include_package_data=True,
      test_suite='nose.collector',
      tests_require=['nose'],
      install_requires=requirements(),
      scripts=['bin/psychic_disco'])
