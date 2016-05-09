from setuptools import setup, find_packages

description = """
This is our command line client for Caramel. It generates keys, requests and
updates the certificates.

It's using the `openssl` command line client in order to reduce the amount of
dependencies.

"""
version = "1.2.3"

setup(
    name="caramel-client",
    version=version,
    description="caramel-client: A python client for the Caramel CA system.",
    packages=find_packages(),
    scripts=['caramel-client'],
    long_description=description,
    classifiers=[
        "Programming Language :: Python",
    ],
    author="D.S. Ljungmark",
    author_email="spider@modio.se",
    url="https://github.com/ModioAB/caramel-client",
    download_url="https://github.com/ModioAB/caramel-client/releases/tag/%s" % version,  # noqa
    keywords="caramel ssl tls certificates x509 ca cert",
    include_package_data=True,
    zip_safe=True,
    install_requires=['requests'],
)
