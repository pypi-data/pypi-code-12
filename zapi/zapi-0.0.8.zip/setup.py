import os
import sys
import re

from codecs import open

from setuptools import setup, find_packages


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

GITHUB_ACCOUNT = "linzhonghong" # your GitHub account name
RELEASE_TAG = "2016-05-10" # the GitHub release tag
NAME = "zapi" # name of your package

with open('zapi/__init__.py', 'r') as fd:
    VERSION = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not VERSION:
    raise RuntimeError('Cannot find version information')

PACKAGES = [NAME] + ["%s.%s" % (NAME, i) for i in find_packages(NAME)]
PACKAGE_DATA = {
    "": ["*.txt", "*.rst"],
}
SHORT_DESCRIPTION = "An easy lightweight web framework by python." # GitHub Short Description
AUTHOR = "Zhonghong Lin"
AUTHOR_EMAIL = "1529909253@qq.com"
MAINTAINER = AUTHOR
MAINTAINER_EMAIL = AUTHOR_EMAIL

PROJECT_NAME = os.path.basename(os.getcwd()) # the project dir is the project name
URL = "https://github.com/{0}/{1}".format(GITHUB_ACCOUNT, PROJECT_NAME)
DOWNLOAD_URL = "https://github.com/{0}/{1}/tarball/{2}".format(
    GITHUB_ACCOUNT, PROJECT_NAME, RELEASE_TAG)

with open("README.rst", "rb") as f:
    README = f.read().decode("utf-8")
with open("HISTORY.rst", "rb") as f:
    HISTORY = f.read().decode("utf-8")
LONG_DESCRIPTION = README + '\n\n' + HISTORY


LICENSE = "MIT"

PLATFORMS = ["Windows", "Unix"]
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: Unix",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 2 :: Only",
]

with open("requirements.txt", "rb") as f:
    REQUIRES = [i.strip() for i in f.read().decode("utf-8").split("\n")]

setup(
    name=NAME,
    packages=PACKAGES,
    include_package_data = True,
    package_data  = PACKAGE_DATA,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer=MAINTAINER,
    maintainer_email=MAINTAINER_EMAIL,
    url=URL,
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    download_url=DOWNLOAD_URL,
    classifiers=CLASSIFIERS,
    platforms=PLATFORMS,
    license=LICENSE,
    install_requires=REQUIRES,
)


