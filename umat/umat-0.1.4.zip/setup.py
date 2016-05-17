from os.path import (
    dirname,
    join
)
from setuptools import (
    find_packages,
    setup
)


PACKAGE = 'umat'
README = 'README.rst'
DESCRIPTION = 'Unofficial SDK for MobileAppTracking Service APIs'
LONG_DESCRIPTION = open(join(dirname(__file__), README)).read()
VERSION = __import__(PACKAGE).__version__
URL = 'https://github.com/AntonSever/umat'


kwargs = {
    'author': 'Anton Sever',
    'author_email': 'anton.sever@playrix.com',
    'description': DESCRIPTION,
    'install_requires': ['pandas'],
    'license': 'MIT',
    'long_description': LONG_DESCRIPTION,
    'name': PACKAGE,
    'packages': find_packages(),
    'readme': README,
    'url': URL,
    'version': VERSION,
}
setup(**kwargs)
