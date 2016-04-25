import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), "README.rst")).read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="le-client",
    version="0.1",
    packages=["le_client"],
    include_package_data=True,
    license="GNU GPLv3+",
    description="Yet another simple Let's Encrypt/ACME client",
    long_description=README,
    maintainer="Aleksey Zhukov",
    maintainer_email="drdaeman@drdaeman.pp.ru",
    url="https://github.com/drdaeman/le-client",
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Security",
        "Topic :: Security :: Cryptography",
    ],
    entry_points={
        "console_scripts": [
            "le_client = le_client.__main__:run"
        ]
    }
)
