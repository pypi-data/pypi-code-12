from setuptools import setup, find_packages

setup(
    name                 = 'zoid',
    description          = 'Commandline tool for easy hosting of project zomboid servers',
    version              = '0.1.1',
    author               = 'David Ewelt',
    author_email         = 'uranoxyd@gmail.com',
    url                  = 'https://bitbucket.org/uranoxyd/zoid/',
    license              = 'BSD',
    scripts              = ['scripts/zoidcmd.py'],
    packages             = find_packages(),
    include_package_data = True,
    zip_safe             = False,

    install_requires = [
        'uconfig>=0.1.0',
    ],
    dependency_links = [
        'https://pypi.python.org/pypi/uconfig',
    ],

    classifiers = [
        'Development Status :: 3 - Alpha',

        'Intended Audience :: End Users/Desktop',
        'Topic :: Games/Entertainment',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],

)