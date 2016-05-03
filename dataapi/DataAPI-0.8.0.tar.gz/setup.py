from setuptools import setup
import io
import sys


if sys.version_info > (3, 0, 0):
    requirements = "requirements/py3.txt"
else:
    requirements = "requirements/py2.txt"

PACKAGE = ["DataAPI", "DataAPI.tests"]
NAME = "DataAPI"
VERSION = '0.8.0'
DESCRIPTION = "DataAPI " + VERSION
AUTHOR = "Dongxing Securities Co., Ltd."
AUTHOR_EMAIL = "licheng@dxzq.net.cn"

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    packages=PACKAGE,
    py_modules=['DataAPI.__init__'],
    install_requires=io.open(requirements, encoding='utf8').read(),
    author_email=AUTHOR_EMAIL,
    url=""
)
