from setuptools import setup
setup(
    name="redicrypt",
    version="0.0.3",
    author="Chris Dutra",
    author_email="cdutra@apprenda.com",
    description="Python-based cryptography package for redis.",
    license="MIT",
    keywords="redis data cryptography",
    url="http://github.com/dutronlabs/redicrypt",
    packages=['redicrypt'],
    install_requires=['pycrypto'],
    long_description="This client package provides a means to encrypt/decrypt data being stored into redis.",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)