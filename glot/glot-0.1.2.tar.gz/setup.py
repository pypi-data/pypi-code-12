from setuptools import setup

setup(
    name='glot',
    version='0.1.2',
    packages=['glot'],
    package_dir={'glot': 'src/glot'},

    description='CLI manager for Glossia (https://go-smart.github.io/glossia)',
    author='NUMA Engineering Services Ltd.',
    author_email='phil.weir@numa.ie',
    url='http://gosmart-project.eu/',

    scripts=[
        'scripts/glot',
    ],

    install_requires=[
        'aiohttp',
        'txaio',
        'Click',
        'gitpython',
        'tabulate',
        'colorama',
        'autobahn'
    ]
)
