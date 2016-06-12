#!/usr/bin/env python
#encoding=utf-8

import sys
from os.path import join, dirname
sys.path.append(join(dirname(__file__), 'src'))
from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup
execfile(join(dirname(__file__), 'src', 'QTLibrary', 'version.py'))

DESCRIPTION = """
QTLibrary是一个个人学习研究时做的测试库，参考了一下Selenium2Library的一些写法.
其中做了几个比较常用的关键字，比如随机生成生日，随机生成身份证号，随机生成中文姓名等。
安装方法：
pip install robotframework-qtlibrary

"""[1:-1]

setup(name         = 'robotframework-qtlibrary',
      version      = VERSION,
      description  = 'QTLibrary for Robot Framework',
      long_description = DESCRIPTION,
      author       = 'Qitao',
      author_email = 'Qitaos@gmail.com',
      url          = 'https://github.com/qitaos/Robotframework-QTLibrary',
      license      = 'No License',
      platforms    = 'any',
      classifiers  = [
                        "Development Status :: 5 - Production/Stable",
                        "License :: OSI Approved :: Apache Software License",
                        "Operating System :: OS Independent",
                        "Programming Language :: Python",
                        "Topic :: Software Development :: Testing"
                     ],
      install_requires = [
							
						 ],
      py_modules=['ez_setup'],
      package_dir  = {'' : 'src'},
      packages     = ['QTLibrary','QTLibrary.keywords'],
      include_package_data = True,
      )

