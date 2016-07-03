from setuptools import setup

def readme():
    with open('README.rst') as rdm:
        return rdm.read()

setup(name = 'django_cryptofield',
      version = '0.2',
      description = 'A field for database backed password crypto',
      long_description = readme(),
      classifiers = [
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Framework :: Django',
      ],
      keywords = 'django crypto pgcrypto',
      url = 'http://github.com/fmorgner/django_cryptofield',
      author = 'Felix Morgner',
      author_email = 'felix.morgner@gmail.com',
      license = 'BSD',
      packages = ['cryptofield'])

