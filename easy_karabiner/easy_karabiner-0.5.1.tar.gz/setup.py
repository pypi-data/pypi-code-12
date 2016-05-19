from setuptools import setup, find_packages
from easy_karabiner import __version__

setup(
    name='easy_karabiner',
    version=__version__,
    description='A tool to simplify key-remapping configuration for Karabiner',
    author='loggerhead',
    author_email='i@loggerhead.me',
    url='https://github.com/loggerhead/Easy-Karabiner',
    keywords=('Karabiner', 'configer', 'remap', 'key'),
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=[
        'lxml >= 3.0.0, < 4.0.0',
        'click >= 6.0.0, < 7.0.0',
    ],
    entry_points='''
        [console_scripts]
        easy_karabiner=easy_karabiner.main:main
    ''',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Operating System :: MacOS',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities',
    ]
)
