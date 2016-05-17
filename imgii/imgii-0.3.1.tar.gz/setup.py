#!/usr/bin/env python3


from setuptools import setup


setup(
    name='imgii',
    packages=['imgii'],
    version='0.3.1',
    description='Very simple conversion of images to text.',
    url='https://github.com/spurll/imgii',
    download_url='https://github.com/spurll/imgii/tarball/0.3.1',
    author='Gem Newman',
    author_email='spurll@gmail.com',
    license='MPL2',
    install_requires=['requests', 'pillow', 'colorama'],
    entry_points = {'console_scripts': ['imgii = imgii:main']},
    keywords=['ascii', 'image'],
    classifiers=[
        'Topic :: Scientific/Engineering :: Image Recognition',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',
        'Programming Language :: Python',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)'
    ],
)
