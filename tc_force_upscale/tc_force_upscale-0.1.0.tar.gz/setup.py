# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='tc_force_upscale',
    version='0.1.0',
    url='http://github.com/vvarp/tc_force_upscale',
    license='MIT',
    author='Maciek Szczesniak',
    author_email='vvarp@me.com',
    description='Thumbor filter',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'thumbor>=5.0.6',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
