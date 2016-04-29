# -*- coding: utf-8 -*-
from setuptools import setup
setup (
    name='denden_extension',
    version='1.0.0',
    description='Python-Markdown extention for Den-Den Markdown',
    url='https://github.com/muranamihdk/denden_extension',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: Japanese',
        'Topic :: Text Processing :: Filters',
        'Topic :: Text Processing :: Markup',
        'Topic :: Text Processing :: Markup :: HTML',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='markdown denden-markdown でんでんマークダウン Japanese epub ruby',
    py_modules=['denden_extension'],
    install_requires=['markdown>=2.6'],
)

