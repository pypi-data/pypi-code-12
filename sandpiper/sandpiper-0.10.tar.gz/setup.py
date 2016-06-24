try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(
    name         = 'sandpiper',
    version      = '0.10',
    description  = 'A Generic/Extendible Key-value Store Interface Library',
    license      = 'MIT',
    author       = 'Juti Noppornpitak',
    author_email = 'juti_n@yahoo.co.jp',
    url          = 'https://github.com/shiroyuki/sandpiper',
    packages     = [
        'sandpiper',
        'sandpiper.adapter',
    ],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries'
    ]
)
