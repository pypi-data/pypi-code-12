from setuptools import setup, find_packages
from alfred_npm_helper import __version__

setup(
    name='alfred_npm_helper',
    version=__version__,
    keywords=('npm', 'search', 'github', 'spider', 'alfred'),
    description='npm website search is sooo silly and inconvenience. That\'s why this plugin born',
    author='ecmadao',
    author_email='wlec@outlook.com',
    url='https://github.com/ecmadao/alfred-npm-helper',
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    install_requires=[
        'bs4',
        'spider_threads'
    ],
    license='MIT',
    zip_safe=False,
    classifiers=[
         'Environment :: Console',
         'Programming Language :: Python',
         'Programming Language :: Python :: 3.5',
         'Programming Language :: Python :: Implementation :: CPython'
    ]
)
