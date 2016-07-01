from setuptools import setup, find_packages
from npm_helper import __version__

setup(
    name='npm_helper',
    version=__version__,
    keywords=('npm', 'search', 'github', 'spider'),
    description='npm website search is sooo silly and inconvenience. That\'s why this plugin born',
    author='ecmadao',
    author_email='wlec@outlook.com',
    url='https://github.com/ecmadao/npm-helper',
    packages=find_packages(),
    py_modules=['run'],
    include_package_data=True,
    platforms='any',
    install_requires=[
        'prettytable',
        'bs4',
        'spider_threads'
    ],
    entry_points={
        'console_scripts': ['pnpm=run:get_keywords']
    },
    license='MIT',
    zip_safe=False,
    classifiers=[
         'Environment :: Console',
         'Programming Language :: Python',
         'Programming Language :: Python :: 3.5',
         'Programming Language :: Python :: Implementation :: CPython'
    ]
)
