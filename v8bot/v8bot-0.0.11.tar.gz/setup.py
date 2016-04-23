from setuptools import setup, find_packages

setup(
    name = 'v8bot',
    description = 'write bots for Hitbox.tv in JavaScript',
    version = '0.0.11',
    author = 'David Ewelt',
    author_email = 'uranoxyd@gmail.com',
    url = 'https://bitbucket.org/uranoxyd/v8bot',
    license = 'BSD',
    packages = find_packages(),
    zip_safe = False,

    scripts = ['scripts/v8b.py'],

    install_requires = [
        'hitboxy[chatclient]>=0.1.21',
    ],
    dependency_links = [
        'https://pypi.python.org/pypi/hitboxy',
    ],

    classifiers = [
        'Development Status :: 3 - Alpha',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
)