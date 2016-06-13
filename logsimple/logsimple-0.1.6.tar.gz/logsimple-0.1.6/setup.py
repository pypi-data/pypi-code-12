from setuptools import setup, find_packages


###################################################################

NAME = "logsimple"
PACKAGES = find_packages(where="logsimple")
KEYWORDS = ["logs", "print", "color"]
CLASSIFIERS = [
    "Intended Audience :: Developers",
    "Natural Language :: English",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Topic :: Software Development :: Libraries :: Python Modules",
]
INSTALL_REQUIRES = []

###################################################################

if __name__ == "__main__":
    setup(
        name=NAME,
        description="simple logging for python",
        license="MIT License",
        version="0.1.6",
        author="Jeremy Hintz",
        author_email="jeremy.hintz@gmail.com",
        maintainer="Jeremy Hintz",
        maintainer_email="jeremy.hintz@gmail.com",
        keywords=KEYWORDS,
        packages=PACKAGES,
        package_dir={"": "logsimple"},
    )