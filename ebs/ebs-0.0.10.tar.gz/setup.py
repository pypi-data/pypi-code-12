from setuptools import setup
from ebs.version import __version__

setup(
    name = "ebs",
    packages = ["ebs"],
    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.sh', '*.md'],
    },
    version = __version__,
    description = "Various utils I use in more than one script/lib",
    author = "Endre Bakken Stovner",
    author_email = "endrebak@stud.ntnu.no",
    url = "http://github.com/endrebak/ebs",
    keywords = ["Helper functions"],
    license = ["GPL-3.0"],
    install_requires = ["pandas"],
    classifiers = [
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Topic :: Scientific/Engineering"],
    long_description = ("See the url for more info.")
)
