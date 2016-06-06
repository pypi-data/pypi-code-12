#!/usr/bin/env python
# coding: utf-8
import codecs
import os
import sys


try:
    from setuptools import setup
except:
    from distutils.core import setup


"""
打包的用的setup必须引入，
"""


def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()


NAME = "xcfsyslogger"
"""
名字，一般放你包的名字即可
"""

PACKAGES = ["xcfsyslogger", ]
"""
包含的包，可以多个，这是一个列表
"""

DESCRIPTION = "this is a test package for packing python liberaries tutorial."
"""
关于这个包的描述
"""

LONG_DESCRIPTION = read("README.rst")
"""
参见read方法说明
"""

KEYWORDS = "xiachufang"
"""
关于当前包的一些关键字，方便PyPI进行分类。
"""

AUTHOR = "liuweibo"
"""
谁是这个包的作者，写谁的名字吧
我是MitchellChu，自然这里写的是MitchellChu
"""

AUTHOR_EMAIL = "liuweibo@xiachufang.com"
"""
作者的邮件地址
"""

URL = "http://blog.useasp.net/"
"""
你这个包的项目地址，如果有，给一个吧，没有你直接填写在PyPI你这个包的地址也是可以的
"""

VERSION = "1.0.0"
"""
当前包的版本，这个按你自己需要的版本控制方式来
"""

LICENSE = "MIT"
"""
授权方式，我喜欢的是MIT的方式，你可以换成其他方式
"""

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    keywords=KEYWORDS,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,
    packages=PACKAGES,
    include_package_data=True,
    zip_safe=True,
)

## 把上面的变量填入了一个setup()中即可。
