import os
from setuptools import setup,find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__),fname)).read()

setup(
    name='awstorrent',
    version='0.0.1',
    author='Cheng Yan',
    author_email='firearasi@qq.com',
    description='A simple bittorent tool with aws',
    license='GPL',
    packages=find_packages(),
    install_requires=['pyperclip']
)
    
