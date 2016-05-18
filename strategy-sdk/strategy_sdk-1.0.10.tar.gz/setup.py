# encoding: utf-8
from __future__ import absolute_import
import codecs
import os

try:
    from setuptools import setup, find_packages
except:
    from distutils.core import setup
u"""
打包的用的setup必须引入，
"""

__author__ = u'Yonka'


def read(fname):
    u"""
    定义一个read方法，用来读取目录下的长描述
    我们一般是将README文件中的内容读取出来作为长描述，这个会在PyPI中你这个包的页面上展现出来，
    你也可以不用这个方法，自己手动写内容即可，
    PyPI上支持.rst格式的文件。暂不支持.md格式的文件，<BR>.rst文件PyPI会自动把它转为HTML形式显示在你包的信息页面上。
    """
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()


NAME = u"strategy_sdk"
u"""
名字，一般放你包的名字即可
"""
PACKAGES = find_packages()
# print(PACKAGES)
u"""
包含的包，可以多个，这是一个列表
"""

DESCRIPTION = u"this is a python2 client sdk for strategy access"
u"""
关于这个包的描述
"""

LONG_DESCRIPTION = read(u"README.rst")
u"""
参见read方法说明
"""

KEYWORDS = u"python2 strategy sdk client"
u"""
关于当前包的一些关键字，方便PyPI进行分类。
"""

AUTHOR = u"vector tang"
u"""
谁是这个包的作者，写谁的名字吧
我是MitchellChu，自然这里写的是MitchellChu
"""

AUTHOR_EMAIL = u"tangtao@hotmail.com"
u"""
作者的邮件地址
"""

URL = u"https://pypi.python.org/pypi/strategy-sdk-py2"
u"""
你这个包的项目地址，如果有，给一个吧，没有你直接填写在PyPI你这个包的地址也是可以的
"""

VERSION = u"1.0.10"
u"""
当前包的版本，这个按你自己需要的版本控制方式来
"""

LICENSE = u"MIT"
u"""
授权方式，我喜欢的是MIT的方式，你可以换成其他方式
"""
install_requires=[
    'protobuf',
    'futures'
]
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=[
        u'License :: OSI Approved :: MIT License',
        u'Programming Language :: Python',
        u'Intended Audience :: Developers',
        u'Operating System :: OS Independent',
    ],
    keywords=KEYWORDS,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,
    # package_dir={"": "sd"},
    packages=PACKAGES,
    include_package_data=True,
    zip_safe=True,
    install_requires=install_requires,
    requires=install_requires
)

# 把上面的变量填入了一个setup()中即可。
