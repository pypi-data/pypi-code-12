"""
Simple SMTP mail sending.

"""

from distutils.core import setup
import setuptools  # this import is needed so that some options and commands work

setup(
    name='simple-mail',
    version='0.1.5.0',
    author='PrintWithMe',
    author_email='bepetersondev@gmail.com',
    url='https://gitlab.com/bepetersn/simple-mail',
    zip_safe=False,
    description=__doc__,
    packages=[
        'simple_mail'
    ],
    install_requires=[
    ],
)
