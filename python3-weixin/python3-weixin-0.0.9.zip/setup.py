#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name="python3-weixin",
      version="0.0.9",
      description="Weixin API client for Python 3.x",
      license="BSD",
      install_requires=["simplejson", "requests", "six", "chardet"],
      author="Yang Kai",
      author_email="yk1001@live.cn",
      url="https://github.com/ykbj/python3-weixin",
      download_url="https://github.com/ykbj/python3-weixin/archive/master.zip",
      packages=find_packages(),
      keywords=["python3-weixin", "weixin", "wechat", "sdk"],
      zip_safe=True)
