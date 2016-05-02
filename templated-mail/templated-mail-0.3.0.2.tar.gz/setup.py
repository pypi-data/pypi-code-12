"""
Package that allows defining an email subject, 
plain text, & html in a template, thus keeping it 
separate from application logic, and providing a 
consistent way to interpolate data into it. 

"""

from distutils.core import setup
import setuptools  # this import is needed so that some options and commands work

setup(
    name='templated-mail',
    version='0.3.0.2',
    author='Brian E. Peterson',
    author_email='bepetersondev@gmail.com',
    url='https://github.com/bepetersn/templated-mail',
    zip_safe=False,
    description=__doc__,
    packages=[
        'templated_mail'
    ],
    install_requires=[
        'simple_mail==0.1.5.0',
        'mock',
        'bunch',
        'jinja2',
        'simple_configparser'
    ],
)
