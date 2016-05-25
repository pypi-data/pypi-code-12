from setuptools import setup

# Thanks to http://peterdowns.com/posts/first-time-with-pypi.html
pkg_version = '0.2'
setup(
    name='tofab',
    packages=['tofab'],
    version=pkg_version,
    description=r'''Fabric utils, intend to use with Tokit.''',
    author='Giang Manh',
    author_email='manhgd@yahoo.com',
    url='https://github.com/manhgd/tofab',
    download_url='https://github.com/manhgd/tofab/tarball/' + pkg_version,
    keywords=['fabric', 'tokit', 'tornado'],
    classifiers=[
        'Programming Language :: Python :: 2.7',
        ],
    install_requires=[
        'fabric',
        'sphinx'
    ]
)
