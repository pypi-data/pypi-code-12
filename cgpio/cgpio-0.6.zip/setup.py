
from setuptools import setup, find_packages

setup(
    name = 'cgpio',
    version = '0.6',
    keywords = ('gpio', 'class'),
    description = 'a gpio class based on gpio-0.1.2',
    long_description='Accesiing Pi-gpio the standard linux [sysfs interface], \n tested on RPI, NanoPi M1',
    license = 'MIT License',
    install_requires = [],

    author = 'caoxp',
    author_email = 'fpdz2010@qq.com',
	url='http://fpdz.taobao.com',
    
    packages = find_packages(),
    platforms = 'any',
)

