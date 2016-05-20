from setuptools import setup, find_packages

setup(
    name='file_lib',
    version='1.0.4',
    description='File Library',
    long_description='https://pypi.python.org/pypi/file_lib',
    url='https://github.com/Akira-Taniguchi/file_lib',
    author='AkiraTaniguchi',
    author_email ='dededededaiou2003@yahoo.co.jp',
    packages=find_packages(),
    license='MIT',
    keywords='csv reaader writer unicode kanji gz zip compress unzip json directory file backup',
    classifiers=[
      'Development Status :: 5 - Production/Stable',
      'Programming Language :: Python :: 2.7',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: MIT License'
    ],
    install_requires=['simplejson==3.8.0', 'unicodecsv==0.9.0']
)
