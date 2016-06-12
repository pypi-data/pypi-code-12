from distutils.core import setup
import os

setup (
    name = "today",
    version = "0.2",
    author = "chenminhua",
    author_email = "chenmh@shanghaitech.edu.cn",
    license = "GPL3",
    description = "don't forget an important day",
    url = "https://github.com/chenminhua/today",
    packages = [

    ],
    scripts = ['bin/today'],
    install_requires = [
        'prettytable >= 0.7'
    ]
)
