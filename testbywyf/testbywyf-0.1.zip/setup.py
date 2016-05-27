#!/usr/local/bin/python
# -*- coding:utf-8 -*-


import codecs
import os
import sys
 
try:
    from setuptools import setup  #打包的用的setup必须引入    
except:
    from distutils.core import setup

 
def read(fname):
    """
    定义一个read方法，用来读取目录下的长描述
    我们一般是将README文件中的内容读取出来作为长描述，这个会在PyPI中你这个包的页面上展现出来，
    你也可以不用这个方法，自己手动写内容即可，
    PyPI上支持.rst格式的文件。暂不支持.md格式的文件，<BR>.rst文件PyPI会自动把它转为HTML形式显示在你包的信息页面上。
    """
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()
  
setup(
    name = "testbywyf", #包的名字
    packages = ["testbywyf"], #包含的包，可以多个，这是一个列表
    version = "0.1", #当前包的版本，这个按你自己需要的版本控制方式来

    keywords = "test python package", #关于当前包的一些关键字，方便PyPI进行分类。
    author = "Weber Juche", # 包的作者
    author_email = "weber.juche@gmail.com", #作者的邮件地址
    url = "http://pwd0.com/",  #这个包的项目地址
    license = "MIT", #授权方式,

    #zip_safe=True,
    zip_safe = False,


    description = "this is a test package for packing python liberaries tutorial.", #关于这个包的描述
    long_description = "Public Funcs", #read("README.rst"), #参见read方法说明
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    include_package_data=True,    
)
 
## 把上面的变量填入了一个setup()中即可。

# from setuptools import setup, find_packages

# setup(
#     name = "test",
#     packages = ['test'], # this must be the same as the name above
#     version = "0.1",    
#     zip_safe = False,

#     description = "test",
#     long_description = "Public Funcs",
#     author = "Weber Juche",
#     author_email = "weber.juche@gmail.com",

#     license = "MIT",
#     keywords = ["test", "egg"],
#     classifiers = [],
#     platforms = "Independant",
#     url = "http://pwd0.com/",
    
# )