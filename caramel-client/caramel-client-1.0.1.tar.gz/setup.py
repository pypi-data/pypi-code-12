from setuptools import setup, find_packages


version = "1.0.1"

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
    url="https://github.com/ModioAB/caramel-client",
    download_url = 'https://github.com/ModioAB/caramel-client/tarball/%s' % version,
    keywords="caramel ssl tls certificates x509 ca cert",
    include_package_data=True,
    zip_safe=True,
)
