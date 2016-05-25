import os

from setuptools import setup

if __name__ == "__main__":
    if os.getenv("I_AM_MAKING_THIS_PACKAGE"):
        setup(
            name="crytography",
            description='I think you meant "cryptography"',
            license="MIT",
            version="1.0.0",
            author="cyli",
            author_email="cyli@twistedmatrix.com",
            maintainer="cyli",
            maintainer_email="cyli@twistedmatrix.com",
            long_description='I really think you meant "cryptography"',
            packages=[],
        )
    else:
        raise Exception('I think you meant "cryptography"')
