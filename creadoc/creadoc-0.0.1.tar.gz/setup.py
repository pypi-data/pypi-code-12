# coding: utf-8
from setuptools import setup, find_packages

__author__ = 'damirazo <me@damirazo.ru>'


setup(
    name='creadoc',
    version='0.0.1',
    description=u'Дизайнер отчетов на основе Stimulsoft Report Js',
    url='https://github.com/damirazo/creadoc',
    author='damirazo',
    author_email='me@damirazo.ru',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: General',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Russian',
        'Programming Language :: Python :: 2.7',
    ],
    packages=find_packages(),
    include_package_data=True,
)
