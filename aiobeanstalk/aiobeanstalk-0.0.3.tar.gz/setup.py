from setuptools import setup, find_packages

PACKAGE_NAME = 'aiobeanstalk'
PACKAGE_VERSION = '0.0.3'

if __name__ == '__main__':
    setup(
        name=PACKAGE_NAME,
        version=PACKAGE_VERSION,
        description="asyncio based beanstalk client",
        author="jonson",
        url="https://github.com/jonson/aiobeanstalk",
        packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
        install_requires=[
            "pyyaml>=3.11",
        ],
        classifiers=[
            "Programming Language :: Python :: 3.5",
        ],
    )
