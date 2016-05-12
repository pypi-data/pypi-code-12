import sys
from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES

PACKAGE = "log4python"
NAME = "log4python"
DESCRIPTION = "log for python like log4j2"
AUTHOR = "li_jia_yue"
AUTHOR_EMAIL = "59727816@qq.com"
URL = "https://github.com/starwithmoon/log4p"
VERSION = __import__(PACKAGE).__version__

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=open("README.rst").read(),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="BSD",
    url=URL,
    packages=[ PACKAGE, ],
    #packages=find_packages(exclude=["tests.*", "tests"]),
    #package_data=find_package_data(
	#		PACKAGE,
	#		only_in_packages=False
	#  ),
    keywords='log for python',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    zip_safe=False,
)
