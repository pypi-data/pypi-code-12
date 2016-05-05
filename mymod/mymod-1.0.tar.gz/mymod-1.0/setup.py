from distutils.core import setup
PACKAGE = "mymod"
NAME = "mymod"
DESCRIPTION = "my mod01"
AUTHOR = "zx2"
AUTHOR_EMAIL = "zx@qq.com"
URL = "www.zx.com"
VERSION = "1.0" 

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description="hahahahahaha",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="BSD",
    url=URL,
    packages=[],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ],
    zip_safe=False,
)
