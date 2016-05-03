# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


REQUIRES = (
    "pysolr==3.4.0",
    "pymongo==2.9",
    "mongoengine==0.10.1",
    "marshmallow==2.6.0",
    "marshmallow-mongoengine==0.7.0",
    "Flask==0.10.1",
    "autobahn-sync",
    "umongo",
    "pyJWT",
    "passlib",
    "klein"
)


def read(fname):
    with open(fname) as fp:
        content = fp.read()
    return content


setup(
    name='xin-back',
    version='0.4.1',
    # description='',
    long_description=read('README.rst'),
    author='Scille',
    author_email='contact@scille.fr',
    url='https://github.com/Scille/xin-back',
    packages=find_packages(exclude=("test*", )),
    package_dir={'xin': 'xin'},
    include_package_data=True,
    install_requires=REQUIRES,
    license='MIT',
    zip_safe=False,
    # keywords='',
    classifiers=[
        'Intended Audience :: Developers',
        # 'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ],
    test_suite='tests',
)
