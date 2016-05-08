import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

version = "1.1.2"

setup(
    name="caramel-client",
    version=version,
    description="caramel-client",
    packages=find_packages(),
    scripts=['caramel-client'],
    classifiers=[
        "Programming Language :: Python",
    ],
    author="D.S. Ljungmark",
    author_email="spider@modio.se",
    url="https://github.com/MyTemp/caramel-client",
    download_url="https://github.com/ModioAB/caramel-client/releases/tag/%s" % version,
    keywords="caramel ssl tls certificates x509 ca cert",
    include_package_data=True,
    zip_safe=True,
    install_requires=['requests'],
)
