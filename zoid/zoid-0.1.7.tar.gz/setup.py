from setuptools import setup, find_packages

setup(
    name                 = 'zoid',
    description          = 'Commandline tool for easy hosting of project zomboid servers',
    version              = '0.1.7',
    author               = 'David Ewelt',
    author_email         = 'uranoxyd@gmail.com',
    url                  = 'https://bitbucket.org/uranoxyd/zoid/',
    license              = 'BSD',
    scripts              = [
        'scripts/zoid-create.py',
        'scripts/zoid-init.py',
        'scripts/zoid-kill.py',
        'scripts/zoid-ls.py',
        'scripts/zoid-restart.py',
        'scripts/zoid-start.py',
        'scripts/zoid-stop.py',
    ],
    packages             = find_packages(),
    include_package_data = True,
    zip_safe             = False,

    install_requires = [
        'uconfig>=0.1.1',
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