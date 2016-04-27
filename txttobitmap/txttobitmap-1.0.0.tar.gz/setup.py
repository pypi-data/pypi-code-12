from setuptools import setup
from codecs import open
from os import path

base_path = path.abspath(path.dirname(__file__))

with open(path.join(base_path, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='txttobitmap',
    version='1.0.0',
    description='Simple script that converts given file (text file or'
                'essentially whatever) to a bitmap',
    long_description=long_description,
    url='https://github.com/m4tx/txttobitmap',

    author='Mateusz Maćkowski',
    author_email='m4tx@m4tx.pl',
    license='MIT',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities'
    ],

    keywords='txt bitmap conversion',
    py_modules=['txttobitmap'],
    install_requires=['Pillow>=3.0.0,<4'],
    entry_points={
        'console_scripts': [
            'txttobitmap=txttobitmap:main',
        ],
    },
)
