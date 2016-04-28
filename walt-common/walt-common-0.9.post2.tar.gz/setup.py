from setuptools import setup, find_packages
import sys

if not sys.version_info[0] == 2:
    sys.exit("Sorry, Python 3 is not supported (yet)")

setup(
    name = "walt-common",
    version = "0.9-2",
    packages = find_packages(),
    install_requires = ['rpyc>=3.3','plumbum>=1.4.2'],

    # metadata for upload to PyPI
    author = "Etienne Duble",
    author_email = "etienne.duble@imag.fr",
    description = "WalT (Wireless Testbed) common python modules.",
    license = "LGPL",
    keywords = "WalT wireless testbed",
    url = "http://walt.forge.imag.fr/",

    namespace_packages = ['walt'],
)

