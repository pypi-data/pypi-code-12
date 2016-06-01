from setuptools import setup

setup(
    version="0.7",
    author="Chris Mutel",
    author_email="cmutel@gmail.com",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
    package_data={'pandarus': [
        "tests/data/*.gpkg",
        "tests/data/*.tif",
    ]},
    entry_points = {
        'console_scripts': [
            'pandarus = pandarus.cli:main',
        ]
    },
    install_requires=[
        "docopt",
        "eight",
        "fiona",
        "GDAL",
        "psutil",
        "pyprind",
        "pyproj",
        "Rtree",
        "shapely",
    ],
    license=open('LICENSE.txt').read(),
    long_description=open('README.rst').read(),
    name='pandarus',
    packages=["pandarus", "pandarus.tests", "pandarus.export"],
    url="https://bitbucket.org/cmutel/pandarus",
)
