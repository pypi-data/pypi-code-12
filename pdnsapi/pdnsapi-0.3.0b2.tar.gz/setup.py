from setuptools import setup

setup(
    name='pdnsapi',
    version='0.3.0b2',
    description='Library for connecting to PowerDNS 4 REST API',
    author='Erik Lundberg',
    author_email='lundbergerik@gmail.com',
    packages=['pdnsapi'],
    include_package_data=True,
    install_requires=['requests'],
    zip_safe=False,
    classifiers=(),
    tests_require=['mock'],
    test_suite='tests.test_pdnsapi'
)
