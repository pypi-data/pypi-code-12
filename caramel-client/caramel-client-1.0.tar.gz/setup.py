from setuptools import setup, find_packages



setup(
    name="caramel-client",
    version="1.0",
    description="caramel-client",
    packages=find_packages(),
    scripts=['caramel-client'],
    classifiers=[
        "Programming Language :: Python",
    ],
    author="D.S. Ljungmark",
    author_email="spider@modio.se",
    url="https://github.com/ModioAB/caramel-client",
    keywords="caramel ssl tls certificates x509 ca cert",
    include_package_data=True,
    zip_safe=True,
)
