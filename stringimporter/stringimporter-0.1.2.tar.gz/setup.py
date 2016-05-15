try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Arbitrary import Python source as a Python module',
    'author': 'Feth Arezki',
    'url': 'https://github.com/majerteam/stringimporter',
    'download_url': 'https://github.com/majerteam/stringimporter',
    'author_email': 'tech@majerti.fr',
    'version': '0.1.2',
    'packages': ['stringimporter'],
    'setup_requires': ['pytest-runner'],
    'tests_require': ['pytest'],
    'name': 'stringimporter'
}

setup(**config)
