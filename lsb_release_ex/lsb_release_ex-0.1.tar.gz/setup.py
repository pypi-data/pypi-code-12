try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from lsb_release_ex import (
    __version__, __doc__, __author__, __email__, __license__)

setup(
    name="lsb_release_ex",
    version=__version__,
    description="Ehanced Linux Standard Base version reporting module",
    long_description=__doc__,
    author=__author__,
    author_email=__email__,
    license=__license__,
    url="https://github.com/likema/lsb_release_ex",
    download_url="https://github.com/likema/lsb_release_ex/archive/master.zip",
    py_modules=["lsb_release_ex"],
    classifiers=[
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)"])
# vim: ts=4 sw=4 et:
